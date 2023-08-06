from typing import Dict
from typing import Optional

import pendulum

from tecton_core import time_utils
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_core.feature_definition_wrapper import pipeline_to_ds_inputs
from tecton_core.id_helper import IdHelper
from tecton_core.pipeline_common import get_time_window_from_data_source_node
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import FeatureTimeFilterNode
from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_core.query.nodes import PartialAggNode
from tecton_core.query.nodes import SetAnchorTimeNode


def build_datasource_input_querynodes(
    fdw: FeatureDefinitionWrapper, feature_data_time_limits: Optional[pendulum.Period] = None
) -> Dict[str, NodeRef]:
    """
    Starting in FWV5, data sources of FVs with incremental backfills may contain transformations that are only
    correct if the data has been filtered to a specific range.
    """
    schedule_interval = fdw.get_tile_interval if fdw.is_temporal else None
    ds_inputs = pipeline_to_ds_inputs(fdw.pipeline)
    return {
        input_name: NodeRef(
            DataSourceScanNode(
                fdw.fco_container.get_by_id(IdHelper.to_string(node.virtual_data_source_id)),
                node,
                get_time_window_from_data_source_node(feature_data_time_limits, schedule_interval, node),
            )
        )
        for input_name, node in ds_inputs.items()
    }


# build QueryTree that executes all transformations
def build_pipeline_querytree(
    fdw: FeatureDefinitionWrapper, feature_data_time_limits: Optional[pendulum.Period] = None
) -> NodeRef:
    inputs_map = build_datasource_input_querynodes(fdw, feature_data_time_limits)
    return NodeRef(
        FeatureViewPipelineNode(
            pipeline=fdw.pipeline,
            inputs_map=inputs_map,
            feature_definition_wrapper=fdw,
            feature_time_limits=feature_data_time_limits,
        )
    )


# builds a QueryTree for just whatever we would materialize
# ie partial aggregates for WAFVs.
def build_run_querytree(
    fdw: FeatureDefinitionWrapper, feature_data_time_limits: Optional[pendulum.Period] = None
) -> NodeRef:
    base = build_pipeline_querytree(fdw, feature_data_time_limits)
    tree = NodeRef(
        FeatureTimeFilterNode(
            base,
            feature_data_time_limits=feature_data_time_limits,
            policy=fdw.time_range_policy,
            timestamp_field=fdw.timestamp_key,
        )
    )
    if fdw.is_temporal:
        tree = NodeRef(
            SetAnchorTimeNode(
                tree,
                offline=True,
                feature_store_format_version=fdw.get_feature_store_format_version,
                batch_schedule_seconds=time_utils.convert_proto_duration_for_version(
                    fdw.fv.materialization_params.schedule_interval, fdw.get_feature_store_format_version
                ),
                timestamp_field=fdw.timestamp_key,
            )
        )
    elif fdw.is_temporal_aggregate:
        tree = NodeRef(PartialAggNode(tree, fdw))
    else:
        raise Exception("unexpected FV type")
    return tree


# QueryTree for getting data from offline store
def build_offline_store_scan_querytree(fdw: FeatureDefinitionWrapper) -> NodeRef:
    raise NotImplementedError
    # return NodeRef(OfflineStoreScanNode(feature_definition_wrapper=fdw))
