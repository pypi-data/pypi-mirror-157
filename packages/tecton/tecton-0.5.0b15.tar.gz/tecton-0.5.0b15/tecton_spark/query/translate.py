from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import FeatureTimeFilterNode
from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_core.query.nodes import MockDataNode
from tecton_core.query.nodes import PartialAggNode
from tecton_core.query.nodes import SetAnchorTimeNode
from tecton_spark.query import data_source
from tecton_spark.query import filter
from tecton_spark.query import pipeline
from tecton_spark.query.node import SparkExecNode

# convert from logical tree to physical tree
def spark_convert(node_ref: NodeRef) -> SparkExecNode:
    logical_tree_node = node_ref.node
    node_mapping = {
        DataSourceScanNode: data_source.DataSourceScanSparkNode,
        FeatureViewPipelineNode: pipeline.PipelineEvalSparkNode,
        FeatureTimeFilterNode: filter.FeatureTimeFilterSparkNode,
        SetAnchorTimeNode: filter.SetAnchorTimeSparkNode,
        MockDataNode: data_source.MockDataSparkNode,
        PartialAggNode: pipeline.PartialAggSparkNode,
    }
    if logical_tree_node.__class__ in node_mapping:
        return node_mapping[logical_tree_node.__class__](logical_tree_node)
    else:
        raise Exception(f"TODO: mapping for {logical_tree_node.__class__}")
