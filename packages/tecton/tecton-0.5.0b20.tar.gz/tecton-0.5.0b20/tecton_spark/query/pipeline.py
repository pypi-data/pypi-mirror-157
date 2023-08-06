from pyspark.sql import SparkSession

from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_core.query.nodes import FullAggNode
from tecton_core.query.nodes import PartialAggNode
from tecton_spark.aggregations import construct_full_tafv_df_with_anchor_time
from tecton_spark.partial_aggregations import construct_partial_time_aggregation_df
from tecton_spark.pipeline_helper import _PipelineBuilder
from tecton_spark.query import translate
from tecton_spark.query.node import SparkExecNode


class PipelineEvalSparkNode(SparkExecNode):
    def __init__(self, node: FeatureViewPipelineNode):
        self.inputs_map = {key: translate.spark_convert(node.inputs_map[key]) for key in node.inputs_map}
        self.feature_definition_wrapper = node.feature_definition_wrapper
        # Needed for correct behavior on MaterializationContextNode in the pipeline
        self.feature_time_limits = node.feature_time_limits
        self.schedule_interval = node.schedule_interval

    def to_dataframe(self, spark: SparkSession):
        return _PipelineBuilder(
            spark,
            self.feature_definition_wrapper.pipeline,
            consume_streaming_data_sources=False,
            data_sources=self.feature_definition_wrapper.data_sources,
            transformations=self.feature_definition_wrapper.transformations,
            feature_time_limits=self.feature_time_limits,
            schedule_interval=self.schedule_interval,
            passed_in_inputs={k: self.inputs_map[k].to_dataframe(spark) for k in self.inputs_map},
        ).get_dataframe()


class PartialAggSparkNode(SparkExecNode):
    def __init__(self, node: PartialAggNode):
        self.input_node = translate.spark_convert(node.input_node)
        self.fdw = node.fdw

    def to_dataframe(self, spark: SparkSession):
        df = construct_partial_time_aggregation_df(
            self.input_node.to_dataframe(spark),
            list(self.fdw.join_keys),
            self.fdw.trailing_time_window_aggregation,
            self.fdw.get_feature_store_format_version,
        )
        return df


class FullAggSparkNode(SparkExecNode):
    def __init__(self, node: FullAggNode):
        self.input_node = translate.spark_convert(node.input_node)
        self.fdw = node.fdw
        self.spine = node.spine
        self.spine_time_field = node.spine_time_field
        if self.spine_time_field is None:
            # We have not implemented the case for full agg without spine
            raise NotImplementedError

    def to_dataframe(self, spark: SparkSession):

        res = construct_full_tafv_df_with_anchor_time(
            spark=spark,
            time_aggregation=self.fdw.trailing_time_window_aggregation,
            join_keys=self.fdw.join_keys,
            feature_store_format_version=self.fdw.get_feature_store_format_version,
            tile_interval=self.fdw.get_tile_interval,
            all_partial_aggregations_df=self.input_node.to_dataframe(spark),
            use_materialized_data=False,
            spine_df=self.spine.withColumnRenamed(
                self.spine_time_field, self.fdw.timestamp_key
            ),  # we do janky stuff on the spine so keep it lightweight
            fd=self.fdw,
            spine_join_keys=self.fdw.join_keys,  # TODO: handle FeatureSetConfig
        )
        return res
