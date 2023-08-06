import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

init_notebook_mode(connected=True)


def read_ch(q, db_config):
    username = db_config['username']
    password = db_config['password']
    host = db_config['host']
    database = db_config['database']
    ch_conn_str = 'clickhouse://{}:{}@{}/{}?protocol=http'.format(username, password, host, database)
    ch_engine = create_engine(ch_conn_str, pool_pre_ping=True)
    ch_session = sessionmaker(bind=ch_engine)()
    return pd.read_sql_query(q, con=ch_engine)


def read_pg(q, db_config):
    username = db_config['username']
    password = db_config['password']
    host = db_config['host']
    database = db_config['database']
    pg_conn_str = 'postgresql://{}:{}@{}/{}'.format(username, password, host, database)
    pg_engine = create_engine(pg_conn_str, pool_pre_ping=True)
    pg_session = sessionmaker(bind=pg_engine)()
    return pd.read_sql_query(q, con=pg_engine)


def get_start_of_week(day):
    try:
        day_of_week = day.weekday()
        to_beginning_of_week = dt.timedelta(days=day_of_week)
        beginning_of_week = day - to_beginning_of_week
        return beginning_of_week.date()
    except:
        return np.nan


def merge_data(users, charges, c1_window, c2_window):
    df = users.merge(charges, on='user_id', how='left')

    df['reg_year'] = pd.to_datetime(df['reg_date']).dt.year
    df['reg_week_of_year'] = df['reg_year'].astype(str) + '_' + \
                             (pd.to_datetime(df['reg_date']).dt.isocalendar().week).astype(str)
    df['reg_start_of_week'] = pd.to_datetime(df['reg_date']).apply(lambda x: get_start_of_week(x))

    df['c1_year'] = pd.to_datetime(df['c1_at']).dt.year
    df.loc[~df.c1_year.isna(), 'c1_year'] = df[~df.c1_year.isna()].c1_year.astype(int)
    df['c1_week_of_year'] = df['c1_year'].astype(str) + '_' + \
                            (pd.to_datetime(df['c1_at']).dt.isocalendar().week).astype(str)

    df.loc[df.c1_year.isna(), 'c1_week_of_year'] = np.nan
    df['c1_start_of_week'] = pd.to_datetime(df['c1_at']).apply(lambda x: get_start_of_week(x))

    df['c1_window'] = pd.to_datetime(df['reg_date'] + timedelta(days=c1_window))
    df['c2_window'] = pd.to_datetime(df['c1_at'] + timedelta(days=c2_window))
    return df


def get_data_since(db_config, data_reqs):
    date = data_reqs['sign_up_week_start']
    c1_window = data_reqs['c1_window_days']
    c2_window = data_reqs['c2_window_days']
    coh = data_reqs['cohort_type']

    q_users = "select id as user_id, created_at as reg_date \
        from postgresql('10.0.14.111:5432', 'resume_production', 'users', 'data_analyst', \
        'pe0+cub8~mi9') as pg where created_at >= '" + date + "'"

    q_charges = "with c1_payments as (select user_id, min(id) as c1_charge_id, \
        min(created_at) as c1_at from postgresql('10.0.14.111:5432', 'resume_production', 'charges', 'data_analyst', \
        'pe0+cub8~mi9') as pg where status = 'succeeded' \
        group by user_id), c2_payments as (select user_id, min(id) as c2_charge_id, \
        min(created_at) as c2_at from postgresql('10.0.14.111:5432', 'resume_production', 'charges', 'data_analyst', \
        'pe0+cub8~mi9') as pg where status = 'succeeded' \
        and id not in (select distinct c1_charge_id from c1_payments) group by user_id) \
        select * from c1_payments left join c2_payments \
        on c1_payments.user_id = c2_payments.user_id where c1_at >= '" + date + "'"

    print('1/2 Reading data... (~10-20 sec)')
    users = read_ch(q_users, db_config)
    charges = read_ch(q_charges, db_config)
    print('2/2 Count CRs with windows...')
    df = merge_data(users, charges, c1_window, c2_window)
    print('Done!')
    return df


