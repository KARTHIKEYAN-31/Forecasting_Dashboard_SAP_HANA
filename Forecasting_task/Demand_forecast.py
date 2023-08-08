import pandas as pd
import numpy as np
from hdbcli import dbapi
import hana_ml
from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas
import xgboost as xgb
from xgboost import plot_importance, plot_tree
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

date_today = datetime.now()


db = pd.read_json('db.json')

db_url = db['db_url'][0]
db_port = db['db_port'][0]
db_user = db['db_user'][0]
db_pwd = db['db_pwd'][0]
cc = ConnectionContext(db_url, db_port, db_user, db_pwd)
print('Connection Created successfully!!')


hana_ml_df = cc.table('TRAIN_TABLE_US_ELECTRICITY_DEMEND', schema='DBADMIN')
us_demand = hana_ml_df.collect()
us_demand = us_demand.set_index('date')
print('Data collected.')


us_demand = us_demand.rename(
    {'Series ID: EBA.US48-ALL.D.H megawatthours': 'megawatthours'},
     axis=1)
us_demand.index.names = ['Date']
us_demand = us_demand.asfreq('H')

train_df = us_demand.head((len(us_demand)//100)*70)
test_df = us_demand.tail(len(us_demand) - (len(us_demand)//100)*70)
print('Train Test Data Splitted')


def create_features(df, label=None):
    """
    Creates time series features from datetime index
    """
    df['date'] = df.index
    df['hour'] = df['date'].dt.hour
    df['dayofweek'] = df['date'].dt.dayofweek
    df['quarter'] = df['date'].dt.quarter
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['dayofyear'] = df['date'].dt.dayofyear
    df['dayofmonth'] = df['date'].dt.day
    df['weekofyear'] = df['date'].dt.weekofyear
    
    X = df[['hour','dayofweek','quarter','month','year',
           'dayofyear','dayofmonth','weekofyear']]
    if label:
        y = df[label]
        return X, y
    return X


X_train, y_train = create_features(train_df, label='megawatthours')
X_test, y_test = create_features(test_df, label='megawatthours')
print('Features Created.')

reg = xgb.XGBRegressor(n_estimators=1000)
reg.fit(X_train, y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        early_stopping_rounds=50,
       verbose=False)
print('Model Trained')

test_df['megawatthours_predicted'] = reg.predict(X_test)
pjme_all = pd.concat([test_df, us_demand], sort=False)
MAE = mean_absolute_error(y_test,test_df['megawatthours_predicted'])
MSE = mean_squared_error(y_test,test_df['megawatthours_predicted'])
MedAE =  median_absolute_error(y_test,test_df['megawatthours_predicted'])
print('Stat value created')

training_stat = pd.DataFrame({'DateTime of Training': date_today ,'Mean Absolute Error': MAE.astype(float), 'Mean Squared Error': MSE, 'Median Absolute Error': MedAE}, index=[0])


days = pd.date_range(us_demand.tail(1).index[0], us_demand.tail(1).index[0] + timedelta(days=90), freq='H')

df = pd.DataFrame({'date': days}).set_index('date')
to_predict = create_features(df)

print('Forecasted for next 90 days')


prediction = reg.predict(to_predict)
prediction_df = pd.DataFrame()
prediction_df['Megawatthours_predicted'] = pd.DataFrame(prediction)
df = pd.DataFrame({'Date': days})
final_prediction = df.join(prediction_df)

dfh = create_dataframe_from_pandas(cc, final_prediction, 'PREDICTION_TABLE_US_ELECTRICITY_DEMEND',
                             schema='DBADMIN', 
                             force=True, # True: truncate and insert
                             replace=True)

print('Prediction Table Updated!!!!')


dfh = create_dataframe_from_pandas(cc, training_stat, 'TRAINING_STAT',
                            schema='DBADMIN',
                            append=True)

print('Stat Table Updated.')

print('Sucessfully Forecasted and Updated!!')