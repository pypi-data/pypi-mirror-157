"""Statistical analysis steps"""
import math
from pyspark.sql.functions import col, udf, mean, percentile_approx
from pyspark.sql.types import IntegerType
from helpers.general import unique_dau_filter, unique_row_filter

def total_records(df) -> int:
    """Counts total number of records"""
    return df.count()

def unique_dau_count(df) -> int:
    """Counts total number of unique DAUs for provider - ad_id"""
    unqiue_dau_count = unique_dau_filter(df).count()
    return unqiue_dau_count

def unqiue_row_count(df) -> int:
    """Counts total number of unique DAUs for provider - ad_id"""
    unqiue_row_count = unique_row_filter(df).count()
    return unqiue_row_count

def priority_point_count(df) -> int:
    """Calculates total count of DAUs that are considered to be a 'priority point'.
    Priority Point: DAU doesn't only appear in a twelve-hour window and has more than fifty pings within a twenty-four-hour period.
    """
    df.createOrReplaceTempView("df")
    q = """SELECT 
             ad_id, 
             COUNT(DISTINCT(utc_timestamp, longitude, latitude)) AS unique_ping_count, 
             collect_set(hour) as hours_pings_appear
           FROM (
             SELECT 
               ad_id, 
               longitude, 
               latitude, 
               utc_timestamp, 
               RIGHT(LEFT(FROM_UNIXTIME(utc_timestamp::bigint), 13),2) as hour
             FROM df
          )
          GROUP BY ad_id
          HAVING unique_ping_count > 50"""
    df_with_hours = spark.sql(q)


    def day_time_span_labeling(s):
        if len(s) >= 12:
            return 1
        else:
            return 0

    day_time_span_labeling = udf(day_time_span_labeling, IntegerType())
    priority_point_count = df_with_hours.select("ad_id", day_time_span_labeling("hours_pings_appear").alias("is_priority_point")).agg(sum("is_priority_point"))

    return priority_point_count

def twenty_point_dau_count(ping_counts_df) -> int:
    """Takes a ping counts dataframe and calculates total number of DAUs with more than 20 pings."""
    dau_twenty_point_count = ping_counts_df.where(col("ping_counts") > 20).count()
    return dau_twenty_point_count

def average_pings_per_dau(ping_counts_df) -> int:
    """The average number of pings for a DAU."""
    average_ping_per_dau = ping_counts_df.select(mean("ping_counts").alias("average_ping_counts")).collect()[0][0]
    return average_ping_per_dau

def median_pings_per_dau(ping_counts_df) -> int:
    """The median number of pings for a DAU."""
    median_ping_per_dau = ping_counts_df.select(percentile_approx("ping_counts", 0.5).alias("median_ping_counts")).collect()[0][0]
    return median_ping_per_dau