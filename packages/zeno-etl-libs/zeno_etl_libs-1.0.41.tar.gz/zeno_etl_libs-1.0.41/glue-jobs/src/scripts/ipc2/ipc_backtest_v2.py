"""wrapper for backtesting IPC model performace """
import os
import json

import sys
sys.path.insert(0,'/Users/tusharuike/generico-analytics-flask/project')

from scripts.ops.dev_ipc_revamp.ipc.config_ipc import local_testing
import pandas as pd
import numpy as np
import datetime as dt
from application.utils.script_manager import ScriptManager
from application import current_config, config_name
from application.utils.task_actions import send_email_file
from scripts.ops.dev_ipc_revamp import ipc_main_backtesting
import psycopg2 as pg

# ========================== DEFINE LEVELS HERE ==========================
levels = {"level_1": {
                    "store_id": [4],
                    "reset_date": [dt.date(2022, 5, 6)]
                    },
        #   "level_2": {
        #             "store_id": [184, 7, 34, 43, 190],
        #             "reset_date": [dt.date(2022, 2, 24) , dt.date(2022, 1, 28),dt.date(2022, 2, 10) ,dt.date(2022, 1, 25), dt.date(2022, 2, 5) ]
        #             }
          "level_2": {
                    "store_id": [273, 267, 229, 225, 272],
                    "reset_date": [dt.date(2022, 2, 16), dt.date(2022, 2, 23),dt.date(2022, 1, 12), dt.date(2022, 3, 6), dt.date(2022, 2, 25) ]
                    }
          }

forecast_cols  = ['fcst_1', 'fcst_2','fcst_3','fcst_4','fcst_5']
# =========================================================================


