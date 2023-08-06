from abc import ABC
from abc import abstractmethod
from typing import Optional

import pendulum

from tecton_core import conf
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import FeatureTimeFilterNode
from tecton_core.query.nodes import FeatureViewPipelineNode


class Rewrite(ABC):
    @abstractmethod
    def rewrite(self, node: NodeRef) -> NodeRef:
        raise NotImplementedError


class RawDataTimeFilterPushdown(Rewrite):
    """
    Recurse to find a FeatureTimeFilterNode, convert the feature time limits to raw data time limits based on the FeatureView below it, and apply those to any data sources.
    This rewrite is necessary to apply for correct behavior if we have a FeatureTimeFilterSparkNode with an "assertion" policy (FWV3 and below).
    In the current iteration of the code, this rewrite is a no-op because time filters have already been applied. We'll either remove this later or make it work for pushing down spine time filters properly for
    cases where get_historical_features can work. TODO(TEC-9497)
    """

    def rewrite(self, nodeRef: NodeRef) -> NodeRef:
        node = nodeRef.node
        if isinstance(node, FeatureTimeFilterNode):
            feature_time_limits = node.time_filter
            for n in node.inputs:
                self._pushdown_feature_data_time_filter(n, feature_time_limits)
        else:
            for n in node.inputs:
                self.rewrite(n)
        return node

    def _pushdown_feature_data_time_filter(
        self,
        nodeRef: NodeRef,
        feature_data_time_limits: pendulum.Period,
        schedule_interval: Optional[pendulum.Period] = None,
    ):
        node = nodeRef.node
        if isinstance(node, DataSourceScanNode):
            nodeRef.node = node.with_feature_time_filter(feature_data_time_limits, schedule_interval)
        else:
            if isinstance(node, FeatureViewPipelineNode):
                # TODO(YIKES) on this logic <- is it correct? it kinda depends on whether we allow some types of custom windows for WAFV
                schedule_interval = (
                    node.feature_definition_wrapper.get_tile_interval
                    if node.feature_definition_wrapper.is_temporal
                    else None
                )
            for n in node.inputs:
                self._pushdown_feature_data_time_filter(n, feature_data_time_limits, schedule_interval)


# Mutates the input
def rewrite_tree(tree: NodeRef):
    if not conf.get_bool("QUERY_REWRITE_ENABLED"):
        return
    rewrites = [RawDataTimeFilterPushdown()]
    for rewrite in rewrites:
        rewrite.rewrite(tree)
