/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                                                       */
/*    This file is part of the HiGHS linear optimization suite           */
/*                                                                       */
/*    Written and engineered 2008-2021 at the University of Edinburgh    */
/*                                                                       */
/*    Available as open-source under the MIT License                     */
/*                                                                       */
/*    Authors: Julian Hall, Ivet Galabova, Qi Huangfu, Leona Gottwald    */
/*    and Michael Feldmeier                                              */
/*                                                                       */
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
#include "mip/HighsLpRelaxation.h"

#include <algorithm>

#include "mip/HighsCutPool.h"
#include "mip/HighsDomain.h"
#include "mip/HighsMipSolver.h"
#include "mip/HighsMipSolverData.h"
#include "mip/HighsPseudocost.h"
#include "util/HighsCDouble.h"
#include "util/HighsHash.h"

void HighsLpRelaxation::LpRow::get(const HighsMipSolver& mipsolver,
                                   HighsInt& len, const HighsInt*& inds,
                                   const double*& vals) const {
  switch (origin) {
    case kCutPool:
      mipsolver.mipdata_->cutpool.getCut(index, len, inds, vals);
      break;
    case kModel:
      mipsolver.mipdata_->getRow(index, len, inds, vals);
  };
}

HighsInt HighsLpRelaxation::LpRow::getRowLen(
    const HighsMipSolver& mipsolver) const {
  switch (origin) {
    case kCutPool:
      return mipsolver.mipdata_->cutpool.getRowLength(index);
    case kModel:
      return mipsolver.mipdata_->ARstart_[index + 1] -
             mipsolver.mipdata_->ARstart_[index];
  };

  assert(false);
  return -1;
}

bool HighsLpRelaxation::LpRow::isIntegral(
    const HighsMipSolver& mipsolver) const {
  switch (origin) {
    case kCutPool:
      return mipsolver.mipdata_->cutpool.cutIsIntegral(index);
    case kModel:
      return mipsolver.mipdata_->rowintegral[index];
  };

  assert(false);
  return false;
}

double HighsLpRelaxation::LpRow::getMaxAbsVal(
    const HighsMipSolver& mipsolver) const {
  switch (origin) {
    case kCutPool:
      return mipsolver.mipdata_->cutpool.getMaxAbsCutCoef(index);
    case kModel:
      return mipsolver.mipdata_->maxAbsRowCoef[index];
  };

  assert(false);
  return 0.0;
}

double HighsLpRelaxation::slackLower(HighsInt row) const {
  switch (lprows[row].origin) {
    case LpRow::kCutPool:
      return mipsolver.mipdata_->domain.getMinCutActivity(
          mipsolver.mipdata_->cutpool, lprows[row].index);
    case LpRow::kModel:
      double rowlower = rowLower(row);
      if (rowlower != -kHighsInf) return rowlower;
      return mipsolver.mipdata_->domain.getMinActivity(lprows[row].index);
  };

  assert(false);
  return -kHighsInf;
}

double HighsLpRelaxation::slackUpper(HighsInt row) const {
  double rowupper = rowUpper(row);
  switch (lprows[row].origin) {
    case LpRow::kCutPool:
      return rowupper;
    case LpRow::kModel:
      if (rowupper != kHighsInf) return rowupper;
      return mipsolver.mipdata_->domain.getMaxActivity(lprows[row].index);
  };

  assert(false);
  return kHighsInf;
}

HighsLpRelaxation::HighsLpRelaxation(const HighsMipSolver& mipsolver)
    : mipsolver(mipsolver) {
  lpsolver.setOptionValue("output_flag", false);
  lpsolver.setOptionValue("random_seed", mipsolver.options_mip_->random_seed);
  lpsolver.setOptionValue("primal_feasibility_tolerance",
                          mipsolver.options_mip_->mip_feasibility_tolerance);
  lpsolver.setOptionValue(
      "dual_feasibility_tolerance",
      mipsolver.options_mip_->mip_feasibility_tolerance * 0.1);
  status = Status::kNotSet;
  numlpiters = 0;
  avgSolveIters = 0;
  numSolved = 0;
  epochs = 0;
  maxNumFractional = 0;
  objective = -kHighsInf;
  currentbasisstored = false;
}

HighsLpRelaxation::HighsLpRelaxation(const HighsLpRelaxation& other)
    : mipsolver(other.mipsolver),
      lprows(other.lprows),
      fractionalints(other.fractionalints),
      objective(other.objective),
      basischeckpoint(other.basischeckpoint),
      currentbasisstored(other.currentbasisstored) {
  lpsolver.setOptionValue("output_flag", false);
  lpsolver.passOptions(other.lpsolver.getOptions());
  lpsolver.passModel(other.lpsolver.getLp());
  lpsolver.setBasis(other.lpsolver.getBasis());
  mask.resize(mipsolver.numCol());
  numlpiters = 0;
  avgSolveIters = 0;
  numSolved = 0;
  epochs = 0;
  maxNumFractional = 0;
  objective = -kHighsInf;
}

