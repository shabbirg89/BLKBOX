import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import json_normalize
import psycopg2
from sklearn.model_selection import train_test_split,GridSearchCV
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
import joblib
from collections import Counter

# Labels
labels ={
  0: "Non-Performing Creative",   
  1: "Performing Creative"
}

# Fetching Data directly from Database
conn = psycopg2.connect(user = "ds_readonly", password = "blkbox2020!",host = "db.blkbox.ai",port = "5432",database = "blkbox")
sql = "select a.adaccount_id,a.date,a.entity_type,CAST(a.metadata as jsonb)->>'cpa' as cpa,CAST(a.metadata as jsonb)->>'cpi' as cpi,CAST(a.metadata as jsonb)->>'cpm' as cpm,CAST(a.metadata as jsonb)->>'ctr' as ctr,CAST(a.metadata as jsonb)->>'impressions' as impression,CAST(a.metadata as jsonb)->>'installs' as installs,CAST(a.metadata as jsonb)->>'spend' as spend,CAST(a.metadata as jsonb)->>'d7_roas' as d7_roas,(b.targets ->> 'd7_roas') as d7_roas1 from public.blkbox_performance_history a left join public.fb_app_adaccounts b on a.adaccount_id = b.adaccount_id where a.entity_type = 'CREATIVE' AND a.date >= date_trunc('month',current_date - interval '1' month) and a.date < date_trunc('month',current_date) order by a.date;"
data = pd.read_sql_query(sql, conn)
conn = None

data['target'] = np.where(data.d7_roas > data.d7_roas1, 1, 0)

data1 = data[['cpa','cpi','cpm','ctr','impression','installs','spend','target']].apply(pd.to_numeric)

data1['IPM'] = ((data1.installs * 1000) / data1.impression)

final = data1[['cpa','spend', 'cpi', 'cpm', 'ctr','IPM','target']]

final = final.dropna()
final.isnull().sum()

x = final.drop(['target'], axis=1)
y = final['target']

# import SMOTE module from imblearn library
sm = SMOTE(random_state = 2)
x, y = sm.fit_resample(x, y)

x_train,x_test,y_train,y_test = train_test_split(x,y, train_size= 0.75,stratify=y,random_state=42,shuffle=True)

rf_fit = RandomForestClassifier(n_estimators=100,criterion="gini",max_depth=None,min_samples_split=2,bootstrap=True,max_features='auto',random_state=42,min_samples_leaf=1)
rf_fit.fit(x_train, y_train.ravel())

from sklearn.metrics import accuracy_score,classification_report

print("\nRandom Forest - Train Confusion Matrix\n\n",pd.crosstab(y_train, rf_fit.predict(x_train),rownames=["Actuall"],colnames = ["Predicted"]))
print("\nRandom Forest - Train accuracy",round(accuracy_score(y_train,rf_fit.predict(x_train)),3))
print("\nRandom Forest - Train ClassificationReport\n",classification_report( y_train, rf_fit.predict(x_train)))

print("\n\nRandom Forest - Test Confusion Matrix\n\n",pd.crosstab(y_test, rf_fit.predict(x_test),rownames =["Actuall"],colnames = ["Predicted"]))
print("\nRandom Forest - Test accuracy",round(accuracy_score(y_test,rf_fit.predict(x_test)),3))
print("\nRandom Forest - Test Classification Report\n",classification_report( y_test, rf_fit.predict(x_test)))

#export the model# Save the model as a pickle in a file
joblib.dump(rf_fit, 'test.pkl')
  
# Load the model from the file
model = joblib.load('test.pkl') 

# Use the loaded model to make predictions
x = [[52.976794, 53, 12.253068, 9.476699, 0.542769, 0.780223]]
predict = model.predict(x)
print("Your Predictions:")
print(labels[predict[0]])
