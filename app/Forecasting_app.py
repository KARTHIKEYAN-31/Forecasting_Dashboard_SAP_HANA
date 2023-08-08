import pandas as pd
import numpy as np
from hdbcli import dbapi
import streamlit as st
import hana_ml
from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas
import plotly.graph_objs as go
import plotly.express as px
from cfenv import AppEnv

st.set_page_config(
    page_title="Real-Time Electricity Demand Monitoring Dashboard",
    page_icon="✅",
    layout="wide",
)


st.title('US Electricity Demand Analysis')
env = AppEnv()

HANA_SERVICE = 'hdb-staging-schema'
hana = env.get_service(name=HANA_SERVICE)


# Instantiate connection object
db_url = 'e1bc9e12-6a46-4758-ab57-a7dead9396fa.hana.trial-us10.hanacloud.ondemand.com'
db_port = 443
db_user = 'DBADMIN'
db_pwd = 'Karthi31@tvm'
cc = ConnectionContext(db_url, db_port, db_user, db_pwd)

st.write('connection created successfully')


hana_ml_df = cc.table('TRAIN_TABLE_US_ELECTRICITY_DEMEND', schema='DBADMIN')
us_demand = hana_ml_df.collect()


if st.button('Enter Data'):

    us_demand = us_demand.set_index('date')
    last_date = us_demand.index[-1]
    new_last = last_date + pd.Timedelta(1, unit='h')


    st.write('Enter the Electricity consumed on '+str(new_last)+' in MegaWattHoures.')


    MWH = st.number_input('Electricity (MWH): ',step =1, min_value = 162800, max_value = 719700)

    new_df = pd.DataFrame({'date': [new_last],'megawatthours': 0})

    if st.button('Upload_data') and (MWH >162800 and MWH<719700):

        dfh = create_dataframe_from_pandas(cc,new_df, 'TRAIN_TABLE_US_ELECTRICITY_DEMEND',
                                        schema = 'DBADMIN',
                                        append = True)

        st.write('Data Updated Successfully!')
    else:
        st.write('Data Not Updated!')



if st.button('Explore and Forecast Data'):
    
    hana_prediction_df = cc.table('PREDICTION_TABLE_US_ELECTRICITY_DEMEND', schema='DBADMIN')
    prediction_df = hana_prediction_df.collect()
    prediction_df = hana_prediction_df.collect().rename(columns={'Megawatthours_predicted': 'megawatthours','Date':'date'})
    
    df =  pd.concat([us_demand, prediction_df], sort=False)

    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=us_demand['date'], y=us_demand['megawatthours'], name="megawatthours",
                                line_color='deepskyblue'))
        
        fig.add_trace(go.Scatter(x=prediction_df['date'], y=prediction_df['megawatthours'], name="megawatthours",
                                line_color='orange'))

        fig.update_layout(title_text='Time Series with Rangeslider',
                        xaxis_rangeslider_visible=True)
        fig

    def create_features(df):
        """
        Creates time series features from datetime index
        """
        df1 = pd.DataFrame()
        df1['date'] = df.index
        df1['hour'] = df1['date'].dt.hour
        df1['dayofweek'] = df1['date'].dt.dayofweek
        df1['quarter'] = df1['date'].dt.quarter
        df1['month'] = df1['date'].dt.month
        df1['year'] = df1['date'].dt.year
        df1['dayofyear'] = df1['date'].dt.dayofyear
        df1['dayofmonth'] = df1['date'].dt.day
        df1['weekofyear'] = df1['date'].dt.isocalendar().week.astype(int)
        df1['megawatthours'] = list(df['megawatthours'])


        X = df1[['hour','dayofweek','quarter','month','year',
            'dayofyear','dayofmonth','weekofyear','megawatthours']]
        return X
    
    df1 = us_demand.set_index('date')
    df1 = df1.rename(
        {'Series ID: EBA.US48-ALL.D.H megawatthours': 'megawatthours'},
        axis=1)
    df1.index.names = ['Date']
    df1 = df1.asfreq('H')

    df2 = create_features(df1)


    for j,i in enumerate(['hour','quarter','month',
            'dayofyear','weekofyear']):
        if (j+2)%2 == 0:
            with fig_col2:
                fig = px.box(df2, x=i, y="megawatthours")
                fig
        else:
            with fig_col1:
                fig = px.box(df2, x=i, y="megawatthours")
                fig

    hana_training_stat = cc.table('TRAINING_STAT', schema='DBADMIN')
    training_stat = hana_training_stat.collect()

    with fig_col1:
        st.write(prediction_df)
    with fig_col2:
        st.write(training_stat.tail())
