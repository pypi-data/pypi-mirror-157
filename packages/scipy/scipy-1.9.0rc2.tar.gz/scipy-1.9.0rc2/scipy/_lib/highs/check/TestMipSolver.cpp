#include "Highs.h"
#include "SpecialLps.h"
#include "catch.hpp"

const bool dev_run = false;
const double double_equal_tolerance = 1e-5;

void solve(Highs& highs, std::string presolve,
           const HighsModelStatus require_model_status,
           const double require_optimal_objective = 0,
           const double require_iteration_count = -1);
void distillationMIP(Highs& highs);
void rowlessMIP(Highs& highs);

TEST_CASE("MIP-distillation", "[highs_test_mip_solver]") {
  Highs highs;
  if (!dev_run) highs.setOptionValue("output_flag", false);
  distillationMIP(highs);
}

TEST_CASE("MIP-rowless", "[highs_test_mip_solver]") {
  Highs highs;
  if (!dev_run) highs.setOptionValue("output_flag", false);
  rowlessMIP(highs);
}

TEST_CASE("MIP-integrality", "[highs_test_mip_solver]") {
  std::string filename;
  filename = std::string(HIGHS_DIR) + "/check/instances/avgas.mps";

  Highs highs;
  highs.readModel(filename);
  if (!dev_run) highs.setOptionValue("output_flag", false);
  highs.run();
  highs.readModel(filename);
  const HighsLp& lp = highs.getLp();
  const HighsInfo& info = highs.getInfo();
  vector<HighsVarType> integrality;
  integrality.resize(lp.num_col_);
  HighsInt from_col0 = 0;
  HighsInt to_col0 = 2;
  HighsInt from_col1 = 5;
  HighsInt to_col1 = 7;
  HighsInt num_set_entries = 6;
  vector<HighsInt> set;
  set.push_back(0);
  set.push_back(7);
  set.push_back(1);
  set.push_back(5);
  set.push_back(2);
  set.push_back(6);
  vector<HighsInt> mask;
  mask.assign(lp.num_col_, 0);
  for (HighsInt ix = 0; ix < num_set_entries; ix++) {
    HighsInt iCol = set[ix];
    mask[iCol] = 1;
    integrality[ix] = HighsVarType::kInteger;
  }
  REQUIRE(highs.changeColsIntegrality(from_col0, to_col0, &integrality[0]) ==
          HighsStatus::kOk);
  REQUIRE(highs.changeColsIntegrality(from_col1, to_col1, &integrality[0]) ==
          HighsStatus::kOk);
  if (dev_run) {
    highs.setOptionValue("log_dev_level", 3);
  } else {
    highs.setOptionValue("output_flag", false);
  }
  if (dev_run) highs.writeModel("");
  highs.run();
  if (dev_run) highs.writeSolution("", kSolutionStylePretty);
  double optimal_objective = info.objective_function_value;
  if (dev_run) printf("Objective = %g\n", optimal_objective);

  highs.clearModel();
  if (!dev_run) highs.setOptionValue("output_flag", false);
  highs.readModel(filename);
  REQUIRE(highs.changeColsIntegrality(num_set_entries, &set[0],
                                      &integrality[0]) == HighsStatus::kOk);
  if (dev_run) highs.writeModel("");
  highs.run();
  if (dev_run) highs.writeSolution("", kSolutionStylePretty);
  REQUIRE(info.objective_function_value == optimal_objective);

  integrality.assign(lp.num_col_, HighsVarType::kContinuous);
  for (HighsInt ix = 0; ix < num_set_entries; ix++) {
    HighsInt iCol = set[ix];
    integrality[iCol] = HighsVarType::kInteger;
  }

  highs.clearModel();
  if (!dev_run) highs.setOptionValue("output_flag", false);
  highs.readModel(filename);
  REQUIRE(highs.changeColsIntegrality(&mask[0], &integrality[0]) ==
          HighsStatus::kOk);
  if (dev_run) highs.writeModel("");
  highs.run();
  if (dev_run) highs.writeSolution("", kSolutionStylePretty);
  if (dev_run) highs.writeSolution("", kSolutionStyleRaw);
  REQUIRE(info.objective_function_value == optimal_objective);

  REQUIRE(info.mip_node_count == 1);
  REQUIRE(info.mip_dual_bound == -6);
  REQUIRE(info.mip_gap == 0);
}

TEST_CASE("MIP-nmck", "[highs_test_mip_solver]") {
  Highs highs;
  if (!dev_run) highs.setOptionValue("output_flag", false);
  HighsLp lp;
  lp.num_col_ = 3;
  lp.num_row_ = 2;
  lp.col_cost_ = {-3, -2, -1};
  lp.col_lower_ = {0, 0, 0};
  lp.col_upper_ = {inf, inf, 1};
  lp.row_lower_ = {-inf, 12};
  lp.row_upper_ = {7, 12};
  lp.a_matrix_.start_ = {0, 2, 4, 6};
  lp.a_matrix_.index_ = {0, 1, 0, 1, 0, 1};
  lp.a_matrix_.value_ = {1, 4, 1, 2, 1, 1};
  lp.integrality_ = {HighsVarType::kContinuous, HighsVarType::kContinuous,
                     HighsVarType::kInteger};
  REQUIRE(highs.passModel(lp) == HighsStatus::kOk);
  highs.setOptionValue("highs_debug_level", kHighsDebugLevelCheap);
  highs.setOptionValue("log_dev_level", 2);
  HighsStatus return_status = highs.run();
  REQUIRE(return_status == HighsStatus::kOk);
  if (dev_run) highs.writeInfo("");
  const HighsInfo& info = highs.getInfo();
  REQUIRE(info.num_primal_infeasibilities == 0);
  REQUIRE(info.max_primal_infeasibility == 0);
  REQUIRE(info.sum_primal_infeasibilities == 0);
}

