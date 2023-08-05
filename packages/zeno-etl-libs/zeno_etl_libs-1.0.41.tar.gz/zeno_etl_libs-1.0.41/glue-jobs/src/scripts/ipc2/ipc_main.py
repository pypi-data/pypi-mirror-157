"""Main Wrapper for IPC revamp"""

import sys

from nbformat import read
sys.path.append('../../../..')
# sys.path.insert(0,'/Users/tusharuike/ETL')

import argparse
from cProfile import run
from calendar import calendar
import os
import json
import time
from scipy.stats import norm
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from dateutil.tz import gettz
from ast import literal_eval

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB, PostGre
from zeno_etl_libs.django.api import Django
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.email.email import Email

from zeno_etl_libs.utils.ipc2_prev.config_ipc import (
    date_col,
    target_col,
    perc_noise,
    key_col,
    store_col,
    drug_col,
    run_ml_flag,
    runs_ts_flag,
    models,
    percentile_bucket_dict,
    local_testing,
    platform_prod,
    forecast_horizon
)

from zeno_etl_libs.utils.ipc2_prev.data_load import LoadData
from zeno_etl_libs.utils.ipc2_prev.data_pre_process import PreprocessData
from zeno_etl_libs.utils.ipc2_prev.segmentation import Segmentation
from zeno_etl_libs.utils.ipc2_prev.ts_fcst import TS_forecast
from zeno_etl_libs.utils.ipc2_prev.feat_engg import Feature_Engg
from zeno_etl_libs.utils.ipc2_prev.forecast import Forecast
from zeno_etl_libs.utils.ipc2_prev.helpers.helper_functions import list_to_sql
from zeno_etl_libs.utils.ipc2_prev.safety_stock import safety_stock_calc
from zeno_etl_libs.utils.ipc.goodaid_substitution import update_ga_ss
from zeno_etl_libs.utils.ipc.npi_exclusion import omit_npi_drugs
from zeno_etl_libs.utils.ipc.post_processing import post_processing
from zeno_etl_libs.utils.ipc.doid_update_ss import doid_update
from zeno_etl_libs.utils.ipc.lead_time import lead_time
from zeno_etl_libs.utils.warehouse.wh_intervention.store_portfolio_consolidation import stores_ss_consolidation