void HighsLpRelaxation::loadModel() {
  HighsLp lpmodel = *mipsolver.model_;
  lpmodel.col_lower_ = mipsolver.mipdata_->domain.col_lower_;
  lpmodel.col_upper_ = mipsolver.mipdata_->domain.col_upper_;
  lpmodel.offset_ = 0;
  lprows.clear();
  lprows.reserve(lpmodel.num_row_);
  for (HighsInt i = 0; i != lpmodel.num_row_; ++i)
    lprows.push_back(LpRow::model(i));
  lpmodel.integrality_.clear();
  lpsolver.clearSolver();
  lpsolver.clearModel();
  lpsolver.passModel(std::move(lpmodel));
  mask.resize(lpmodel.num_col_);
}

double HighsLpRelaxation::computeBestEstimate(const HighsPseudocost& ps) const {
  HighsCDouble estimate = objective;

  if (!fractionalints.empty()) {
    // because the pseudocost may be zero, we add an offset to the pseudocost so
    // that we always have some part of the estimate depending on the
    // fractionality.

    HighsCDouble increase = 0.0;
    double offset = mipsolver.mipdata_->feastol *
                    std::max(std::abs(objective), 1.0) /
                    mipsolver.mipdata_->integral_cols.size();

    for (const std::pair<HighsInt, double>& f : fractionalints) {
      increase += std::min(ps.getPseudocostUp(f.first, f.second, offset),
                           ps.getPseudocostDown(f.first, f.second, offset));
    }

    estimate += double(increase);
  }

  return double(estimate);
}

double HighsLpRelaxation::computeLPDegneracy(
    const HighsDomain& localdomain) const {
  if (!lpsolver.getSolution().dual_valid || !lpsolver.getBasis().valid) {
    return 1.0;
  }

  double dualFeasTol = lpsolver.getInfo().max_dual_infeasibility;

  const HighsBasis& basis = lpsolver.getBasis();
  const HighsSolution& sol = lpsolver.getSolution();

  HighsInt numFixedRows = 0;
  HighsInt numInequalities = 0;
  HighsInt numBasicEqualities = 0;

  for (HighsInt i = 0; i < numRows(); ++i) {
    if (lpsolver.getLp().row_lower_[i] != lpsolver.getLp().row_upper_[i]) {
      ++numInequalities;

      if (basis.row_status[i] != HighsBasisStatus::kBasic) {
        if (std::abs(sol.row_dual[i]) > dualFeasTol) ++numFixedRows;
      }
    } else
      numBasicEqualities += basis.row_status[i] == HighsBasisStatus::kBasic;
  }

  HighsInt numAlreadyFixedCols = 0;
  HighsInt numFixedCols = 0;
  for (HighsInt i = 0; i < numCols(); ++i) {
    if (basis.col_status[i] != HighsBasisStatus::kBasic) {
      if (std::abs(sol.col_dual[i]) > dualFeasTol)
        ++numFixedCols;
      else if (localdomain.col_lower_[i] == localdomain.col_upper_[i])
        ++numAlreadyFixedCols;
    }
  }

  HighsInt base = numCols() - numAlreadyFixedCols + numInequalities +
                  numBasicEqualities - numRows();

  double degenerateColumnShare =
      base > 0 ? 1.0 - double(numFixedCols + numFixedRows) / base : 0.0;

  double varConsRatio =
      numRows() > 0
          ? double(numCols() + numInequalities + numBasicEqualities -
                   numFixedCols - numFixedRows - numAlreadyFixedCols) /
                numRows()
          : 1.0;
  double fac1 = degenerateColumnShare < 0.8
                    ? 1.0
                    : std::pow(10.0, 10 * (degenerateColumnShare - 0.7));
  double fac2 = varConsRatio < 2.0 ? 1.0 : 10.0 * varConsRatio;

  return fac1 * fac2;
}

