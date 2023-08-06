from pyspark.sql import functions

from tecton_core.query.nodes import FeatureTimeFilterNode
from tecton_core.query.nodes import SetAnchorTimeNode
from tecton_spark import materialization_plan
from tecton_spark.partial_aggregations import TEMPORAL_ANCHOR_COLUMN_NAME
from tecton_spark.query import translate
from tecton_spark.query.node import SparkExecNode
from tecton_spark.time_utils import convert_timestamp_to_epoch


class FeatureTimeFilterSparkNode(SparkExecNode):
    def __init__(self, node: FeatureTimeFilterNode):
        self.input_node = translate.spark_convert(node.input_node)
        self.time_filter = node.time_filter
        self.policy = node.policy
        self.timestamp_field = node.timestamp_field

    def to_dataframe(self, spark):
        input_df = self.input_node.to_dataframe(spark)
        return materialization_plan._apply_or_check_feature_data_time_limits(
            spark, input_df, self.policy, self.timestamp_field, self.time_filter
        )


class SetAnchorTimeSparkNode(SparkExecNode):
    def __init__(self, node: SetAnchorTimeNode):
        self.input_node = translate.spark_convert(node.input_node)
        self.offline = node.offline
        self.feature_store_format_version = node.feature_store_format_version
        self.batch_schedule_seconds = node.batch_schedule_seconds
        self.timestamp_field = node.timestamp_field

    def to_dataframe(self, spark):
        input_df = self.input_node.to_dataframe(spark)
        anchor_time_val = convert_timestamp_to_epoch(
            functions.col(self.timestamp_field), self.feature_store_format_version
        )
        df = input_df.withColumn(
            TEMPORAL_ANCHOR_COLUMN_NAME, anchor_time_val - anchor_time_val % self.batch_schedule_seconds
        )
        if not self.offline:
            MATERIALIZED_RAW_DATA_END_TIME = "_materialized_raw_data_end_time"
            df = df.withColumn(
                MATERIALIZED_RAW_DATA_END_TIME, functions.col(TEMPORAL_ANCHOR_COLUMN_NAME) + self.batch_schedule_seconds
            ).drop(TEMPORAL_ANCHOR_COLUMN_NAME)
        return df
