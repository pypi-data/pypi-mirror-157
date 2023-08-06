import boto3
import sys
import os
import argparse
import json
sys.path.append('../../../..')
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.logger import get_logger

client = boto3.client('glue')

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-jn', '--job_name', default="", type=str, required=False)
args, unknown = parser.parse_known_args()
env = args.env
job_name = args.job_name
os.environ['env'] = env

logger = get_logger()
db = DB()

query = """select job_id from "prod2-generico"."audit-log" where "job-name" = {};""".format(job_name)
df_init = db.get_df(query)
max_store_id = df_init.values[0][0]

response = client.get_job_runs(
    JobName='prod-91-drug-daily-backup'
)

print(response)