void HighsLpRelaxation::addCuts(HighsCutSet& cutset) {
  HighsInt numcuts = cutset.numCuts();
  assert(lpsolver.getLp().num_row_ ==
         (HighsInt)lpsolver.getLp().row_lower_.size());
  assert(lpsolver.getLp().num_row_ == (HighsInt)lprows.size());
  if (numcuts > 0) {
    status = Status::kNotSet;
    currentbasisstored = false;
    basischeckpoint.reset();

    lprows.reserve(lprows.size() + numcuts);
    for (HighsInt i = 0; i != numcuts; ++i)
      lprows.push_back(LpRow::cut(cutset.cutindices[i]));

    bool success =
        lpsolver.addRows(numcuts, cutset.lower_.data(), cutset.upper_.data(),
                         cutset.ARvalue_.size(), cutset.ARstart_.data(),
                         cutset.ARindex_.data(),
                         cutset.ARvalue_.data()) == HighsStatus::kOk;
    assert(success);
    (void)success;
    assert(lpsolver.getLp().num_row_ ==
           (HighsInt)lpsolver.getLp().row_lower_.size());
    cutset.clear();
  }
}

void HighsLpRelaxation::removeObsoleteRows(bool notifyPool) {
  HighsInt nlprows = numRows();
  HighsInt nummodelrows = getNumModelRows();
  std::vector<HighsInt> deletemask;

  HighsInt ndelcuts = 0;
  for (HighsInt i = nummodelrows; i != nlprows; ++i) {
    assert(lprows[i].origin == LpRow::Origin::kCutPool);
    if (lpsolver.getBasis().row_status[i] == HighsBasisStatus::kBasic) {
      if (ndelcuts == 0) deletemask.resize(nlprows);
      ++ndelcuts;
      deletemask[i] = 1;
      if (notifyPool) mipsolver.mipdata_->cutpool.lpCutRemoved(lprows[i].index);
    }
  }

  removeCuts(ndelcuts, deletemask);
}

void HighsLpRelaxation::removeCuts(HighsInt ndelcuts,
                                   std::vector<HighsInt>& deletemask) {
  assert(lpsolver.getLp().num_row_ ==
         (HighsInt)lpsolver.getLp().row_lower_.size());
  if (ndelcuts > 0) {
    HighsBasis basis = lpsolver.getBasis();
    HighsInt nlprows = lpsolver.getNumRow();
    lpsolver.deleteRows(deletemask.data());
    for (HighsInt i = mipsolver.numRow(); i != nlprows; ++i) {
      if (deletemask[i] >= 0) {
        lprows[deletemask[i]] = lprows[i];
        basis.row_status[deletemask[i]] = basis.row_status[i];
      }
    }

    assert(lpsolver.getLp().num_row_ ==
           (HighsInt)lpsolver.getLp().row_lower_.size());

    basis.row_status.resize(basis.row_status.size() - ndelcuts);
    lprows.resize(lprows.size() - ndelcuts);

    assert(lpsolver.getLp().num_row_ == (HighsInt)lprows.size());
    basis.debug_origin_name = "HighsLpRelaxation::removeCuts";
    lpsolver.setBasis(basis);
    lpsolver.run();
  }
}

void HighsLpRelaxation::removeCuts() {
  assert(lpsolver.getLp().num_row_ ==
         (HighsInt)lpsolver.getLp().row_lower_.size());
  HighsInt nlprows = lpsolver.getNumRow();
  HighsInt modelrows = mipsolver.numRow();

  lpsolver.deleteRows(modelrows, nlprows - 1);
  for (HighsInt i = modelrows; i != nlprows; ++i) {
    if (lprows[i].origin == LpRow::Origin::kCutPool)
      mipsolver.mipdata_->cutpool.lpCutRemoved(lprows[i].index);
  }
  lprows.resize(modelrows);
  assert(lpsolver.getLp().num_row_ ==
         (HighsInt)lpsolver.getLp().row_lower_.size());
}

void HighsLpRelaxation::performAging(bool useBasis) {
  assert(lpsolver.getLp().num_row_ ==
         (HighsInt)lpsolver.getLp().row_lower_.size());

  size_t agelimit = mipsolver.options_mip_->mip_lp_age_limit;

  ++epochs;
  if (epochs % std::max(size_t(agelimit) / 2u, size_t(2)) != 0)
    agelimit = kHighsIInf;
  else if (epochs < agelimit)
    agelimit = epochs;

  HighsInt nlprows = numRows();
  HighsInt nummodelrows = getNumModelRows();
  std::vector<HighsInt> deletemask;

  if (!useBasis && agelimit != kHighsIInf) {
    HighsBasis b = mipsolver.mipdata_->firstrootbasis;
    b.row_status.resize(nlprows, HighsBasisStatus::kBasic);
    b.debug_origin_name = "HighsLpRelaxation::removeCuts";
    HighsStatus st = lpsolver.setBasis(b);
    assert(st != HighsStatus::kError);
  }

  HighsInt ndelcuts = 0;
  for (HighsInt i = nummodelrows; i != nlprows; ++i) {
    assert(lprows[i].origin == LpRow::Origin::kCutPool);
    if (!useBasis ||
        lpsolver.getBasis().row_status[i] == HighsBasisStatus::kBasic) {
      lprows[i].age += 1;
      if (lprows[i].age > agelimit) {
        if (ndelcuts == 0) deletemask.resize(nlprows);
        ++ndelcuts;
        deletemask[i] = 1;
        mipsolver.mipdata_->cutpool.lpCutRemoved(lprows[i].index);
      }
    } else if (std::abs(lpsolver.getSolution().row_dual[i]) >
               lpsolver.getOptions().dual_feasibility_tolerance) {
      lprows[i].age = 0;
    }
  }

  removeCuts(ndelcuts, deletemask);
}

