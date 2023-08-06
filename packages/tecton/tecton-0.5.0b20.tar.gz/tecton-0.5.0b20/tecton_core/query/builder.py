from typing import Any
from typing import Dict
from typing import Optional

import pendulum

from tecton_core import time_utils
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_core.feature_definition_wrapper import pipeline_to_ds_inputs
from tecton_core.id_helper import IdHelper
from tecton_core.pipeline_common import get_time_window_from_data_source_node
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import AsofJoinNode
from tecton_core.query.nodes import DataNode
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import FeatureTimeFilterNode
from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_core.query.nodes import FullAggNode
from tecton_core.query.nodes import JoinNode
from tecton_core.query.nodes import OfflineStoreScanNode
from tecton_core.query.nodes import PartialAggNode
from tecton_core.query.nodes import RenameColsNode
from tecton_core.query.nodes import RespectFSTNode
from tecton_core.query.nodes import RespectTTLNode
from tecton_core.query.nodes import SetAnchorTimeNode

ANCHOR_TIME = "_anchor_time"


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
        input_name: DataSourceScanNode.ref(
            fdw.fco_container.get_by_id(IdHelper.to_string(node.virtual_data_source_id)),
            node,
            get_time_window_from_data_source_node(feature_data_time_limits, schedule_interval, node),
        )
        for input_name, node in ds_inputs.items()
    }


# build QueryTree that executes all transformations
def build_pipeline_querytree(
    fdw: FeatureDefinitionWrapper, feature_data_time_limits: Optional[pendulum.Period] = None
) -> NodeRef:
    inputs_map = build_datasource_input_querynodes(fdw, feature_data_time_limits)
    return FeatureViewPipelineNode.ref(
        pipeline=fdw.pipeline,
        inputs_map=inputs_map,
        feature_definition_wrapper=fdw,
        feature_time_limits=feature_data_time_limits,
    )


# builds a QueryTree for just whatever we would materialize
# ie partial aggregates for WAFVs.
def build_run_querytree(
    fdw: FeatureDefinitionWrapper, feature_data_time_limits: Optional[pendulum.Period] = None
) -> NodeRef:
    base = build_pipeline_querytree(fdw, feature_data_time_limits)
    tree = FeatureTimeFilterNode.ref(
        base,
        feature_data_time_limits=feature_data_time_limits,
        policy=fdw.time_range_policy,
        timestamp_field=fdw.timestamp_key,
    )
    if fdw.is_temporal:
        tree = SetAnchorTimeNode.ref(
            tree,
            offline=True,
            feature_store_format_version=fdw.get_feature_store_format_version,
            batch_schedule_in_feature_store_specific_version_units=time_utils.convert_proto_duration_for_version(
                fdw.fv.materialization_params.schedule_interval, fdw.get_feature_store_format_version
            ),
            timestamp_field=fdw.timestamp_key,
            retrieval=False,
        )
    elif fdw.is_temporal_aggregate:

        tree = PartialAggNode.ref(tree, fdw)
    else:
        raise Exception("unexpected FV type")
    return tree


# QueryTree for getting data from offline store
def build_offline_store_scan_querytree(fdw: FeatureDefinitionWrapper) -> NodeRef:
    return OfflineStoreScanNode.ref(feature_definition_wrapper=fdw)


def build_get_features_from_spine(fdw: FeatureDefinitionWrapper, spine: Any, spine_time_field: str, from_source: bool):
    if not from_source:
        base = build_offline_store_scan_querytree(fdw)
    else:
        base = build_run_querytree(fdw, None)
    if fdw.is_temporal:
        return base
    elif fdw.is_temporal_aggregate:
        return FullAggNode.ref(base, fdw, spine, spine_time_field)
    else:
        raise Exception("unexpected FV type")


def build_spine_join_querytree(
    fdw: FeatureDefinitionWrapper, spine: Any, spine_time_field: str, from_source: bool
) -> NodeRef:
    base = build_get_features_from_spine(fdw, spine=spine, spine_time_field=spine_time_field, from_source=from_source)
    spine_node = DataNode.ref(spine)
    if spine_time_field != fdw.timestamp_key:
        spine_node = RenameColsNode.ref(spine_node, [spine_time_field], [fdw.timestamp_key])
    if fdw.is_temporal:
        # TODO(TEC-9497): handle namespace/feature-service.ghf
        rightside_join_prefix = "_tecton_right"
        join_prefixed_feature_names = [f"{rightside_join_prefix}_{f}" for f in fdw.features]
        # we can't just ask for the correct right_prefix to begin with because the asofJoin always sticks an extra underscore in between
        rename_map = {f"{rightside_join_prefix}_{f}": f"{fdw.name}{fdw.namespace_separator}{f}" for f in fdw.features}
        rename_map[f"{rightside_join_prefix}_{fdw.timestamp_key}"] = None
        rename_map[f"{rightside_join_prefix}_{ANCHOR_TIME}"] = None

        respected_fst_node = RespectFSTNode.ref(base, fdw.timestamp_key, fdw.feature_start_timestamp, fdw.features)
        join = AsofJoinNode.ref(
            spine_node,
            respected_fst_node,
            join_cols=fdw.join_keys,
            timestamp_field=fdw.timestamp_key,
            right_prefix=rightside_join_prefix,
        )
        ttl_node = RespectTTLNode.ref(
            join,
            fdw.timestamp_key,
            f"{rightside_join_prefix}_{fdw.timestamp_key}",
            fdw.serving_ttl,
            join_prefixed_feature_names,
        )
        # remove anchor cols/dupe timestamp cols
        ret = RenameColsNode.ref(ttl_node, rename_map)
    elif fdw.is_temporal_aggregate:
        augmented_spine = SetAnchorTimeNode.ref(
            spine_node,
            offline=True,
            feature_store_format_version=fdw.get_feature_store_format_version,
            batch_schedule_in_feature_store_specific_version_units=fdw.get_tile_interval_for_version,
            timestamp_field=fdw.timestamp_key,
            retrieval=True,
        )
        # TODO(TEC-9497) handle namespace/feature-service.ghf
        renamed_features = {feature: fdw.name + fdw.namespace_separator + feature for feature in fdw.features}
        right = RenameColsNode.ref(base, renamed_features)
        join_keys = fdw.join_keys + [ANCHOR_TIME]
        # TODO: can consider having "inner" be an enum. right now join type as string can be passed directly to spark/snowflake
        join = JoinNode.ref(augmented_spine, right, how="inner", join_cols=join_keys)
        # Drop anchor time col
        ret = RenameColsNode.ref(join, {ANCHOR_TIME: None})
    else:
        raise NotImplementedError
    if spine_time_field != fdw.timestamp_key:
        ret = RenameColsNode.ref(ret, {fdw.timestamp_key: spine_time_field})
    return ret
