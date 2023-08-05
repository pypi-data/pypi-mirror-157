"""Main Wrapper for IPC revamp"""

from asyncio.log import logger
from cProfile import run
from calendar import calendar
import os
import json
import time
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

import sys
sys.path.insert(0,'/Users/tusharuike/generico-analytics-flask/project')

from ast import literal_eval
from scripts.ops.ipc.forecasting_modules.helper_functions import sum_std,\
    applyParallel, applyParallel_lstm

from application import current_config, config_name
from application.utils.script_manager import ScriptManager
from application.utils.task_actions import send_email_file
from scripts.ops.ipc.forecast_reset import ipc_forecast_reset
from scripts.ops.safety_stock.mysql_update_ss import mysql_doi_update
from scripts.ops.safety_stock.omit_drug_reset import omit_drug_reset
from scripts.ops.ipc.post_processing import post_processing
from scripts.ops.ipc.good_aid_substituion import update_ga_ss
from scripts.ops.warehouse.wh_intervention.\
    store_portfolio_consolidation import stores_ss_consolidation
from application.utils.\
    helper_modules import django_model_execution_log_create_api
from scripts.ops.ipc.forecasting_modules.helper_functions import list_to_sql
from scripts.ops.dev_ipc_revamp.ipc.config_ipc import platform_prod
from scripts.ops.dev_ipc_revamp.ipc.data_load import LoadData
from scripts.ops.dev_ipc_revamp.ipc.data_pre_process import PreprocessData
from scripts.ops.dev_ipc_revamp.ipc.segmentation import Segmentation
from scripts.ops.dev_ipc_revamp.ipc.feat_engg import Feature_Engg
from scripts.ops.dev_ipc_revamp.ipc.forecast import Forecast
from scripts.ops.dev_ipc_revamp.ipc.ts_fcst import TS_forecast

from scripts.ops.dev_ipc_revamp.ipc.config_ipc import (
    date_col,
    target_col,
    perc_noise,
    key_col,
    store_col,
    drug_col,
    run_ml_flag,
    runs_ts_flag,
    models
)