void HighsLpRelaxation::resetAges() {
  assert(lpsolver.getLp().num_row_ ==
         (HighsInt)lpsolver.getLp().row_lower_.size());

  HighsInt nlprows = numRows();
  HighsInt nummodelrows = getNumModelRows();

  for (HighsInt i = nummodelrows; i != nlprows; ++i) {
    assert(lprows[i].origin == LpRow::Origin::kCutPool);
    if (lpsolver.getBasis().row_status[i] != HighsBasisStatus::kBasic &&
        std::abs(lpsolver.getSolution().row_dual[i]) >
            lpsolver.getOptions().dual_feasibility_tolerance)
      lprows[i].age = 0;
  }
}

void HighsLpRelaxation::flushDomain(HighsDomain& domain, bool continuous) {
  if (!domain.getChangedCols().empty()) {
    if (&domain == &mipsolver.mipdata_->domain) continuous = true;
    currentbasisstored = false;
    for (HighsInt col : domain.getChangedCols()) {
      if (!continuous &&
          mipsolver.variableType(col) == HighsVarType::kContinuous)
        continue;
      mask[col] = 1;
    }

    lpsolver.changeColsBounds(mask.data(), domain.col_lower_.data(),
                              domain.col_upper_.data());

    for (HighsInt col : domain.getChangedCols()) mask[col] = 0;

    domain.clearChangedCols();
  }
}

bool HighsLpRelaxation::computeDualProof(const HighsDomain& globaldomain,
                                         double upperbound,
                                         std::vector<HighsInt>& inds,
                                         std::vector<double>& vals, double& rhs,
                                         bool extractCliques) const {
  std::vector<double> row_dual = lpsolver.getSolution().row_dual;

  const HighsLp& lp = lpsolver.getLp();

  assert(std::isfinite(upperbound));
  HighsCDouble upper = upperbound;

  for (HighsInt i = 0; i != lp.num_row_; ++i) {
    // @FlipRowDual row_dual[i] < 0 became row_dual[i] > 0
    if (row_dual[i] > 0) {
      if (lp.row_lower_[i] != -kHighsInf)
        // @FlipRowDual += became -=
        upper -= row_dual[i] * lp.row_lower_[i];
      else
        row_dual[i] = 0;
      // @FlipRowDual row_dual[i] > 0 became row_dual[i] < 0
    } else if (row_dual[i] < 0) {
      if (lp.row_upper_[i] != kHighsInf)
        // @FlipRowDual += became -=
        upper -= row_dual[i] * lp.row_upper_[i];
      else
        row_dual[i] = 0;
    }
  }

  inds.clear();
  vals.clear();
  inds.reserve(lp.num_col_);
  vals.reserve(lp.num_col_);
  for (HighsInt i = 0; i != lp.num_col_; ++i) {
    HighsInt start = lp.a_matrix_.start_[i];
    HighsInt end = lp.a_matrix_.start_[i + 1];

    HighsCDouble sum = lp.col_cost_[i];

    for (HighsInt j = start; j != end; ++j) {
      if (row_dual[lp.a_matrix_.index_[j]] == 0) continue;
      // @FlipRowDual += became -=
      sum -= lp.a_matrix_.value_[j] * row_dual[lp.a_matrix_.index_[j]];
    }

    double val = double(sum);

    if (std::abs(val) <= mipsolver.options_mip_->small_matrix_value) continue;

    bool removeValue = std::abs(val) <= mipsolver.mipdata_->feastol ||
                       globaldomain.col_lower_[i] == globaldomain.col_upper_[i];

    if (!removeValue &&
        mipsolver.variableType(i) == HighsVarType::kContinuous) {
      if (val > 0)
        removeValue =
            lpsolver.getSolution().col_value[i] - globaldomain.col_lower_[i] <=
            mipsolver.mipdata_->feastol;
      else
        removeValue =
            globaldomain.col_upper_[i] - lpsolver.getSolution().col_value[i] <=
            mipsolver.mipdata_->feastol;
    }

    if (removeValue) {
      if (val < 0) {
        if (globaldomain.col_upper_[i] == kHighsInf) return false;
        upper -= val * globaldomain.col_upper_[i];
      } else {
        if (globaldomain.col_lower_[i] == -kHighsInf) return false;

        upper -= val * globaldomain.col_lower_[i];
      }

      continue;
    }

    vals.push_back(val);
    inds.push_back(i);
  }

  rhs = double(upper);
  assert(std::isfinite(rhs));
  globaldomain.tightenCoefficients(inds.data(), vals.data(), inds.size(), rhs);

  mipsolver.mipdata_->debugSolution.checkCut(inds.data(), vals.data(),
                                             inds.size(), rhs);
  if (extractCliques)
    mipsolver.mipdata_->cliquetable.extractCliquesFromCut(
        mipsolver, inds.data(), vals.data(), inds.size(), rhs);

  return true;
}

