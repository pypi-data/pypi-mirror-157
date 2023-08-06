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
/**@file ipm/IpxWrapperEmpty.h
 * @brief
 */
#ifndef IPM_IPX_WRAPPER_EMPTY_H_
#define IPM_IPX_WRAPPER_EMPTY_H_

#include "lp_data/HighsLpSolverObject.h"

HighsStatus solveLpIpx(HighsLpSolverObject& solver_object) {
  solver_object.unscaled_model_status_ = HighsModelStatus::kNotset;
  return HighsStatus::kError;
}
#endif
