import argparse
import datetime
import sys
import os
import boto3
import time

from zeno_etl_libs.helper import helper

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email
from zeno_etl_libs.db.db import DB

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-ss', '--schema_name', default="", type=str, required=False)
parser.add_argument('-d', '--date_prefix', default="NA", type=str, required=False)
parser.add_argument('-lt', '--list_of_tables', default=None, type=str, required=False)
parser.add_argument('-et', '--email_to', default="kuldeep.singh@zeno.health", type=str, required=False)
parser.add_argument('-rc', '--reason_code', default="NA", type=str, required=False)
parser.add_argument('-ndo', '--n_day_old', default="NA", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

logger = get_logger()
logger.info(f"env: {env}")

schema_name = args.schema_name
list_of_tables = args.list_of_tables
email_to = args.email_to
reason_code = args.reason_code
date_prefix = args.date_prefix
n_day_old = args.n_day_old

logger.info(f"schema_name: {schema_name}")
logger.info(f"list_of_tables: {list_of_tables}")
logger.info(f"email_to: {email_to}")
logger.info(f"reason_code: {reason_code}")
logger.info(f"date_prefix: {date_prefix}")
logger.info(f"n_day_old: {n_day_old}")

if not schema_name:
    raise Exception("Please provide schema name !!!")

if not list_of_tables:
    raise Exception("Please provide list of tables")

if date_prefix == "NA":
    """ since glue gives error while passing empty string so, NA is used for empty string """
    date_prefix = ""

""" n_day_old: n day old tables to be deleted  """
if n_day_old and n_day_old != "NA":
    n_day_old = int(n_day_old)
    old_date = datetime.datetime.now() + datetime.timedelta(days=-n_day_old)
    date_prefix = old_date.strftime("%Y-%m-%d")

if reason_code == "NA":
    """ since glue gives error while passing empty string so, NA is used for empty string """
    reason_code = ""

list_of_tables = list_of_tables.split(",")

email = Email()

rs_db = DB(read_only=False)
rs_db.open_connection()

for i in list_of_tables:
    logger.info(f"started dropping table: {i}")
    new_table_name = i
    if reason_code:
        new_table_name += f"-{reason_code}"
    if date_prefix:
        new_table_name += f"-{date_prefix}"

    table_info = helper.get_table_info(db=rs_db, table_name=new_table_name, schema=schema_name)
    if isinstance(table_info, type(None)):
        logger.info(f"Table: {new_table_name} is absent, not need to drop.")
    else:
        logger.info(f"Table exists: {new_table_name}, so needs to drop.")
        q = f"""
            drop table "{schema_name}"."{new_table_name}";
        """
        rs_db.execute(query=q)

        logger.info(f"table dropped successfully: {new_table_name}")
