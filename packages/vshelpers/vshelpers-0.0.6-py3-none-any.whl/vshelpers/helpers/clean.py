"""Steps used to clean the initial dataframe before anaylsis and evaluation"""
from pyspark.sql import DataFrame

def remove_duplicates(df) -> DataFrame:
    """Removes duplicates on ad_id, utc_timestamp, and location"""
    deduped_df = df.dropDuplicates(["ad_id", "utc_timestamp", "longitude", "latitude", "provider_id"])
    return deduped_df