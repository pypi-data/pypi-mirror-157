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
#include "mip/HighsNodeQueue.h"

#include <algorithm>
#include <tuple>

#include "lp_data/HConst.h"
#include "mip/HighsDomain.h"
#include "mip/HighsLpRelaxation.h"
#include "mip/HighsMipSolverData.h"
#include "util/HighsSplay.h"

#define ESTIMATE_WEIGHT .5
#define LOWERBOUND_WEIGHT .5

namespace highs {
template <>
struct RbTreeTraits<HighsNodeQueue::NodeLowerRbTree> {
  using KeyType = std::tuple<double, double, HighsInt>;
};

template <>
struct RbTreeTraits<HighsNodeQueue::NodeHybridEstimRbTree> {
  using KeyType = std::tuple<double, HighsInt, HighsInt>;
};
}  // namespace highs

using namespace highs;

class HighsNodeQueue::NodeLowerRbTree : public CacheMinRbTree<NodeLowerRbTree> {
  HighsNodeQueue* nodeQueue;

 public:
  NodeLowerRbTree(HighsNodeQueue* nodeQueue)
      : CacheMinRbTree<NodeLowerRbTree>(nodeQueue->lowerRoot,
                                        nodeQueue->lowerMin),
        nodeQueue(nodeQueue) {}

  RbTreeLinks& getRbTreeLinks(HighsInt node) {
    return nodeQueue->nodes[node].lowerLinks;
  }
  const RbTreeLinks& getRbTreeLinks(HighsInt node) const {
    return nodeQueue->nodes[node].lowerLinks;
  }
  std::tuple<double, double, HighsInt> getKey(HighsInt node) const {
    return std::make_tuple(nodeQueue->nodes[node].lower_bound,
                           nodeQueue->nodes[node].estimate, node);
  }
};

class HighsNodeQueue::NodeHybridEstimRbTree
    : public CacheMinRbTree<NodeHybridEstimRbTree> {
  HighsNodeQueue* nodeQueue;

 public:
  NodeHybridEstimRbTree(HighsNodeQueue* nodeQueue)
      : CacheMinRbTree<NodeHybridEstimRbTree>(nodeQueue->hybridEstimRoot,
                                              nodeQueue->hybridEstimMin),
        nodeQueue(nodeQueue) {}

  RbTreeLinks& getRbTreeLinks(HighsInt node) {
    return nodeQueue->nodes[node].hybridEstimLinks;
  }
  const RbTreeLinks& getRbTreeLinks(HighsInt node) const {
    return nodeQueue->nodes[node].hybridEstimLinks;
  }
  std::tuple<double, HighsInt, HighsInt> getKey(HighsInt node) const {
    constexpr double kLbWeight = 0.5;
    constexpr double kEstimWeight = 0.5;
    return std::make_tuple(kLbWeight * nodeQueue->nodes[node].lower_bound +
                               kEstimWeight * nodeQueue->nodes[node].estimate,
                           -HighsInt(nodeQueue->nodes[node].domchgstack.size()),
                           node);
  }
};

void HighsNodeQueue::link_estim(HighsInt node) {
  assert(node != -1);
  NodeHybridEstimRbTree rbTree(this);
  rbTree.link(node);
}

void HighsNodeQueue::unlink_estim(HighsInt node) {
  assert(node != -1);
  NodeHybridEstimRbTree rbTree(this);
  rbTree.unlink(node);
}

void HighsNodeQueue::link_lower(HighsInt node) {
  assert(node != -1);
  NodeLowerRbTree rbTree(this);
  rbTree.link(node);
}

void HighsNodeQueue::unlink_lower(HighsInt node) {
  assert(node != -1);
  NodeLowerRbTree rbTree(this);
  rbTree.unlink(node);
}

void HighsNodeQueue::link_domchgs(HighsInt node) {
  assert(node != -1);
  HighsInt numchgs = nodes[node].domchgstack.size();
  nodes[node].domchglinks.resize(numchgs);

  for (HighsInt i = 0; i != numchgs; ++i) {
    double val = nodes[node].domchgstack[i].boundval;
    HighsInt col = nodes[node].domchgstack[i].column;
    switch (nodes[node].domchgstack[i].boundtype) {
      case HighsBoundType::kLower:
        nodes[node].domchglinks[i] =
            colLowerNodes[col].emplace(val, node).first;
        break;
      case HighsBoundType::kUpper:
        nodes[node].domchglinks[i] =
            colUpperNodes[col].emplace(val, node).first;
    }
  }
}

void HighsNodeQueue::unlink_domchgs(HighsInt node) {
  assert(node != -1);
  HighsInt numchgs = nodes[node].domchgstack.size();

  for (HighsInt i = 0; i != numchgs; ++i) {
    HighsInt col = nodes[node].domchgstack[i].column;
    switch (nodes[node].domchgstack[i].boundtype) {
      case HighsBoundType::kLower:
        colLowerNodes[col].erase(nodes[node].domchglinks[i]);
        break;
      case HighsBoundType::kUpper:
        colUpperNodes[col].erase(nodes[node].domchglinks[i]);
    }
  }

  nodes[node].domchglinks.clear();
  nodes[node].domchglinks.shrink_to_fit();
}