def count_stats(df, coh):
    year_col = coh + '_year'
    week_of_year_col = coh + '_week_of_year'
    start_of_week_col = coh + '_start_of_week'

    years = sorted(list(df[~df[year_col].isna()][year_col].unique().astype(int)))
    weeks = sorted(list(df[~df[week_of_year_col].isna()][week_of_year_col].unique()))

    df_res = pd.DataFrame(data={year_col: years[0], week_of_year_col: weeks})

    df_res = df_res.merge(df.groupby(week_of_year_col, as_index=False) \
                          .agg(start_of_week=('reg_start_of_week', 'max')) \
                          .rename(columns={'start_of_week': start_of_week_col}), how='left', on=week_of_year_col)

    df_res['week_full'] = df_res[start_of_week_col].astype(str) + ' (' + df_res[week_of_year_col].astype(str) + ')'

    for i in weeks:
        df_temp_1 = df[df[week_of_year_col] == i]

        if coh == 'reg':
            n_users_came = df_temp_1.user_id.nunique()
            n_users_c1 = df_temp_1[~df_temp_1.c1_charge_id.isna()].query(
                'c1_charge_id > 0 and c1_at <= c1_window').user_id.nunique()
            df_res.loc[df_res[week_of_year_col] == i, 'n_users_C0'] = n_users_came
            df_res.loc[df_res[week_of_year_col] == i, 'C1'] = round(n_users_c1 / n_users_came * 100, 2)
            C1 = n_users_c1 / n_users_came
            c1_left = C1 - (1.96 * np.sqrt(((C1 * (1 - C1)) / n_users_came)))
            c1_right = C1 + (1.96 * np.sqrt(((C1 * (1 - C1)) / n_users_came)))

            df_res.loc[df_res[week_of_year_col] == i, 'c1_ci_left'] = round(c1_left * 100, 2)
            df_res.loc[df_res[week_of_year_col] == i, 'c1_ci_right'] = round(c1_right * 100, 2)

        else:
            n_users_c1 = df_temp_1[~df_temp_1.c1_charge_id.isna()].query('c1_charge_id > 0').user_id.nunique()

        n_users_c2 = df_temp_1[~df_temp_1.c2_charge_id.isna()].query(
            'c2_charge_id > 0 and c1_at <= c1_window and c2_at <= c2_window').user_id.nunique()

        C2 = n_users_c2 / n_users_c1

        df_res.loc[df_res[week_of_year_col] == i, 'n_users_C1'] = n_users_c1
        df_res.loc[df_res[week_of_year_col] == i, 'n_users_C2'] = n_users_c2
        df_res.loc[df_res[week_of_year_col] == i, 'C2'] = round(C2 * 100, 2)

        c2_left = C2 - (1.96 * np.sqrt(((C2 * (1 - C2)) / n_users_c1)))
        c2_right = C2 + (1.96 * np.sqrt(((C2 * (1 - C2)) / n_users_c1)))

        df_res.loc[df_res[week_of_year_col] == i, 'c2_ci_left'] = round(c2_left * 100, 2)
        df_res.loc[df_res[week_of_year_col] == i, 'c2_ci_right'] = round(c2_right * 100, 2)

    df_res_fact = df_res.iloc[:-2]
    df_res_predict_c2 = df_res.tail(3)
    df_res_predict_c1 = df_res.tail(2)

    fig = go.Figure()
    if coh == 'reg':
        fig.add_trace(
            go.Scatter(x=df_res['week_full'], y=df_res['C1'], name='C1', mode="lines+markers+text", text=df_res['C1'],
                       textposition="top center", textfont_size=14))
        fig.add_trace(
            go.Scatter(x=df_res['week_full'], y=df_res['c1_ci_right'], fill='tonexty', mode='none', name='upper'))
        fig.add_trace(
            go.Scatter(x=df_res['week_full'], y=df_res['c1_ci_left'], fill='tonexty', mode='none', name='lower'))
        fig.add_trace(go.Scatter(x=df_res_predict_c1['week_full'], y=df_res_predict_c1['C1'], name='C1 in progress',
                                 mode="lines+markers+text", text=df_res_predict_c1['C1'], textposition="top center",
                                 textfont_size=14, line=dict(color='firebrick', width=4, dash='dot')))
        fig.add_trace(go.Scatter(x=df_res_predict_c1['week_full'], y=df_res_predict_c1['c1_ci_right'], fill='tonexty',
                                 mode='none', name='upper', line=dict(color='firebrick', width=4, dash='dot')))
        fig.add_trace(
            go.Scatter(x=df_res_predict_c1['week_full'], y=df_res_predict_c1['c1_ci_left'], fill='tonexty', mode='none',
                       name='lower', line=dict(color='firebrick', width=4, dash='dot')))

    fig.add_trace(go.Scatter(x=df_res_fact['week_full'], y=df_res_fact['C2'], name='C2', mode="lines+markers+text",
                             text=df_res_fact['C2'], textposition="top center", textfont_size=14))
    fig.add_trace(
        go.Scatter(x=df_res_fact['week_full'], y=df_res_fact['c2_ci_right'], fill='tonexty', mode='none', name='upper'))
    fig.add_trace(
        go.Scatter(x=df_res_fact['week_full'], y=df_res_fact['c2_ci_left'], fill='tonexty', mode='none', name='lower'))

    fig.add_trace(go.Scatter(x=df_res_predict_c2['week_full'], y=df_res_predict_c2['C2'], name='C2 in progress',
                             mode="lines+markers+text", text=df_res_predict_c2['C2'], textposition="top center",
                             textfont_size=14, line=dict(color='royalblue', width=4, dash='dot')))
    fig.add_trace(
        go.Scatter(x=df_res_predict_c2['week_full'], y=df_res_predict_c2['c2_ci_right'], fill='tonexty', mode='none',
                   name='upper', line=dict(color='royalblue', width=4, dash='dot')))
    fig.add_trace(
        go.Scatter(x=df_res_predict_c2['week_full'], y=df_res_predict_c2['c2_ci_left'], fill='tonexty', mode='none',
                   name='lower', line=dict(color='royalblue', width=4, dash='dot')))

    fig.update_layout(title='Weekly CR {}'.format(dt.date.today()), xaxis_title='Week of year', yaxis_title='CR')

    fig.show()

    if not os.path.exists("images"):
        os.mkdir("images")

    path = 'images/' + coh
    fig.write_image((path + '.png'))

    df_res.to_csv((path + '.csv'))

    return df_res