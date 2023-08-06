from pyspark.sql import DataFrame

from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import MockDataNode
from tecton_spark import data_source_helper
from tecton_spark.query.node import SparkExecNode


class MockDataSparkNode(SparkExecNode):
    def __init__(self, node: MockDataNode):
        self.data = node.data

    def to_dataframe(self, spark):
        if isinstance(self.data, DataFrame):
            return self.data
        else:
            raise Exception(f"Unimplemented data type: {self.data}")


class DataSourceScanSparkNode(SparkExecNode):
    def __init__(self, node: DataSourceScanNode):
        self.inputs = []
        self.ds = node.ds
        self.time_filter = node.time_filter

    def to_dataframe(self, spark):
        start_time = self.time_filter.start if self.time_filter else None
        end_time = self.time_filter.end if self.time_filter else None
        return data_source_helper.get_ds_dataframe(
            spark, self.ds, consume_streaming_data_source=False, start_time=start_time, end_time=end_time
        )
