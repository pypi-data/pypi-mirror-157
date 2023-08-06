from pyspark.sql import SparkSession

from tecton_core.query.nodes import AsofJoinNode
from tecton_core.query.nodes import JoinNode
from tecton_spark.query import translate
from tecton_spark.query.node import SparkExecNode


class JoinSparkNode(SparkExecNode):
    """
    A basic left join on 2 inputs
    """

    def __init__(self, node: JoinNode):
        self.left = translate.spark_convert(node.left)
        self.right = translate.spark_convert(node.right)
        self.join_cols = node.join_cols
        self.how = node.how

    def to_dataframe(self, spark: SparkSession):
        left_df = self.left.to_dataframe(spark)
        right_df = self.right.to_dataframe(spark)
        return left_df.join(right_df, how=self.how, on=self.join_cols)


class AsofJoinSparkNode(SparkExecNode):
    """
    A "basic" asof join on 2 inputs
    """

    def __init__(self, node: AsofJoinNode):
        self.left = translate.spark_convert(node.left)
        self.right = translate.spark_convert(node.right)
        self.timestamp_field = node.timestamp_field
        self.join_cols = node.join_cols
        self.right_prefix = node.right_prefix

    def to_dataframe(self, spark: SparkSession):
        """
        We'd like to do the following:
        left_df = self.left.to_dataframe(spark)
        right_df = self.right.to_dataframe(spark)
        left_tsdf = TSDF(left_df, ts_col=self.timestamp_field, partition_cols=self.join_cols)
        right_tsdf = TSDF(right_df, ts_col=self.timestamp_field, partition_cols=self.join_cols)
        # TODO(TEC-9494) - we could speed up by setting partition_ts to ttl size
        out = left_tsdf.asofJoin(right_tsdf, right_prefix=self.right_prefix, skipNulls=False).df
        return out
        """

        raise NotImplementedError