void HighsLpRelaxation::storeDualInfProof() {
  assert(lpsolver.getModelStatus(true) == HighsModelStatus::kInfeasible);

  HighsInt numrow = lpsolver.getNumRow();
  hasdualproof = false;
  lpsolver.getDualRay(hasdualproof);

  if (!hasdualproof) {
    highsLogDev(mipsolver.options_mip_->log_options, HighsLogType::kVerbose,
                "no dual ray stored\n");
    return;
  }

  dualproofinds.clear();
  dualproofvals.clear();
  dualproofrhs = kHighsInf;
  const HighsLp& lp = lpsolver.getLp();
  dualproofbuffer.resize(numrow);

  lpsolver.getDualRay(hasdualproof, dualproofbuffer.data());
  std::vector<double>& dualray = dualproofbuffer;

  HighsCDouble upper = 0.0;

  double maxval = 0;
  for (HighsInt i = 0; i != lp.num_row_; ++i)
    maxval = std::max(maxval, std::abs(dualray[i]));

  int expscal;
  std::frexp(maxval, &expscal);
  expscal = -expscal;

  for (HighsInt i = 0; i != lp.num_row_; ++i) {
    dualray[i] = std::ldexp(dualray[i], expscal);
    if (std::abs(dualray[i]) <= mipsolver.mipdata_->epsilon ||
        std::abs(dualray[i]) * getMaxAbsRowVal(i) <=
            mipsolver.mipdata_->feastol)
      dualray[i] = 0;
    else if (dualray[i] < 0) {
      if (lp.row_upper_[i] == kHighsInf) dualray[i] = 0.0;
    } else if (dualray[i] > 0) {
      if (lp.row_lower_[i] == -kHighsInf) dualray[i] = 0.0;
    }
  }

  for (HighsInt i = 0; i != lp.num_row_; ++i) {
    if (dualray[i] < 0) {
      assert(lp.row_upper_[i] != kHighsInf);
      upper -= dualray[i] * lp.row_upper_[i];
    } else if (dualray[i] > 0) {
      assert(lp.row_lower_[i] != -kHighsInf);
      upper -= dualray[i] * lp.row_lower_[i];
    }
  }

  for (HighsInt i = 0; i != lp.num_col_; ++i) {
    HighsInt start = lp.a_matrix_.start_[i];
    HighsInt end = lp.a_matrix_.start_[i + 1];

    HighsCDouble sum = 0.0;

    for (HighsInt j = start; j != end; ++j) {
      if (dualray[lp.a_matrix_.index_[j]] == 0.0) continue;
      sum -= lp.a_matrix_.value_[j] * dualray[lp.a_matrix_.index_[j]];
    }

    double val = double(sum);

    if (std::abs(val) <= mipsolver.options_mip_->small_matrix_value) continue;

    if (mipsolver.variableType(i) == HighsVarType::kContinuous ||
        std::abs(val) <= mipsolver.mipdata_->feastol ||
        mipsolver.mipdata_->domain.col_lower_[i] ==
            mipsolver.mipdata_->domain.col_upper_[i]) {
      if (val < 0) {
        if (mipsolver.mipdata_->domain.col_upper_[i] == kHighsInf) return;
        upper -= val * mipsolver.mipdata_->domain.col_upper_[i];
      } else {
        if (mipsolver.mipdata_->domain.col_lower_[i] == -kHighsInf) return;
        upper -= val * mipsolver.mipdata_->domain.col_lower_[i];
      }

      continue;
    }

    dualproofvals.push_back(val);
    dualproofinds.push_back(i);
  }

  dualproofrhs = double(upper);
  mipsolver.mipdata_->domain.tightenCoefficients(
      dualproofinds.data(), dualproofvals.data(), dualproofinds.size(),
      dualproofrhs);

  mipsolver.mipdata_->debugSolution.checkCut(
      dualproofinds.data(), dualproofvals.data(), dualproofinds.size(),
      dualproofrhs);

  mipsolver.mipdata_->cliquetable.extractCliquesFromCut(
      mipsolver, dualproofinds.data(), dualproofvals.data(),
      dualproofinds.size(), dualproofrhs);
}