def run_func():
    # Write these lines in start of every script
    script_manager_obj = ScriptManager(199, 'ipc_backtest-dummy')
    output_dir_path = script_manager_obj.temp_dir_output_data_path
    job_data_params = script_manager_obj.job_data_params
    actions_list = script_manager_obj.actions_list
    logger = script_manager_obj.logger_obj

    # Start
    logger.info('Script Manager Initialized')
    logger.info('Data params: ' + json.dumps(job_data_params))
    logger.info('Actions list' + json.dumps(actions_list))

    # get backtesting level from frontend
    # try:
    #     level = job_data_params['level']
    # except:
    level = 'level_1'

    # initializing variables (in case of failed run)
    df_old_fcst = pd.DataFrame()
    run_date = str(dt.date.today())
    status = 'Failed'
    wmape_old, wmape_new = 0, []
    bias_old, bias_new = 0, []
    count_na = 0
    store_id_list, reset_date_list = [], []
    metric_overall_lvl = pd.DataFrame()
    metric_old_bucket_lvl = pd.DataFrame()
    metric_bucket_lvl = pd.DataFrame()
    metric_store_lvl = pd.DataFrame()
    metric_PLC_lvl = pd.DataFrame()
    df_mismatch = pd.DataFrame()
    # try:
        # get performance data for recorded reset dates
    logger.info("Getting performance data for recorded reset dates")

    count = 0
    # connection_pg = pg.connect(host="127.0.0.1", user= "data_science_admin", password = "zLKAd3n4bHWui4wNJVi1VQ==", dbname="datascience_generico", port=5433)
    connection_pg = current_config.data_science_postgresql_conn()
    for store_id in levels[level]["store_id"]:
        reset_date = levels[level]["reset_date"][count]
        q_fcst_perf = """
                    select store_id , store_type, reset_date , drug_id, bucket , fcst , demand_28days 
                    from forecast_performance_store_drug_level
                    where store_id = {0}
                    and reset_date = '{1}';
                    """.format(store_id, reset_date.strftime("%Y-%m-%d"))
        df = pd.read_sql(q_fcst_perf, connection_pg)
        df_old_fcst = df_old_fcst.append(df)
        count += 1
    connection_pg.close()

    logger.info("Got performance data for recorded reset dates")

    df_old_fcst.rename({"bucket": "bucket_old", "fcst": "fcst_old"},
                        axis=1, inplace=True)

    ##########################
    # get new model forecast #
    ##########################
    logger.info("Running new model pipeline")

    store_id_list = levels[level]["store_id"]
    reset_date_list = levels[level]["reset_date"]
    reset_date_list = [date.strftime("%Y-%m-%d") for date in reset_date_list]

    # ======================================================================
    # define forecast call function
    # output should contain columns:
    # "store_id", "reset_date", "bucket", "PLC", "drug_id", "fcst_1", "fcst_2", "fcst_3", "fcst_4", "fcst_5"
    df_new_fcst, model_rename = ipc_main_backtesting.ipc_backtesting(store_id_list, reset_date_list, logger)
    # if any fcst column is empty, fill it with np.nan
    # ======================================================================

    logger.info("Got new model forecasts")

    for col in forecast_cols:
        if col not in df_new_fcst.columns:
            logger.info("{} column not present in new forecast".format(str(col)))
            df_new_fcst[col] = 0 

    # merge old and new fcst
    df_fcst_comb = df_old_fcst.merge(df_new_fcst,
                                        on=["store_id", "reset_date", "drug_id"],
                                        how="left")

    count_na = df_fcst_comb.loc[df_fcst_comb["fcst_1"].isna()].shape[0]
    print(f"Missing store-drug entries in new forecast = {count_na}")
    logger.info(f"Missing store-drug entries in new forecast = {count_na}")

    df_mismatch = df_fcst_comb.loc[df_fcst_comb["fcst_1"].isna()]
    df_mismatch = df_mismatch[["store_id", "reset_date", "drug_id"]]
    if local_testing:
        df_fcst_comb = df_fcst_comb.loc[~df_fcst_comb["fcst_1"].isna()]
    df_fcst_comb['All'] = 'All'
    ######################
    # Metric Calculation #
    ######################
    logger.info("Performance metric calculation started")

    metric_overall_lvl = acc_bias_calc(df_merged=df_fcst_comb, slice_col=['All'])
    metric_store_lvl= acc_bias_calc(df_merged=df_fcst_comb, slice_col=['store_id', 'reset_date'])
    metric_old_bucket_lvl= acc_bias_calc(df_merged=df_fcst_comb, slice_col=['bucket_old'])
    metric_bucket_lvl= acc_bias_calc(df_merged=df_fcst_comb, slice_col=['Mixed'])
    metric_PLC_lvl= acc_bias_calc(df_merged=df_fcst_comb, slice_col=['PLC Status L1'])
    metric_classification_lvl = acc_bias_calc(df_merged=df_fcst_comb, slice_col=['classification'])
    metric_store_type_lvl = acc_bias_calc(df_merged=df_fcst_comb, slice_col=['store_type'])
    metric_store_bucket_lvl = acc_bias_calc(df_merged=df_fcst_comb, slice_col=['store_id', 'Mixed'])

    # # to save
    df_pg_dump = df_fcst_comb[['store_id', 'reset_date', 'drug_id', 'bucket_old', 'fcst_old',
    'demand_28days', 'fcst_1', 'fcst_2', 'fcst_3', 'PLC Status L1']].copy()

    df_pg_dump.rename(columns= {'PLC Status L1':'PLC'},inplace=True)

    logger.info("Performance metric calculation ended")

    wmape_old = metric_overall_lvl['acc_fcst_old'][0]*100
    wmape_new = [       
                metric_overall_lvl['acc_fcst_1'][0]*100,
                metric_overall_lvl['acc_fcst_2'][0]*100,
                metric_overall_lvl['acc_fcst_3'][0]*100,
                metric_overall_lvl['acc_fcst_4'][0]*100,
                metric_overall_lvl['acc_fcst_5'][0]*100
                ]

    bias_old = metric_overall_lvl['bias_fcst_old'][0]*100
    bias_new = [
                metric_overall_lvl['bias_fcst_1'][0]*100,
                metric_overall_lvl['bias_fcst_2'][0]*100,
                metric_overall_lvl['bias_fcst_3'][0]*100,
                metric_overall_lvl['bias_fcst_4'][0]*100,
                metric_overall_lvl['bias_fcst_5'][0]*100
                ]

    ###############################
    # writing & compiling outputs #
    ###############################
    # write to PG Stag
    logger.info("Writing base performance data to PG table")

    engine = current_config.data_science_postgresql_write_engine()
    engine.execute("TRUNCATE TABLE ipc_backtest_results")
    df_pg_dump["uploaded_at"] = dt.datetime.now()
    logger.info(f"Columns: {df_pg_dump.columns}")
    df_pg_dump.to_sql(
                name='ipc_backtest_results', con=engine, schema='public',
                if_exists='append', chunksize=500, method='multi', index=False)

    logger.info("Writing to PG table successful")

    status = 'Success'

    # except Exception as error:
    #     logger.info(str(error))

    # create email attachments
    logger.info("Writing email attachments")

    with pd.ExcelWriter(
            output_dir_path +
            'ipc_backtest_results_{}.xlsx'.format(str(run_date))) as writer:
        metric_overall_lvl.to_excel(
            writer, sheet_name='overall_run', index=False)
        metric_store_lvl.to_excel(
            writer, sheet_name='store_reset_date_level', index=False)
        metric_old_bucket_lvl.to_excel(
            writer, sheet_name='old_bucket_level', index=False)
        metric_bucket_lvl.to_excel(
            writer, sheet_name='new_bucket_level', index=False)
        metric_PLC_lvl.to_excel(
            writer, sheet_name='PLC_level', index=False)
        metric_classification_lvl.to_excel(
            writer, sheet_name='classification_level', index=False)
        metric_store_type_lvl.to_excel(
            writer, sheet_name='store_type_level', index=False)
        metric_store_bucket_lvl.to_excel(
            writer, sheet_name='store_bucket_evel', index=False)
        df_mismatch.to_excel(
            writer, sheet_name='drugs_not_in_new_fcst', index=False)

    logger.info("Email attachments written to excel")
    logger.info('Script ended')
    logger.close()


    for action_dict in actions_list:
        if action_dict['category'] == 'EML':
            to_emails = action_dict['email_to']
            subject = '''
            IPC Revamp: Backtest Results: LGBM for march ({config_name}) {run_date}: {status}
            '''.format(config_name=config_name, run_date=run_date, status=status)
            mail_body = '''Backtesting Summary: \n
                Store IDs: {0} \n
                Reset Dates: {1} \n
                ===OVERALL RUN RESULTS=== \n
                OLD WMAPE ACC: {2} \n
                NEW WMAPE ACC: {3} \n
                ------------------------- \n
                OLD BIAS: {4} \n
                NEW BIAS: {5} \n
                ------------------------- \n
                Number of store-drugs present in old but not in new: {6}
                Fcst Columns:{7}
                '''.format(store_id_list, reset_date_list, wmape_old,
                           wmape_new, bias_old, bias_new, count_na, model_rename)
            file_paths = [
                output_dir_path +
                'debug_{}.txt'.format(script_manager_obj.job_id),
                output_dir_path +
                'ipc_backtest_results_{}.xlsx'.format(str(run_date))]
            send_email_file(subject, mail_body, to_emails, file_paths)

    script_manager_obj.teardown(os.path.realpath(__file__), True)