def ipc_backtesting(store_id_list, reset_date_list, logger):
    # Write these lines in start of every script
    script_manager_obj = ScriptManager(95, 'ipc-forecast-reset')
    output_dir_path = script_manager_obj.temp_dir_output_data_path
    job_data_params = script_manager_obj.job_data_params
    actions_list = script_manager_obj.actions_list
    logger = script_manager_obj.logger_obj

    # Start
    logger.info('Script Manager Initialized')
    logger.info('Data params: ' + json.dumps(job_data_params))
    logger.info('Actions list' + json.dumps(actions_list))
    debug_mode = str(job_data_params['debug_mode'])
    print('Debug mode ', debug_mode)
    exclude_stores = job_data_params["exclude_stores"]

    # Goodaid runtime parameters
    goodaid_ss_flag = job_data_params['goodaid_ss_flag']
    ga_inv_weight = float(job_data_params['ga_inv_weight'])
    rest_inv_weight = float(job_data_params['rest_inv_weight'])
    top_inv_weight = float(job_data_params['top_inv_weight'])

    # getting schema name for writing
    if (config_name == 'production_ipc') & (debug_mode == 'N'):
        schema_name = 'public'
    elif config_name == 'staging_ipc':
        schema_name = 'public'
    else:
        schema_name = 'test'

    status = 'Failed'
    chronic_max_flag = job_data_params['chronic_max_flag']
    wh_gen_consolidation = job_data_params['wh_gen_consolidation']
    v5_active_flag = job_data_params['v5_active_flag']
    v6_active_flag = job_data_params['v6_active_flag']
    v6_type_list = job_data_params['v6_type_list']
    v6_ptr_cut_off = job_data_params['v6_ptr_cut_off']

    # try:
    #     reset_date = str(job_data_params['reset_date'])
    # except KeyError:
    #     reset_date = '2022-01-20'

    try:
        corrections_flag = literal_eval(job_data_params['corrections_flag'])
        corrections_selling_probability_cutoff = literal_eval(
            job_data_params['corrections_selling_probability_cutoff'])
        corrections_cumulative_probability_cutoff = literal_eval(
            job_data_params['corrections_cumulative_probability_cutoff'])
    except:
        corrections_flag = False
        corrections_selling_probability_cutoff = {
            'ma_less_than_2': 0.99, 'ma_more_than_2': 0.99}
        corrections_cumulative_probability_cutoff = {
            'ma_less_than_2': 0.99, 'ma_more_than_2': 0.99}

    print('Corrections Flag: ', corrections_flag)
    print('cumulative probability corrections cutoff are: ',
          corrections_cumulative_probability_cutoff)
    print('selling probability corrections cutoff are: ',
          corrections_selling_probability_cutoff)

    connection = current_config.mysql_conn()
    store_query = '''select `id`, name, `opened-at` as opened_at
    from stores
    where `name` <> 'Zippin Central'
    and `is-active` = 1
    and `opened-at` != '0000-00-00 00:00:00'
    and `id` not in {0}
    '''.format(list_to_sql(exclude_stores))
    stores = pd.read_sql_query(store_query, connection)
    # considering reset of old stores only
    store_id = stores.loc[
        datetime.datetime.now() - stores['opened_at'] > datetime.timedelta(days=365),
        'id'
    ].values
    connection.close()

    order_value_all = pd.DataFrame()
    new_drug_entries = pd.DataFrame()
    missed_entries = pd.DataFrame()

    engine = current_config.data_science_postgresql_write_engine()

    drug_type_list_v4 = literal_eval(job_data_params['drug_type_list_v4'])

    type_list = "('ethical', 'ayurvedic', 'generic', 'discontinued-products', 'banned', 'general', 'high-value-ethical', 'baby-product', 'surgical', 'otc', 'glucose-test-kit', 'category-2', 'category-1', 'category-4', 'baby-food', '', 'category-3')"

    count = 0 
    final_forecast_df = pd.DataFrame()
    for store_id in store_id_list:
        all_forecast_df = pd.DataFrame()
        ml_fc_cols = []
        ts_fcst_cols = []
        fc_cols = []

        store = ("({})").format(store_id)
        reset_date = str(reset_date_list[count])
        count += 1
        logger.info('Running fcst pipeline for store {} and reset date {}'.format(store, reset_date))


        last_date = datetime.date(day=1, month=4, year=2019)
        

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
            reset_date = reset_date
        )

        logger.info("Data Pre Processing Started...")
        data_prep_obj = PreprocessData()

        (   
            sales,
            sales_pred,
            cal_sales,
            sales_daily              
        )     = data_prep_obj.preprocess_all(
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


        # logger.info("Feature Engineering Started...")
        # feat_obj = Feature_Engg()

        # df_feat = feat_obj.feat_agg(
        #     df = sales_pred.copy(deep=True), 
        #     train_max_date= train_max_date,
        #     num_shift_lag=1
        # ) 

        merged_df1 = pd.merge(sales_pred, seg_df, how='left', on ='ts_id')
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

                    # assert np.all(
                    #     (
                    #         feat_df[
                    #             feat_df[date_col]<=train_max_date][[date_col, 'ts_id']
                    #         ]
                    #         .value_counts()
                    #         .unique()
                    #     ) == len(perc_noise)*2+1
                    # )

                    # assert np.all(
                    #     (
                    #         feat_df[
                    #             feat_df[date_col]>train_max_date][[date_col, 'ts_id']
                    #         ]
                    #         .value_counts()
                    #         .unique()
                    #     ) == 1
                    # )

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
            
        
                all_forecast_df = pd.concat([all_forecast_df, forecast_df])  
                all_forecast_df['reset_date'] = reset_date
            
        if runs_ts_flag==0:
            all_forecast_df = all_forecast_df.copy(deep=True)
        if run_ml_flag ==0:
            all_forecast_df = ts_fcst.copy(deep=True)
            all_forecast_df['reset_date'] = reset_date
        if (run_ml_flag==1 & runs_ts_flag==1):
            all_forecast_df = pd.merge(all_forecast_df, ts_fcst[[key_col, date_col]+ ts_fcst_cols ], how='left', on = [key_col, date_col])
        
        all_forecast_df.drop_duplicates(inplace=True)
        fc_cols = [i for i in all_forecast_df.columns if i.startswith('preds_')]
        all_forecast_df= all_forecast_df.groupby([key_col,'reset_date'])[fc_cols].sum().reset_index()
        all_forecast_df = pd.merge(all_forecast_df, seg_df, how='left', on = 'ts_id')
        final_forecast_df = pd.concat([final_forecast_df, all_forecast_df])  

    
    # final_forecast_df = final_forecast_df.groupby([key_col,'reset_date'])[fc_cols].sum().reset_index()
    final_forecast_df[[store_col, drug_col]] = final_forecast_df[key_col].str.split('_', expand = True)
    final_forecast_df[[store_col, drug_col]] = final_forecast_df[[store_col, drug_col]].astype(int)
    # final_forecast_df.rename(columns= cols_rename, inplace=True)
    count = 0
    model_rename = {}
    for col in fc_cols:
        count +=1
        final_forecast_df.rename(columns={str(col):"fcst_"+str(count)},inplace=True)
        model_rename["fcst_"+str(count)] = str(col)
    final_forecast_df.drop(columns=[key_col],inplace=True)
    final_forecast_df = final_forecast_df.round()

    # return sales,sales_pred, seg_df, df_feat, final_forecast_df
    return final_forecast_df, model_rename

# sales,sales_pred, seg_df, df_feat, final_forecast_df = ipc_backtesting(store_id_list=[188, 188], reset_date_list=[datetime.date(2021, 8, 25), datetime.date(2021, 10, 27)], logger=logger)