void HighsLpRelaxation::storeDualUBProof() {
  assert(lpsolver.getModelStatus(true) == HighsModelStatus::kObjectiveBound);

  dualproofinds.clear();
  dualproofvals.clear();

  hasdualproof = computeDualProof(mipsolver.mipdata_->domain,
                                  mipsolver.mipdata_->upper_limit,
                                  dualproofinds, dualproofvals, dualproofrhs);
  if (!hasdualproof) dualproofrhs = kHighsInf;
}

bool HighsLpRelaxation::checkDualProof() const {
  if (!hasdualproof) return true;
  if (dualproofrhs == kHighsInf) return false;

  HighsInt len = dualproofinds.size();

  HighsCDouble viol = -dualproofrhs;

  const HighsLp& lp = lpsolver.getLp();

  for (HighsInt i = 0; i != len; ++i) {
    HighsInt col = dualproofinds[i];
    if (dualproofvals[i] > 0) {
      if (lp.col_lower_[col] == -kHighsInf) return false;
      viol += dualproofvals[i] * lp.col_lower_[col];
    } else {
      assert(dualproofvals[i] < 0);
      if (lp.col_upper_[col] == kHighsInf) return false;
      viol += dualproofvals[i] * lp.col_upper_[col];
    }
  }

  return viol > mipsolver.mipdata_->feastol;
}

bool HighsLpRelaxation::computeDualInfProof(const HighsDomain& globaldomain,
                                            std::vector<HighsInt>& inds,
                                            std::vector<double>& vals,
                                            double& rhs) {
  if (!hasdualproof) return false;

  // assert(checkDualProof());

  inds = dualproofinds;
  vals = dualproofvals;
  rhs = dualproofrhs;
  return true;
}

void HighsLpRelaxation::recoverBasis() {
  if (basischeckpoint) {
    lpsolver.setBasis(*basischeckpoint, "HighsLpRelaxation::recoverBasis");
    currentbasisstored = true;
  }
}

void HighsLpRelaxation::setObjectiveLimit(double objlim) {
  lpsolver.setOptionValue(
      "objective_bound",
      objlim + std::max(0.5, mipsolver.mipdata_->lower_bound *
                                 mipsolver.mipdata_->feastol));
}

