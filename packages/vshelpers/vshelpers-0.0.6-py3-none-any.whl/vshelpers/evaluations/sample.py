"""Sample evaluation analysis with curation and statistical"""
from collections import namedtuple

from helpers.statistic import *
from helpers.general import *
from helpers.clean import *


class SampleEvaluation():
    def __init__(self, sample_s3_path, file_type="csv"):
        self.file_type = file_type
        self.sample_s3_path = sample_s3_path
        self.df = remove_duplicates(spark.read.format(file_type).load(sample_s3_path))
        self.ping_count_df = ping_counts(self.df)

    def statistic_evaluation(self) -> namedtuple:
        statistic_metrics = namedtuple(
            "statistic_metrics", 
            "total_records, unique_dau_count, unique_row_count, dau_20p_count, avg_ping_per_dau, median_ping_per_dau, priority_point_count"
        )

        return statistic_metrics

    def curation_evaluation(self) -> namedtuple:
        curation_metrics = namedtuple(
            "curation_metrics",
            "..."
            )

        return curation_metrics
    
    def total_evaluation(self, run_statistics=False, run_curation=False):
        """Prints all the metrics associated with the sample evaluation"""
        if run_statistics:
            statistic_metrics = self.statistic_evaluation()

            print(f"""
            Total Records: {statistic_metrics.total_records}
            Unique DAU count: {statistic_metrics.unique_dau_count}
            Unique row count: {statistic_metrics.unique_row_count}
            20p DAU count: {statistic_metrics.dau_20p_count}
            Average pings per DAU: {statistic_metrics.avg_ping_per_dau}
            Median pings per DAU: {statistic_metrics.median_ping_per_dau}
            """)
            print("\n----------------------------------------------")

        if run_curation:
            curation_metrics = self.curation_evaluation()
            print("....")

        return statistic_metrics, curation_metrics