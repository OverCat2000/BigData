import os
import logging
from datetime import datetime, timedelta

import pandas as pd
from pyarrow import parquet as pq

from airflow.models.dag import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyDatasetOperator,
    BigQueryCreateExternalTableOperator,
)

from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator, GCSDeleteBucketOperator

from Scrapper import main

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET = os.getenv("GCP_GCS_BUCKET")
print(PROJECT_ID)
print(BUCKET)
DAG_ID = "my_dag"

#dataset_file = 'yellow_tripdata_2022-01.parquet'
#dataset_url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{dataset_file}'


# def transform_columns():
#     file = pq.ParquetFile(dataset_file)
#     table = file.read()
#     df = table.to_pandas()
#     #df = df.iloc[:, 0]
#     df.columns = [i.lower() for i in df.columns]
#     print(df.head(1))
#     rename_dict = {
#         "vendorid": "vender_id",
#         "tpep_pickup_datetime": "pickup_datetime",
#         "tpep_dropoff_datetime": "dropff_datetime",
#         "ratecodeid": "rate_code_id",
#         "pulocationid": "pickup_location_id",
#         "dolocationid": "dropoff_location_id",
#     }
#     df = df.rename(columns=rename_dict)
#     df.to_parquet(dataset_file, index=False)
    

def drop():
    data = pd.read_parquet(dataset_file)
    data.to_csv(dataset_csv, index=False, header=False)


default_args = {
    'owner': 'airflow',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

with DAG(
    DAG_ID,
    schedule_interval='@yearly',  # Runs once a year
    start_date=datetime(2007, 1, 1),  # Start date
    end_date=datetime(2022, 12, 31),  # End date
    catchup=True,
    tags=["mydag"],
    default_args=default_args,
    max_active_runs=1
) as dag:

    # Calculate the date 3 months behind the execution date
    #execution_date_3_months_ago = "{{ (execution_date - macros.timedelta(days=90)).strftime('%Y-%m') }}"
    year = "{{execution_date.year}}"
    # Use the calculated execution date in the dataset file name
    #dataset_file = f"yellow_tripdata_{execution_date_3_months_ago}.parquet"
    dataset_file = f"{year}.csv"
    #dataset_url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{dataset_file}'
    # Local Path
    path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
    # Bigquery dataset
    dataset_name = f"dataset_{DAG_ID}"
    # Bucket destination
    object_name = f"lepto/{dataset_file}"

    create_bucket = GCSCreateBucketOperator(
        task_id="create_bucket",
        bucket_name=BUCKET
    )

    create_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id="create_dataset",
        dataset_id =dataset_name
    )

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        #curl -X POST -H "Content-Type: application/json" -d '{"year": 2015}' http://localhost:5000/download-data --output 2015.csv

        bash_command=f"""curl -X POST -H "Content-Type: application/json" -d '{{"year": {year}}}' http://flask-app:5000/download-data --output {path_to_local_home}/{dataset_file}"""
    
    )

    # download_dataset_task = BashOperator(
    #     task_id="download_dataset_task",
    #     bash_command=f"curl -sSL {dataset_url} > {path_to_local_home}/{dataset_file}"
    # )


    # drop_task = PythonOperator(
    #     task_id="drop_columns",
    #     python_callable=drop
    # )

    local_to_gcs_taks = LocalFilesystemToGCSOperator(
        task_id="local_to_gcs_taks",
        src=f"{path_to_local_home}/{dataset_file}",
        dst=object_name,
        bucket=BUCKET,
        gcp_conn_id='google_cloud_default',
    )

    create_external_table = BigQueryCreateExternalTableOperator(
        task_id="create_external_table",
        destination_project_dataset_table=f"{dataset_name}.external_name5",
        bucket=BUCKET,
        source_objects=["bigquery/yellow_tripdata_*.parquet"],
        gcp_conn_id='google_cloud_default',
        schema_fields=[
            {"name": "VendorID", "type":"INTEGER", "mode":"REQUIRED"},
            {"name": "tpep_pickup_datetime", "type":"TIMESTAMP", "mode":"NULLABLE"},
            {"name": "tpep_dropoff_datetime", "type":"TIMESTAMP", "mode":"NULLABLE"},
            {"name": "passenger_count", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "trip_distance", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "RatecodeID", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "store_and_fwd_flag", "type":"STRING", "mode":"NULLABLE"},
            {"name": "PUlocationID", "type":"INTEGER", "mode":"NULLABLE"},
            {"name": "DOlocationID", "type":"INTEGER", "mode":"NULLABLE"},
            {"name": "payment_type", "type":"INTEGER", "mode":"NULLABLE"},
            {"name": "fare_amount", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "extra", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "mta_tax", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "tip_amount", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "tolls_amount", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "improvement_surcharge", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "total_amount", "type":"FLOAT", "mode":"NULLABLE"},
            {"name": "congestion_surcharge", "type":"FLOAT", "mode":"NULLABLE"},
        ],
        source_format="PARQUET"
    )


    create_bucket >> create_dataset >> download_dataset_task >> local_to_gcs_taks >> create_external_table

    # transform = PythonOperator(
    #     task_id="fix_columns",
    #     python_callable=transform_columns,
        # op_kwargs={
        #     "dataset_file": dataset_file,
        #     "dataset_file_in": dataset_file_in
        # },
    # )