HighsLpRelaxation::Status HighsLpRelaxation::run(bool resolve_on_error) {
  lpsolver.setOptionValue(
      "time_limit", lpsolver.getRunTime() + mipsolver.options_mip_->time_limit -
                        mipsolver.timer_.read(mipsolver.timer_.solve_clock));
  // lpsolver.setOptionValue("output_flag", true);
  HighsStatus callstatus = lpsolver.run();

  const HighsInfo& info = lpsolver.getInfo();
  HighsInt itercount = std::max(HighsInt{0}, info.simplex_iteration_count);
  numlpiters += itercount;

  if (callstatus == HighsStatus::kError) {
    lpsolver.clearSolver();
#if 0
    // first try to use the primal simplex solver starting from the last basis
    if (lpsolver.getOptions().simplex_strategy == kSimplexStrategyDual) {
      lpsolver.setOptionValue("simplex_strategy", kSimplexStrategyPrimal);
      recoverBasis();
      auto retval = run(resolve_on_error);
      lpsolver.setOptionValue("simplex_strategy", kSimplexStrategyDual);

      return retval;
    }
#endif

    if (resolve_on_error) {
      // still an error: now try to solve with presolve from scratch
      lpsolver.setOptionValue("simplex_strategy", kSimplexStrategyDual);
      lpsolver.setOptionValue("presolve", "on");
      auto retval = run(false);
      lpsolver.setOptionValue("presolve", "off");

      return retval;
    }

    recoverBasis();

    return Status::kError;
  }

  HighsModelStatus scaledmodelstatus = lpsolver.getModelStatus(true);
  switch (scaledmodelstatus) {
    case HighsModelStatus::kObjectiveBound:
      ++numSolved;
      avgSolveIters += (itercount - avgSolveIters) / numSolved;

      storeDualUBProof();
      if (hasdualproof && checkDualProof()) {
        // printf("proof constraint for obj limit %g valid\n",
        //        lpsolver.getOptions().objective_bound);
        return Status::kInfeasible;
      } else {
        double objbound = lpsolver.getOptions().objective_bound;
        // printf(
        //     "proof constraint for obj limit %g not valid, solving without "
        //     "objlim\n",
        //     objbound);
        lpsolver.setOptionValue("objective_bound", kHighsInf);
        Status result = run(resolve_on_error);
        lpsolver.setOptionValue("objective_bound", objbound);
        return result;
      }
    case HighsModelStatus::kInfeasible: {
      ++numSolved;
      avgSolveIters += (itercount - avgSolveIters) / numSolved;

      storeDualInfProof();
      if (true || checkDualProof()) return Status::kInfeasible;
      // /printf("infeasibility proof not valid\n");
      hasdualproof = false;

      // HighsInt scalestrategy = lpsolver.getOptions().simplex_scale_strategy;
      // if (scalestrategy != kSimplexScaleStrategyOff) {
      //   lpsolver.setOptionValue("simplex_scale_strategy",
      //                           kSimplexScaleStrategyOff);
      //   HighsBasis basis = lpsolver.getBasis();
      //   lpsolver.clearSolver();
      //   lpsolver.setBasis(basis);
      //   auto tmp = run(resolve_on_error);
      //   lpsolver.setOptionValue("simplex_scale_strategy", scalestrategy);
      //   if (!scaledOptimal(tmp)) {
      //     lpsolver.clearSolver();
      //     lpsolver.setBasis(basis);
      //   }
      //   return tmp;
      // }
      //
      // // trust the primal simplex result without scaling
      // if (lpsolver.getModelStatus() == HighsModelStatus::kInfeasible)
      //   return Status::kInfeasible;

      // highsLogUser(mipsolver.options_mip_->log_options,
      //                 HighsLogType::kWarning,
      //                 "LP failed to reliably determine infeasibility\n");

      // printf("error: unreliable infeasiblities, modelstatus = %"
      // HIGHSINT_FORMAT " (scaled
      // %" HIGHSINT_FORMAT ")\n",
      //        (HighsInt)lpsolver.getModelStatus(),
      //        (HighsInt)lpsolver.getModelStatus(true));
      return Status::kError;
    }
    case HighsModelStatus::kUnknown:
      if (info.basis_validity == kBasisValidityInvalid) return Status::kError;
      // fall through
    case HighsModelStatus::kOptimal:
      assert(info.max_primal_infeasibility >= 0);
      assert(info.max_dual_infeasibility >= 0);
      ++numSolved;
      avgSolveIters += (itercount - avgSolveIters) / numSolved;
      if (info.max_primal_infeasibility <= mipsolver.mipdata_->feastol &&
          info.max_dual_infeasibility <= mipsolver.mipdata_->feastol)
        return Status::kOptimal;

      if (info.max_primal_infeasibility <= mipsolver.mipdata_->feastol)
        return Status::kUnscaledPrimalFeasible;

      if (info.max_dual_infeasibility <= mipsolver.mipdata_->feastol)
        return Status::kUnscaledDualFeasible;

      return Status::kUnscaledInfeasible;
    case HighsModelStatus::kIterationLimit: {
      if (!mipsolver.submip && resolve_on_error) {
        // printf(
        //     "error: lpsolver reached iteration limit, resolving with basis "
        //     "from ipm\n");
        Highs ipm;
        ipm.passModel(lpsolver.getLp());
        ipm.setOptionValue("solver", "ipm");
        ipm.setOptionValue("output_flag", false);
        ipm.setOptionValue("ipm_iteration_limit", 200);
        // todo @ Julian : If you remove this you can see the looping on
        // istanbul-no-cutoff
        ipm.setOptionValue("simplex_iteration_limit",
                           info.simplex_iteration_count);
        ipm.run();
        lpsolver.setBasis(ipm.getBasis(), "HighsLpRelaxation::run IPM basis");
        return run(false);
      }

      // printf("error: lpsolver reached iteration limit\n");
      return Status::kError;
    }
    // case HighsModelStatus::kUnboundedOrInfeasible:
    //  if (lpsolver.getModelStatus(false) == scaledmodelstatus)
    //    return Status::kInfeasible;
    //  return Status::kError;
    case HighsModelStatus::kTimeLimit:
      return Status::kError;
    default:
      // printf("error: lpsolver stopped with unexpected status %"
      // HIGHSINT_FORMAT "\n",
      //        (HighsInt)scaledmodelstatus);
      highsLogUser(mipsolver.options_mip_->log_options, HighsLogType::kWarning,
                   "LP solved to unexpected status: %s\n",
                   lpsolver.modelStatusToString(scaledmodelstatus).c_str());
      return Status::kError;
  }
}