def main(debug_mode, reset_stores, reset_date, type_list, reset_store_ops,
         goodaid_ss_flag, ga_inv_weight, rest_inv_weight, top_inv_weight,
         chronic_max_flag, wh_gen_consolidation, v5_active_flag, v6_active_flag,
         v6_type_list, v6_ptr_cut_off, v3_active_flag,
         omit_npi, corrections_selling_probability_cutoff,
         corrections_cumulative_probability_cutoff, drug_type_list_v4,
         rs_db_read, rs_db_write, read_schema, write_schema, s3, django, logger):

    logger.info(f"Debug Mode: {debug_mode}")
    status = 'Failed'
    if v3_active_flag == 'Y':
        corrections_flag = True
    else:
        corrections_flag = False

    # Define empty DF if required in case of fail
    order_value_all = pd.DataFrame()
    new_drug_entries = pd.DataFrame()
    missed_entries = pd.DataFrame()
    final_forecast_df = pd.DataFrame()




    try:
        for store_id in reset_stores:
            weekly_fcst = pd.DataFrame()
            ml_fc_cols = []
            ts_fcst_cols = []
            fc_cols = []

            store = ("({})").format(store_id)
            reset_date = str(reset_date)
            logger.info('Running fcst pipeline for store {} and reset date {}'.format(store, reset_date))


            last_date = dt.date(day=1, month=4, year=2019)
            

            logger.info("Data Loading Started...")
            data_load_obj = LoadData()

            (
                drug_list,
                sales_history,
                cfr_pr,
                calendar,
                first_bill_date
            ) = data_load_obj.load_all_input(
                type_list = type_list,
                store_id_list= store,
                last_date= last_date,
                reset_date = reset_date,
                schema = read_schema,
                db = rs_db_read
            )

            logger.info("Data Pre Processing Started...")
            data_prep_obj = PreprocessData()

            (   
                sales,
                sales_pred,
                cal_sales,
                sales_daily
            ) = data_prep_obj.preprocess_all(
                sales = sales_history, 
                drug_list= drug_list,
                cfr_pr= cfr_pr, 
                calendar= calendar, 
                first_bill_date= first_bill_date,
                last_date = last_date
            )

            train_max_date = sales[date_col].max()
            end_date = sales_pred[date_col].max()

            logger.info("Segmentation Started...")
            seg_obj = Segmentation()

            seg_df, drug_class = seg_obj.get_weekly_segmentation(
                df = sales.copy(deep = True),
                df_sales_daily= sales_daily.copy(deep=True),
                train_max_date = train_max_date,
                end_date = end_date
            )

            seg_df['reset_date'] = str(reset_date)

            merged_df1 = pd.merge(sales_pred, seg_df, how='left', on =['ts_id'])
            merged_df1 = merged_df1[merged_df1['PLC Status L1'].isin(['Mature','NPI'])]

            if runs_ts_flag==1:
                ts_fcst_obj = TS_forecast()
                # df_ts_fcst = applyParallel(merged_df1.groupby('ts_id'), func=TS_forecast.ts_forecast(df=merged_df1.copy(), train_max_date = train_max_date,forecast_start = train_max_date + relativedelta(weeks=2) ))
                ts_fcst, ts_fcst_cols = ts_fcst_obj.apply_ts_forecast(
                    df = merged_df1.copy(), 
                    train_max_date= train_max_date,
                    forecast_start = train_max_date + relativedelta(weeks=2))

            # ----------------------- Forecast for 1-4 weeks -----------------------------
            if run_ml_flag ==1:
                start_time = time.time()

                forecast_start = train_max_date + relativedelta(weeks=2)

                merged_df1['All'] = 'All'
                slice_col = 'All'
                forecast_volume = merged_df1[merged_df1[date_col] > train_max_date][target_col].sum()
                assert forecast_volume == 0
                logger.info(
                    "forecast start {} total volume: {}"
                    .format(forecast_start, forecast_volume)
                )

                forecast_df = pd.DataFrame()
                validation_df = pd.DataFrame()
                

                for i in range(1,5):

                    num_shift_lags = i + 1

                    # for group_name in merged_df1[slice_col].dropna.unique():
                    for group_name in ['All']:
                        logger.info('Group: {}'.format(group_name))
                        logger.info("Feature Engineering Started...")
                        feat_df = pd.DataFrame()
                        for one_df in [merged_df1]:
                            feat_engg_obj = Feature_Engg()
                            one_feat_df = feat_engg_obj.feat_agg(
                                one_df[
                                    one_df[slice_col] == group_name
                                ].drop(slice_col, axis = 1).copy(deep = True),
                                train_max_date= train_max_date,
                                num_shift_lag = num_shift_lags
                            )
                            feat_df = pd.concat([one_feat_df, feat_df])


                        if pd.DataFrame(feat_df).empty:
                            continue

                        logger.info("Forecasting Started for {}...".format(forecast_start))
                        forecast_obj = Forecast()
                        fcst_df, val_df, Feature_Imp_all = forecast_obj.get_STM_forecast(
                            feat_df.copy(deep = True),
                            forecast_start = forecast_start,
                            num_shift_lags = num_shift_lags
                        )
                        forecast_df = pd.concat([forecast_df, fcst_df], axis = 0)
                        validation_df = pd.concat([validation_df, val_df])
                        ml_fc_cols = [i for i in forecast_df.columns if i.startswith('preds_')]
                        forecast_df['AE'] = forecast_df[ml_fc_cols].mean(axis=1)

                    end_time = time.time()
                    logger.info(
                        "total time for {} forecast: {}"
                        .format(forecast_start, end_time - start_time)
                    )

                    forecast_start = forecast_start + relativedelta(weeks=1)
                
            
                    weekly_fcst = pd.concat([weekly_fcst, forecast_df])  
                    weekly_fcst['reset_date'] = reset_date
                
            if runs_ts_flag==0:
                weekly_fcst = weekly_fcst.copy(deep=True)
            if run_ml_flag ==0:
                weekly_fcst = ts_fcst.copy(deep=True)
                weekly_fcst['reset_date'] = reset_date
            if (run_ml_flag==1 & runs_ts_flag==1):
                weekly_fcst = pd.merge(weekly_fcst, ts_fcst[[key_col, date_col]+ ts_fcst_cols ], how='left', on = [key_col, date_col])
            
            weekly_fcst.drop_duplicates(inplace=True)
            weekly_fcst['model'] = 'LGBM'
            weekly_fcst[[store_col, drug_col]] = weekly_fcst[key_col].str.split('_', expand = True)
            weekly_fcst.rename(columns={'preds_lgb':'fcst'},inplace=True)
            # weekly_fcst.rename(columns={'preds_xgb_rf_target':'fcst'},inplace=True)
            weekly_fcst = pd.merge(weekly_fcst, seg_df[['ts_id', 'std', 'Mixed']], how='left', on = ['ts_id'])
            weekly_fcst.rename(columns={'Mixed':'bucket'},inplace=True)
            for key in percentile_bucket_dict.keys():
                print(key, percentile_bucket_dict[key])
                indexs = weekly_fcst[weekly_fcst.bucket == key].index
                weekly_fcst.loc[indexs, 'percentile'] = percentile_bucket_dict[key]
                weekly_fcst.loc[indexs, 'fcst'] = np.round(
                    weekly_fcst.loc[indexs, 'fcst'] +
                    norm.ppf(percentile_bucket_dict[key]) *
                    weekly_fcst.loc[indexs, 'std'])
            weekly_fcst = weekly_fcst[['store_id', 'drug_id', 'model','date', 'fcst', 'std', 'bucket','percentile']]

            fc_cols = [i for i in weekly_fcst.columns if i.startswith('preds_')]
            weekly_fcst['std'].fillna(seg_df['std'].mean(),inplace=True)
            # agg_fcst = weekly_fcst.groupby(
            # ['model', 'store_id', 'drug_id', 'bucket', 'percentile']).\
            # agg({'fcst': 'sum', 'std': sum_std}).reset_index()
            agg_fcst = weekly_fcst.groupby(
            ['model', 'store_id', 'drug_id', 'bucket', 'percentile']).\
            agg({'fcst': 'sum', 'std': 'mean'}).reset_index()

            final_forecast_df = pd.concat([final_forecast_df, agg_fcst])  


            '''LEAD TIME CALCULATION'''
            lt_drug, lt_store_mean, lt_store_std = lead_time(
                store_id, cal_sales, reset_date, rs_db_read, read_schema, logger)

            lt_drug['drug_id'] = lt_drug['drug_id'].astype(int)
            agg_fcst['drug_id'] = agg_fcst['drug_id'].astype(int)

            '''SAFETY STOCK CALCULATION'''
            safety_stock_df, df_corrections, df_corrections_111, \
            drugs_max_to_lock_ipcv6, drug_rejects_ipcv6 = safety_stock_calc(
                agg_fcst, store_id, forecast_horizon, lt_drug,
                lt_store_mean, lt_store_std, reset_date, corrections_flag,
                corrections_selling_probability_cutoff,
                corrections_cumulative_probability_cutoff, chronic_max_flag,
                v5_active_flag, v6_active_flag, v6_type_list,
                v6_ptr_cut_off, drug_type_list_v4, rs_db_read ,read_schema, logger)

            # WAREHOUSE GENERIC SKU CONSOLIDATION
            if wh_gen_consolidation == 'Y':
                safety_stock_df, consolidation_log = stores_ss_consolidation(
                    safety_stock_df, rs_db_read, read_schema,
                    min_column='safety_stock', ss_column='reorder_point',
                    max_column='order_upto_point')

            # GOODAID SAFETY STOCK MODIFICATION
            if goodaid_ss_flag == 'Y':
                safety_stock_df, good_aid_ss_log = update_ga_ss(
                    safety_stock_df, store_id, rs_db_read, read_schema,
                    ga_inv_weight, rest_inv_weight,
                    top_inv_weight, substition_type=['generic'],
                    min_column='safety_stock', ss_column='reorder_point',
                    max_column='order_upto_point', logger=logger)

            # OMIT NPI DRUGS
            if omit_npi == 'Y':
                safety_stock_df = omit_npi_drugs(safety_stock_df, store_id,
                                                 reset_date, rs_db_read,
                                                 read_schema, logger)

            safety_stock_df.drop(columns=['correction_flag'], inplace=True)
            safety_stock_df.rename(columns={'corrections': 'correction_flag'},
                                   inplace=True)
            drug_class['drug_id'] = drug_class['drug_id'].astype(int)

            # POST PROCESSING AND ORDER VALUE CALCULATION
            drug_class, weekly_fcst, safety_stock_df, \
                order_value = post_processing(store_id, drug_class, weekly_fcst,
                                              safety_stock_df, rs_db_read,
                                              read_schema,  logger)
            order_value_all = order_value_all.append(order_value, ignore_index=True)

            seg_df[[store_col, drug_col]] = seg_df['ts_id'].str.split('_', expand = True)
            seg_df.drop(columns=['ts_id'],inplace=True)
            seg_df.rename(columns={'std':'sales_std_dev', 'cov':'sales_cov', 'ABC':'bucket_abcd', 'WXYZ':'bucket_wxyz', 'Mixed':'bucket'}, inplace=True)
            seg_df['PLC Status L1'] = np.where(seg_df['PLC Status L1']=='NPI', 'New_Product', seg_df['PLC Status L1'])
            seg_df['start_date'] = seg_df['start_date'].astype(str)
            seg_df = seg_df[[store_col, drug_col,'PLC Status L1', 'total_LY_sales', 'bucket_abcd', 'bucket_wxyz', 'bucket', 'classification', 'Group', 'sales_std_dev', 'sales_cov', 'ADI', 'start_date' ]]
            seg_df[store_col] = seg_df[store_col].astype(int)
            seg_df[drug_col] = seg_df[drug_col].astype(int)
            seg_df = pd.merge(seg_df, drug_class[[store_col, 'store_name',  drug_col, 'drug_grade', 'type']], on = [store_col, drug_col])
            seg_df['reset_date'] = str(reset_date)

            # WRITING TO RS-DB
            if debug_mode == 'N':
                logger.info("Writing table to RS-DB")
                # writing table ipc-forecast
                weekly_fcst.rename(
                    columns={'date': 'week_begin_dt', 'fcst': 'weekly_forecast',
                             'std': 'forecast_deviation', 'forecast_date':'reset_date'}, inplace=True)
                weekly_fcst['store_id'] = weekly_fcst['store_id'].astype(int)
                weekly_fcst['drug_id'] = weekly_fcst['drug_id'].astype(int)
                weekly_fcst['forecast_date'] = dt.datetime.strptime(reset_date, '%Y-%m-%d').date()
                weekly_fcst['week_begin_dt'] = weekly_fcst['week_begin_dt']
                weekly_fcst['created-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                weekly_fcst['created-by'] = 'etl-automation'
                weekly_fcst['updated-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                weekly_fcst['updated-by'] = 'etl-automation'
                weekly_fcst.columns = [c.replace('_', '-') for c in weekly_fcst.columns]
                table_info = helper.get_table_info(db=rs_db_write,
                                                   table_name='ipc-forecast',
                                                   schema=write_schema)
                columns = list(table_info['column_name'])
                weekly_fcst = weekly_fcst[columns]  # required column order

                logger.info("Writing to table: ipc-forecast")
                s3.write_df_to_db(df=weekly_fcst,
                                  table_name='ipc-forecast',
                                  db=rs_db_write, schema=write_schema)

                # writing table ipc-safety-stock
                safety_stock_df['store_id'] = safety_stock_df['store_id'].astype(int)
                safety_stock_df['drug_id'] = safety_stock_df['drug_id'].astype(int)
                safety_stock_df['reset_date'] = dt.datetime.strptime(reset_date, '%Y-%m-%d').date()
                safety_stock_df['created-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                safety_stock_df['created-by'] = 'etl-automation'
                safety_stock_df['updated-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                safety_stock_df['updated-by'] = 'etl-automation'
                safety_stock_df.columns = [c.replace('_', '-') for c in safety_stock_df.columns]
                table_info = helper.get_table_info(db=rs_db_write,
                                                   table_name='ipc-safety-stock',
                                                   schema=write_schema)
                columns = list(table_info['column_name'])
                safety_stock_df = safety_stock_df[columns]  # required column order

                logger.info("Writing to table: ipc-safety-stock")
                s3.write_df_to_db(df=safety_stock_df,
                                  table_name='ipc-safety-stock',
                                  db=rs_db_write, schema=write_schema)

                # writing table ipc-abc-xyz-class
                drug_class['store_id'] = drug_class['store_id'].astype(int)
                drug_class['drug_id'] = drug_class['drug_id'].astype(int)
                drug_class['reset_date'] = dt.datetime.strptime(reset_date, '%Y-%m-%d').date()
                drug_class['created-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                drug_class['created-by'] = 'etl-automation'
                drug_class['updated-at'] = dt.datetime.now(
                    tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                drug_class['updated-by'] = 'etl-automation'
                drug_class.columns = [c.replace('_', '-') for c in drug_class.columns]
                table_info = helper.get_table_info(db=rs_db_write,
                                                  table_name='ipc-abc-xyz-class',
                                                  schema=write_schema)
                columns = list(table_info['column_name'])
                drug_class = drug_class[columns]  # required column order

                logger.info("Writing to table: ipc-abc-xyz-class")
                s3.write_df_to_db(df=drug_class,
                                  table_name='ipc-abc-xyz-class',
                                  db=rs_db_write, schema=write_schema)

                # to write ipc v6 tables ...

                # UPLOADING MIN, SS, MAX in DOI-D
                logger.info("Updating new SS to DrugOrderInfo-Data")
                safety_stock_df.columns = [c.replace('-', '_') for c in safety_stock_df.columns]
                ss_data_upload = safety_stock_df.query('order_upto_point > 0')[
                    ['store_id', 'drug_id', 'safety_stock', 'reorder_point',
                     'order_upto_point']]
                ss_data_upload.columns = ['store_id', 'drug_id', 'corr_min',
                                          'corr_ss', 'corr_max']
                new_drug_entries_str, missed_entries_str = doid_update(
                    ss_data_upload, type_list, rs_db_write, write_schema, logger)
                new_drug_entries = new_drug_entries.append(new_drug_entries_str)
                missed_entries = missed_entries.append(missed_entries_str)

                logger.info("All writes to RS-DB completed!")

                # INTERNAL TABLE SCHEDULE UPDATE - OPS ORACLE
                logger.info(f"Rescheduling SID:{store_id} in OPS ORACLE")
                if isinstance(reset_store_ops, pd.DataFrame):
                    content_type = 74
                    object_id = reset_store_ops.loc[
                        reset_store_ops['store_id'] == store_id, 'object_id'].unique()
                    for obj in object_id:
                        request_body = {"object_id": int(obj), "content_type": content_type}
                        api_response, _ = django.django_model_execution_log_create_api(
                            request_body)
                        reset_store_ops.loc[
                            reset_store_ops['object_id'] == obj,
                            'api_call_response'] = api_response

            else:
                logger.info("Writing to RS-DB skipped")

        status = 'Success'
        logger.info(f"IPC code execution status: {status}")

    except Exception as error:
        logger.exception(error)
        logger.info(f"IPC code execution status: {status}")

    return status, order_value_all, new_drug_entries, missed_entries


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False)
    parser.add_argument('-et', '--email_to',
                        default="tushar.uike@zeno.health", type=str,
                        required=False)

    parser.add_argument('-d', '--debug_mode', default="N", type=str,
                        required=False)
    parser.add_argument('-exsto', '--exclude_stores',
                        default=[52, 60, 92, 243, 281], nargs='+', type=int,
                        required=False)
    parser.add_argument('-gad', '--gaid_flag', default="Y", type=str,
                        required=False)
    parser.add_argument('-giw', '--gaid_inv_wt', default=0.5, type=float,
                        required=False)
    parser.add_argument('-riw', '--rest_inv_wt', default=0.0, type=float,
                        required=False)
    parser.add_argument('-tiw', '--top_inv_wt', default=1, type=float,
                        required=False)
    parser.add_argument('-cmf', '--chronic_max_flag', default="N", type=str,
                        required=False)
    parser.add_argument('-wgc', '--wh_gen_consld', default="Y", type=str,
                        required=False)
    parser.add_argument('-v5', '--v5_active_flag', default="N", type=str,
                        required=False)
    parser.add_argument('-v6', '--v6_active_flag', default="N", type=str,
                        required=False)
    parser.add_argument('-v6lst', '--v6_type_list',
                        default=['ethical', 'generic', 'others'], nargs='+',
                        type=str, required=False)
    parser.add_argument('-v6ptr', '--v6_ptr_cut_off', default=400, type=int,
                        required=False)
    parser.add_argument('-rd', '--reset_date', default="YYYY-MM-DD", type=str,
                        required=False)
    parser.add_argument('-rs', '--reset_stores',
                        default=[4], nargs='+', type=int,
                        required=False)
    parser.add_argument('-v3', '--v3_active_flag', default="N", type=str,
                        required=False)
    parser.add_argument('-v3sp', '--corr_selling_prob_cutoff',
                        default="{'ma_less_than_2': 0.40, 'ma_more_than_2' : 0.40}",
                        type=str, required=False)
    parser.add_argument('-v3cp', '--corr_cumm_prob_cutoff',
                        default="{'ma_less_than_2':0.50,'ma_more_than_2':0.63}",
                        type=str, required=False)
    parser.add_argument('-v4tl', '--v4_drug_type_list',
                        default="{'generic':'{0:[0,0,0], 1:[0,0,1], 2:[0,1,2],3:[1,2,3]}',"
                                "'ethical':'{0:[0,0,0], 1:[0,0,1], 2:[0,1,2],3:[1,2,3]}',"
                                "'others':'{0:[0,0,0], 1:[0,1,2], 2:[0,1,2],3:[1,2,3]}'}",
                        type=str, required=False)
    parser.add_argument('-npi', '--omit_npi', default='N', type=str,
                        required=False)

    args, unknown = parser.parse_known_args()

    env = args.env
    os.environ['env'] = env
    email_to = args.email_to
    debug_mode = args.debug_mode

    # JOB EXCLUSIVE PARAMS
    exclude_stores = args.exclude_stores
    goodaid_ss_flag = args.gaid_flag
    ga_inv_weight = args.gaid_inv_wt
    rest_inv_weight = args.rest_inv_wt
    top_inv_weight = args.rest_inv_wt
    chronic_max_flag = args.chronic_max_flag
    wh_gen_consolidation = args.wh_gen_consld
    v5_active_flag = args.v5_active_flag
    v6_active_flag = args.v6_active_flag
    v6_type_list = args.v6_type_list
    v6_ptr_cut_off = args.v6_ptr_cut_off
    reset_date = args.reset_date
    reset_stores = args.reset_stores
    v3_active_flag = args.v3_active_flag
    corrections_selling_probability_cutoff = args.corr_selling_prob_cutoff
    corrections_cumulative_probability_cutoff = args.corr_cumm_prob_cutoff
    drug_type_list_v4 = args.v4_drug_type_list
    omit_npi = args.omit_npi

    # EVALUATE REQUIRED JSON PARAMS
    corrections_selling_probability_cutoff = literal_eval(
        corrections_selling_probability_cutoff)
    corrections_cumulative_probability_cutoff = literal_eval(
        corrections_cumulative_probability_cutoff)
    drug_type_list_v4 = literal_eval(drug_type_list_v4)

    logger = get_logger()
    s3 = S3()
    django = Django()
    rs_db_read = DB(read_only=True)
    rs_db_write = DB(read_only=False)
    read_schema = 'prod2-generico'
    write_schema = 'prod2-generico'

    # open RS connection
    rs_db_read.open_connection()
    rs_db_write.open_connection()

    if reset_date == 'YYYY-MM-DD':  # Take current date
        reset_date = dt.date.today().strftime("%Y-%m-%d")

    if reset_stores == [0]:  # Fetch scheduled IPC stores from OPS ORACLE
        store_query = """
            select "id", name, "opened-at" as opened_at
            from "{read_schema}".stores
            where name <> 'Zippin Central'
            and "is-active" = 1
            and "opened-at" != '0101-01-01 00:00:00'
            and id not in {0}
            """.format(str(exclude_stores).replace('[', '(').replace(']', ')'),
                       read_schema=read_schema)
        stores = rs_db_read.get_df(store_query)
        # considering reset of old stores only (age > 1 year)
        store_id = stores.loc[dt.datetime.now() -
                              stores['opened_at'] >
                              dt.timedelta(days=365), 'id'].values

        # QUERY TO GET SCHEDULED STORES AND TYPE FROM OPS ORACLE
        pg_internal = PostGre(is_internal=True)
        pg_internal.open_connection()
        reset_store_query = """
            SELECT
                "ssr"."id" as object_id,
                "s"."bpos_store_id" as store_id,
                "dc"."slug" as type,
                "ssr"."drug_grade"
            FROM
                "safety_stock_reset_drug_category_mapping" ssr
                INNER JOIN "ops_store_manifest" osm
                ON ( "ssr"."ops_store_manifest_id" = "osm"."id" )
                INNER JOIN "retail_store" s
                ON ( "osm"."store_id" = "s"."id" )
                INNER JOIN "drug_category" dc
                ON ( "ssr"."drug_category_id" = "dc"."id")
            WHERE
                (
                    ( "ssr"."should_run_daily" = TRUE OR
                        "ssr"."trigger_dates" && ARRAY[ date('{reset_date}')] )
                    AND "ssr"."is_auto_generate" = TRUE
                    AND "osm"."is_active" = TRUE
                AND "osm"."is_generate_safety_stock_reset" = TRUE
                AND "dc"."is_safety_stock_reset_enabled" = TRUE
                AND "dc"."is_active" = TRUE
                AND s.bpos_store_id in {store_list}
                )
            """.format(
            store_list=str(list(store_id)).replace('[', '(').replace(']', ')'),
            reset_date=reset_date)
        reset_store_ops = pd.read_sql_query(reset_store_query,
                                            pg_internal.connection)
        pg_internal.close_connection()

        reset_store_ops['api_call_response'] = False
        reset_stores = reset_store_ops['store_id'].unique()
        type_list = None

    else:
        type_list = "('ethical', 'ayurvedic', 'generic', 'discontinued-products', " \
                    "'banned', 'general', 'high-value-ethical', 'baby-product'," \
                    " 'surgical', 'otc', 'glucose-test-kit', 'category-2', " \
                    "'category-1', 'category-4', 'baby-food', '', 'category-3')"
        reset_store_ops = None

    """ calling the main function """
    status, order_value_all, new_drug_entries, \
        missed_entries = main(
            debug_mode, reset_stores, reset_date, type_list, reset_store_ops,
            goodaid_ss_flag, ga_inv_weight, rest_inv_weight, top_inv_weight,
            chronic_max_flag, wh_gen_consolidation, v5_active_flag,
            v6_active_flag, v6_type_list, v6_ptr_cut_off, v3_active_flag,
            omit_npi, corrections_selling_probability_cutoff,
            corrections_cumulative_probability_cutoff, drug_type_list_v4,
            rs_db_read, rs_db_write, read_schema, write_schema, s3, django, logger)

    # close RS connection
    rs_db_read.close_connection()
    rs_db_write.close_connection()

    # save email attachements to s3
    order_value_all_uri = s3.save_df_to_s3(order_value_all,
                                           file_name=f"order_value_all_{reset_date}.csv")
    new_drug_entries_uri = s3.save_df_to_s3(new_drug_entries,
                                            file_name=f"new_drug_entries_{reset_date}.csv")
    missed_entries_uri = s3.save_df_to_s3(missed_entries,
                                          file_name=f"missed_entries_{reset_date}.csv")

    # SEND EMAIL ATTACHMENTS
    logger.info("Sending email attachments..")
    email = Email()
    email.send_email_file(
        subject=f"IPC SS Reset (SM-{env}) {reset_date}: {status}",
        mail_body=f"""
                Debug Mode: {debug_mode}
                Reset Stores: {reset_stores}
                Job Params: {args}
                """,
        to_emails=email_to, file_uris=[order_value_all_uri,
                                       new_drug_entries_uri,
                                       missed_entries_uri])

    logger.info("Script ended")