def pe(forecast, actual):
    """percentage forecast error"""
    if (actual == 0) & (forecast == 0):
        pe = 0
    elif forecast == 0:
        pe = -1
    elif actual == 0:
        pe = 1
    else:
        pe = (forecast - actual)/actual
    return round(100 * pe, 1)


def mean(pd_arr):
    return np.round(np.mean(pd_arr), 2)


def acc_bias_calc(df_merged, slice_col):
    #All lags

    fc_cols = ['fcst_old', 'fcst_1', 'fcst_2','fcst_3','fcst_4','fcst_5']
    target_col = 'demand_28days'
    date_col = 'reset_date'
    # slice_col = [date_col,'Mixed']
    # slice_col = [date_col]
    acc_cols = []
    bias_cols = []
    overall_acc_cols = []
    overall_bias_cols = []
    abs_error_cols = []
    error_cols = []


    df_temp = df_merged.copy()
    df_temp['count_drugs'] = 1

    # df_temp['AE'] = df_temp[['preds_xgb_rf_target', 'preds_cb_target', 'preds_lgb']].mean(axis=1)
    df_temp[fc_cols+[target_col]] = df_temp[fc_cols+[target_col]].fillna(0)

    for col in fc_cols :
        abs_error_cols = abs_error_cols+['abs_error_'+str(col)]
        df_temp['abs_error_'+str(col)] = abs(df_temp[col] - df_temp[target_col]) 
        
    for col in fc_cols :
        error_cols = error_cols+['error_'+str(col)]
        df_temp['error_'+str(col)] = df_temp[col] - df_temp[target_col]

    if slice_col is None:
        df_monthly_acc = df_temp[[target_col]+fc_cols+abs_error_cols+error_cols+['count_drugs']].sum()

    df_monthly_acc = df_temp.groupby(slice_col)[[target_col]+fc_cols+abs_error_cols+error_cols+['count_drugs']].sum()

    for col in fc_cols:
        acc_cols = acc_cols+["acc_"+str(col)]
        df_monthly_acc["acc_"+str(col)] = 1 - (df_monthly_acc['abs_error_'+str(col)]/df_monthly_acc[target_col])
        
    for col in fc_cols:
        bias_cols = bias_cols+["bias_"+str(col)]
        df_monthly_acc["bias_"+str(col)] = ((df_monthly_acc['error_'+str(col)]/df_monthly_acc[target_col]))
        
    for col in fc_cols:
        overall_acc_cols = overall_acc_cols + ["overall_acc_"+str(col)]
        df_monthly_acc["overall_acc_"+str(col)] = 1 - (df_monthly_acc['abs_error_'+str(col)].sum()/df_monthly_acc[target_col].sum())
        
    for col in fc_cols:
        overall_bias_cols = overall_bias_cols + ["overall_bias_"+str(col)]
        df_monthly_acc["overall_bias_"+str(col)] = (df_monthly_acc['error_'+str(col)].sum()/df_monthly_acc[target_col].sum())
        

    df_monthly_acc = df_monthly_acc[[target_col]+fc_cols+acc_cols+bias_cols+['count_drugs']]
    df_monthly_acc = df_monthly_acc.reset_index()
    return df_monthly_acc

# if local_testing:
run_func()


