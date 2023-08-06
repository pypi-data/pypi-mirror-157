"""Overlap evaluations"""
from pyspark.sql.functions import col, collect_set, expr, explode, array_distinct, arrays_zip, size, array_contains

from helpers.provider import collect_provider_set_dau, collect_provider_set_row, extract_providers


def all_provider_dau_overlaps(df) -> dict:
    """Creates a dictionary for all providers with the total count of DAUs that are shared with the whole dataframe.
    
    The key is the provider ID and the value is count of shared DAUs.
    """
    overlap_dau = (df
                  .groupBy(df.ad_id)
                  .agg(collect_set("provider_id").alias("provider_ids")))
    
    collected_dau = (overlap_dau.withColumn("atr", expr("""transform(array_distinct(provider_ids),x->aggregate(provider_ids,0,(acc,y)->\
                                     IF(y=x, acc+1,acc)))"""))
                          .withColumn("zip", explode(arrays_zip(array_distinct("provider_ids"),("atr"))))
                          .select("zip.*").withColumnRenamed("0","elements")
                          .groupBy("elements").agg(sum("atr").alias("sum")).collect())
    
    overlap_counts_dau = {collected_dau[i][0]: collected_dau[i][1] for i in range(len(collected_dau))} 
    
    return overlap_counts_dau

def all_provider_row_overlaps(df) -> dict:
    """Creates a dictionary for all providers with the total count of rows that are shared with the whole dataframe.
    
    The key is the provider ID and the value is count of shared rows.
    """
    overlap_row = (df
                    .groupBy(df.ad_id, df.utc_timestamp)
                    .agg(collect_set("provider_id").alias("provider_ids")))

    collected_row = (overlap_row.withColumn("atr", expr("""transform(array_distinct(provider_ids),x->aggregate(provider_ids,0,(acc,y)->\
                                    IF(y=x, acc+1,acc)))"""))
                            .withColumn("zip", explode(arrays_zip(array_distinct("provider_ids"),("atr"))))
                            .select("zip.*").withColumnRenamed("0","elements")
                            .groupBy("elements").agg(sum("atr").alias("sum")).collect())


    overlap_counts_row = {collected_row[i][0]: collected_row[i][1] for i in range(len(collected_row))} 

    return overlap_counts_row

def provider_dau_overlap(df, provider_id) -> int:
    """Counts number of shared DAUs the provider_id has with the whole dataframe."""
    shared_dau_provider_set_df = collect_provider_set_dau(df)
    contains_provider = shared_dau_provider_set_df.where(array_contains(col("provider_ids"), provider_id))
    provider_shared_dau_count = contains_provider.count()
    return provider_shared_dau_count

def provider_row_overlap(df, provider_id) -> int:
    """Counts number of shared rows the provider_id has with the whole dataframe."""
    shared_row_provider_set_df = collect_provider_set_row(df)
    contains_provider = shared_row_provider_set_df.where(array_contains(col("provider_ids"), provider_id))
    provider_shared_row_count = contains_provider.count()
    return provider_shared_row_count

def provider_provider_dau_overlap(df, provider_id_1, provider_id_2) -> int:
    """Counts how many DAUs from provider 1 are shared with provider 2"""
    extracted_providers = extract_providers([provider_id_1, provider_id_2])
    provider_shared_dau_count = provider_dau_overlap(extracted_providers, provider_id_1)
    return provider_shared_dau_count

def provider_provider_row_overlap(df, provider_id_1, provider_id_2) -> int:
    """Counts how many rows from provider 1 are shared with provider 2"""
    extracted_providers = extract_providers([provider_id_1, provider_id_2])
    provider_shared_row_count = provider_row_overlap(extracted_providers, provider_id_1)
    return provider_shared_row_count