HighsLpRelaxation::Status HighsLpRelaxation::resolveLp(HighsDomain* domain) {
  fractionalints.clear();

  bool solveagain;
  do {
    solveagain = false;
    if (domain) flushDomain(*domain);
    status = run();

    switch (status) {
      case Status::kUnscaledInfeasible:
      case Status::kUnscaledDualFeasible:
      case Status::kUnscaledPrimalFeasible:
      case Status::kOptimal: {
        HighsHashTable<HighsInt, std::pair<double, int>> fracints(
            maxNumFractional);
        const HighsSolution& sol = lpsolver.getSolution();

        HighsCDouble objsum = 0;
        bool roundable = true;

        for (HighsInt i : mipsolver.mipdata_->integral_cols) {
          // for the fractionality we assume that LP bounds are not violated
          // bounds that are violated by the unscaled LP are indicated by the
          // return status already
          double val = std::max(
              std::min(sol.col_value[i], lpsolver.getLp().col_upper_[i]),
              lpsolver.getLp().col_lower_[i]);
          double intval = std::floor(val + 0.5);

          if (std::abs(val - intval) > mipsolver.mipdata_->feastol) {
            HighsInt col = i;
            if (roundable && mipsolver.mipdata_->uplocks[col] != 0 &&
                mipsolver.mipdata_->downlocks[col] != 0)
              roundable = false;

            const HighsCliqueTable::Substitution* subst =
                mipsolver.mipdata_->cliquetable.getSubstitution(col);
            while (subst != nullptr) {
              if (lpsolver.getLp().col_lower_[subst->replace.col] ==
                  lpsolver.getLp().col_upper_[subst->replace.col]) {
                if (domain) {
                  domain->fixCol(
                      col, subst->replace.weight(lpsolver.getLp().col_lower_));
                  if (domain->infeasible()) {
                    objective = kHighsInf;
                    status = Status::kInfeasible;
                    return status;
                  }
                } else
                  break;
              }

              col = subst->replace.col;
              if (subst->replace.val == 0) val = 1.0 - val;

              subst = mipsolver.mipdata_->cliquetable.getSubstitution(col);
            }

            col = mipsolver.mipdata_->symmetries.getBranchingColumn(
                getLp().col_lower_, getLp().col_upper_, col);

            auto& pair = fracints[col];
            pair.first += val;
            pair.second += 1;
          }
        }

        maxNumFractional =
            std::max((HighsInt)fracints.size(), maxNumFractional);

        if (domain && !domain->getChangedCols().empty()) {
          // printf("resolving due to fixings of substituted columns\n");
          solveagain = true;
          continue;
        }

        for (const auto& it : fracints) {
          fractionalints.emplace_back(
              it.key(), it.value().first / (double)it.value().second);
        }

        if (roundable && !fractionalints.empty()) {
          std::vector<double> roundsol = sol.col_value;

          for (const std::pair<HighsInt, double>& fracint : fractionalints) {
            HighsInt col = fracint.first;

            if (mipsolver.mipdata_->uplocks[col] == 0 &&
                (mipsolver.colCost(col) < 0 ||
                 mipsolver.mipdata_->downlocks[col] != 0))
              roundsol[col] = std::ceil(fracint.second);
            else
              roundsol[col] = std::floor(fracint.second);
          }

          const auto& cliquesubst =
              mipsolver.mipdata_->cliquetable.getSubstitutions();
          for (HighsInt k = cliquesubst.size() - 1; k >= 0; --k) {
            if (cliquesubst[k].replace.val == 0)
              roundsol[cliquesubst[k].substcol] =
                  1 - roundsol[cliquesubst[k].replace.col];
            else
              roundsol[cliquesubst[k].substcol] =
                  roundsol[cliquesubst[k].replace.col];
          }

          for (HighsInt i = 0; i != mipsolver.numCol(); ++i)
            objsum += roundsol[i] * mipsolver.colCost(i);

          mipsolver.mipdata_->addIncumbent(roundsol, double(objsum), 'S');
          objsum = 0;
        }

        for (HighsInt i = 0; i != mipsolver.numCol(); ++i)
          objsum += sol.col_value[i] * mipsolver.colCost(i);

        objective = double(objsum);
        break;
      }
      case Status::kInfeasible:
        objective = kHighsInf;
        break;
      default:
        break;
    }
  } while (solveagain);

  return status;
}