void HighsNodeQueue::link(HighsInt node) {
  link_estim(node);
  link_lower(node);
  link_domchgs(node);
}

void HighsNodeQueue::unlink(HighsInt node) {
  unlink_estim(node);
  unlink_lower(node);
  unlink_domchgs(node);
  freeslots.push(node);
}

void HighsNodeQueue::setNumCol(HighsInt numcol) {
  colLowerNodes.resize(numcol);
  colUpperNodes.resize(numcol);
}

void HighsNodeQueue::checkGlobalBounds(HighsInt col, double lb, double ub,
                                       double feastol,
                                       HighsCDouble& treeweight) {
  std::set<HighsInt> delnodes;
  auto prunestart =
      colLowerNodes[col].lower_bound(std::make_pair(ub + feastol, -1));
  for (auto it = prunestart; it != colLowerNodes[col].end(); ++it)
    delnodes.insert(it->second);

  auto pruneend =
      colUpperNodes[col].upper_bound(std::make_pair(lb - feastol, kHighsIInf));
  for (auto it = colUpperNodes[col].begin(); it != pruneend; ++it)
    delnodes.insert(it->second);

  for (HighsInt delnode : delnodes) {
    treeweight += std::ldexp(1.0, 1 - nodes[delnode].depth);
    unlink(delnode);
  }
}

double HighsNodeQueue::pruneInfeasibleNodes(HighsDomain& globaldomain,
                                            double feastol) {
  size_t numchgs;

  HighsCDouble treeweight = 0.0;

  do {
    if (globaldomain.infeasible()) break;

    numchgs = globaldomain.getDomainChangeStack().size();

    assert(colLowerNodes.size() == globaldomain.col_lower_.size());
    HighsInt numcol = colLowerNodes.size();
    for (HighsInt i = 0; i != numcol; ++i) {
      checkGlobalBounds(i, globaldomain.col_lower_[i],
                        globaldomain.col_upper_[i], feastol, treeweight);
    }

    size_t numopennodes = numNodes();
    if (numopennodes == 0) break;

    for (HighsInt i = 0; i != numcol; ++i) {
      if (colLowerNodes[i].size() == numopennodes) {
        double globallb = colLowerNodes[i].begin()->first;
        if (globallb > globaldomain.col_lower_[i]) {
          globaldomain.changeBound(HighsBoundType::kLower, i, globallb,
                                   HighsDomain::Reason::unspecified());
          if (globaldomain.infeasible()) break;
        }
      }

      if (colUpperNodes[i].size() == numopennodes) {
        double globalub = colUpperNodes[i].rbegin()->first;
        if (globalub < globaldomain.col_upper_[i]) {
          globaldomain.changeBound(HighsBoundType::kUpper, i, globalub,
                                   HighsDomain::Reason::unspecified());
          if (globaldomain.infeasible()) break;
        }
      }
    }

    globaldomain.propagate();
  } while (numchgs != globaldomain.getDomainChangeStack().size());

  return double(treeweight);
}

double HighsNodeQueue::pruneNode(HighsInt nodeId) {
  double treeweight = std::ldexp(1.0, 1 - nodes[nodeId].depth);
  unlink(nodeId);
  return treeweight;
}

double HighsNodeQueue::performBounding(double upper_limit) {
  NodeLowerRbTree lowerTree(this);

  if (lowerTree.empty()) return 0.0;

  HighsCDouble treeweight = 0.0;

  HighsInt maxLbNode = lowerTree.last();
  while (maxLbNode != -1) {
    if (nodes[maxLbNode].lower_bound < upper_limit) break;
    HighsInt next = lowerTree.predecessor(maxLbNode);
    treeweight += pruneNode(maxLbNode);
    maxLbNode = next;
  }

  return double(treeweight);
}

void HighsNodeQueue::emplaceNode(std::vector<HighsDomainChange>&& domchgs,
                                 std::vector<HighsInt>&& branchPositions,
                                 double lower_bound, double estimate,
                                 HighsInt depth) {
  HighsInt pos;

  if (freeslots.empty()) {
    pos = nodes.size();
    nodes.emplace_back(std::move(domchgs), std::move(branchPositions),
                       lower_bound, estimate, depth);
  } else {
    pos = freeslots.top();
    freeslots.pop();
    nodes[pos] = OpenNode(std::move(domchgs), std::move(branchPositions),
                          lower_bound, estimate, depth);
  }

  assert(nodes[pos].lower_bound == lower_bound);
  assert(nodes[pos].estimate == estimate);
  assert(nodes[pos].depth == depth);

  link(pos);
}

HighsNodeQueue::OpenNode&& HighsNodeQueue::popBestNode() {
  HighsInt bestNode = hybridEstimMin;

  unlink(bestNode);

  return std::move(nodes[bestNode]);
}

HighsNodeQueue::OpenNode&& HighsNodeQueue::popBestBoundNode() {
  HighsInt bestBoundNode = lowerMin;

  unlink(bestBoundNode);

  return std::move(nodes[bestBoundNode]);
}

double HighsNodeQueue::getBestLowerBound() {
  if (lowerMin == -1) return kHighsInf;

  return nodes[lowerMin].lower_bound;
}
