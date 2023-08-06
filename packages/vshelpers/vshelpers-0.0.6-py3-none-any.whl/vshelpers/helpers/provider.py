"""Provider specific transformations on the dataframe"""
from pyspark.sql.functions import collect_set, size
from pyspark.sql import DataFrame


def count_provider_daus(df, provider_id) -> int:
    """Counts total number of unique DAUs (ad_id) for a provider"""
    filtered_provider = df.where(df.provider_id == provider_id)
    dau_count = filtered_provider.dropDuplicates(["ad_id"]).count()

    return dau_count

def count_provider_rows(df, provider_id) -> int:
    """Counts total number of unique rows (ad_id, utc_timestamp) for a provider"""
    filtered_provider = df.where(df.provider_id == provider_id)
    row_count = filtered_provider.dropDuplicates(["ad_id", "utc_timestamp"]).count()
    
    return row_count

def collect_provider_set_dau(df) -> DataFrame:
    """Creates a column of of providers that share the same DAUs (ad_id)"""
    shared_dau_provider_set_df  = (df
                                    .groupBy(df.ad_id)
                                    .agg(collect_set("provider_id").alias("provider_ids"))
                                    .where(size("provider_ids") > 1))
    return shared_dau_provider_set_df 

def collect_provider_set_row(df) -> DataFrame:
    """Creates a column of of providers that share the same rows (ad_id, utc_timestamp)"""
    shared_row_provider_set_df  = (df
                                    .groupBy(df.ad_id, df.utc_timestamp)
                                    .agg(collect_set("provider_id").alias("provider_ids"))
                                    .where(size("provider_ids") > 1))

    return shared_row_provider_set_df

def extract_providers(df, provider_ids) -> DataFrame:
    """Extracts provider_ids from dataframe"""
    extracted_providers = df.where(df.provider_id.isin(provider_ids))
    return extracted_providers