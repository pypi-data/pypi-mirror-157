import argparse
import os
import sys
from io import StringIO

import pandas as pd

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()
logger.info(f"info message")

reviews = pd.DataFrame()
s3 = S3()
last_month = 6
for year in (21, 22):
    for month in range(1, 12):
        if month > last_month and year == 22:
            """ stopping """
            break

        uri = f"s3://aws-glue-temporary-921939243643-ap-south-1/playstore-reviews/reviews_reviews_com.zenohealth.android_20{year}{str(month).zfill(2)}.csv"
        logger.info(f"uri: {uri}")
        csv_string = s3.get_file_object(uri=uri, encoding="utf-16")
        df = pd.read_csv(StringIO(csv_string))
        reviews = pd.concat([reviews, df], ignore_index=True)

columns = [c.replace(" ", "-").lower() for c in reviews.columns]
reviews.columns = columns

logger.info(f"all reviews: {reviews}")
