"""General dataframe transformations"""
from pyspark.sql.functions import count
from pyspark.sql import DataFrame


def unique_dau_filter(df) -> DataFrame:
    """Dropping any duplicate daus (ad_id)"""
    unqiue_dau_df = df.dropDuplicates(["ad_id"])
    return unqiue_dau_df

def unique_row_filter(df) -> DataFrame:
    """Dropping any duplicate rows (ad_id, utc_timestamp)"""
    unqiue_row_df = df.dropDuplicates(["ad_id", "utc_timestamp"])
    return unqiue_row_df

def ping_counts(df) -> DataFrame:
    """Creates a dataframe with the total number of unqiue row counts for each DAU"""
    unqiue_row_df = unique_row_filter(df)
    ping_counts_df =  unqiue_row_df.groupBy(unqiue_row_df.ad_id).agg(count("*").alias("ping_counts"))
    return ping_counts_df