TEST_CASE("MIP-od", "[highs_test_mip_solver]") {
  Highs highs;
  if (!dev_run) highs.setOptionValue("output_flag", false);
  HighsLp lp;
  lp.num_col_ = 1;
  lp.num_row_ = 0;
  lp.col_cost_ = {-2};
  lp.col_lower_ = {-inf};
  lp.col_upper_ = {1.5};
  lp.integrality_ = {HighsVarType::kInteger};
  double required_objective_value = -2;
  double required_x0_value = 1;

  const HighsInfo& info = highs.getInfo();
  const HighsSolution& solution = highs.getSolution();

  HighsStatus return_status = highs.passModel(lp);
  REQUIRE(return_status == HighsStatus::kOk);

  if (dev_run) {
    printf("One variable unconstrained MIP: model\n");
    highs.writeModel("");
  }

  return_status = highs.run();
  REQUIRE(return_status == HighsStatus::kOk);

  const HighsInt style = kSolutionStylePretty;
  if (dev_run) {
    printf("One variable unconstrained MIP: solution\n");
    highs.writeSolution("", style);
  }

  HighsModelStatus model_status = highs.getModelStatus();

  REQUIRE(model_status == HighsModelStatus::kOptimal);
  REQUIRE(fabs(info.objective_function_value - required_objective_value) <
          double_equal_tolerance);
  REQUIRE(fabs(solution.col_value[0] - required_x0_value) <
          double_equal_tolerance);

  highs.changeColBounds(0, -2, 2);

  if (dev_run) {
    printf("After changing bounds: model\n");
    highs.writeModel("");
  }

  return_status = highs.run();
  REQUIRE(return_status == HighsStatus::kOk);

  model_status = highs.getModelStatus();

  if (dev_run) {
    printf("After changing bounds: solution\n");
    highs.writeSolution("", style);
  }

  required_objective_value = -4;
  required_x0_value = 2;
  REQUIRE(model_status == HighsModelStatus::kOptimal);
  REQUIRE(fabs(info.objective_function_value - required_objective_value) <
          double_equal_tolerance);
  REQUIRE(fabs(solution.col_value[0] - required_x0_value) <
          double_equal_tolerance);
}

bool objectiveOk(const double optimal_objective,
                 const double require_optimal_objective,
                 const bool dev_run = false) {
  double error = std::fabs(optimal_objective - require_optimal_objective) /
                 std::max(1.0, std::fabs(require_optimal_objective));
  bool error_ok = error < 1e-10;
  if (!error_ok && dev_run)
    printf("Objective is %g but require %g (error %g)\n", optimal_objective,
           require_optimal_objective, error);
  return error_ok;
}

void solve(Highs& highs, std::string presolve,
           const HighsModelStatus require_model_status,
           const double require_optimal_objective,
           const double require_iteration_count) {
  if (!dev_run) highs.setOptionValue("output_flag", false);
  const HighsInfo& info = highs.getInfo();
  REQUIRE(highs.setOptionValue("presolve", presolve) == HighsStatus::kOk);

  REQUIRE(highs.setBasis() == HighsStatus::kOk);

  REQUIRE(highs.run() == HighsStatus::kOk);

  REQUIRE(highs.getModelStatus() == require_model_status);

  if (require_model_status == HighsModelStatus::kOptimal) {
    REQUIRE(objectiveOk(info.objective_function_value,
                        require_optimal_objective, dev_run));
  }
  REQUIRE(highs.resetOptions() == HighsStatus::kOk);
}

void distillationMIP(Highs& highs) {
  SpecialLps special_lps;
  HighsLp lp;
  HighsModelStatus require_model_status;
  double optimal_objective;
  special_lps.distillationMip(lp, require_model_status, optimal_objective);
  REQUIRE(highs.passModel(lp) == HighsStatus::kOk);
  // Presolve doesn't reduce the LP
  solve(highs, "on", require_model_status, optimal_objective);
}

void rowlessMIP(Highs& highs) {
  HighsLp lp;
  HighsModelStatus require_model_status;
  double optimal_objective;
  lp.num_col_ = 2;
  lp.num_row_ = 0;
  lp.col_cost_ = {1, -1};
  lp.col_lower_ = {0, 0};
  lp.col_upper_ = {1, 1};
  lp.a_matrix_.start_ = {0, 0, 0};
  lp.a_matrix_.format_ = MatrixFormat::kColwise;
  lp.sense_ = ObjSense::kMinimize;
  lp.offset_ = 0;
  lp.integrality_ = {HighsVarType::kInteger, HighsVarType::kInteger};
  require_model_status = HighsModelStatus::kOptimal;
  optimal_objective = -1.0;
  REQUIRE(highs.passModel(lp) == HighsStatus::kOk);
  // Presolve reduces the LP to empty
  solve(highs, "on", require_model_status, optimal_objective);
  solve(highs, "off", require_model_status, optimal_objective);
}
