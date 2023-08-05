from google.cloud import storage
from airflow.models import Variable
from datetime import datetime
import os


def load_gcs(project=None,
             database=None,
             table=None,
             gcs_bucket=None,
             processed=False):

    curr_date = datetime.now().strftime('%Y-%m-%d')
    data_folder = Variable.get('data_folder')
    data_path = f'{data_folder}/{database}/{table}'

    client = storage.Client(project=project)
    bucket = client.get_bucket(gcs_bucket)

    if processed:
        filename = f'{table}-extract-{curr_date}-processed.parquet'

        for file in os.listdir(f'{data_path}/{filename}'):
            blob = bucket.blob(
                f'processed/{database}/{table}/{filename}/{file}')
            blob.upload_from_filename(
                filename=f'{data_path}/{filename}/{file}')

    else:
        filename = f'{table}-extract-{curr_date}.csv'

        blob = bucket.blob(f'raw/{database}/{table}/{filename}')
        blob.upload_from_filename(filename=f'{data_path}/{filename}')
