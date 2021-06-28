import numpy as np
import pandas as pd
import psycopg2
from sklearn.model_selection import train_test_split,GridSearchCV
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
import joblib

from flask import Blueprint, jsonify, request

# define the blueprint
CreativePerformance = Blueprint(name="creative_performance", import_name=__name__)

from dotenv import dotenv_values
config = dotenv_values(".env")

performanceLabels = {
  0: "Non-Performing Creative",   
  1: "Performing Creative"
}

@CreativePerformance.route('/train', methods=['GET'])
def trainPerformancePredictionModel():
  # Fetching Data directly from Database
  conn = psycopg2.connect(
    user = config['USER'], 
    password = config['PASSWORD'],
    host = config['HOST'],
    port = "5432",
    database = config['DATABASE']
  )
  sql = "SELECT performance.adaccount_id, performance.date, performance.entity_type, \
      CAST(performance.metadata as jsonb)->>'cpa' as cpa, CAST(performance.metadata as jsonb)->>'cpi' as cpi, \
      CAST(performance.metadata as jsonb)->>'cpm' as cpm, CAST(performance.metadata as jsonb)->>'ctr' as ctr, \
      CAST(performance.metadata as jsonb)->>'impressions' as impression, CAST(performance.metadata as jsonb)->>'installs' as installs, \
      CAST(performance.metadata as jsonb)->>'spend' as spend, CAST(performance.metadata as jsonb)->>'d7_roas' as d7_roas, \
      (adaccounts.targets ->> 'd7_roas') as d7_target \
    FROM public.blkbox_performance_history as performance \
    LEFT JOIN public.fb_app_adaccounts as adaccounts \
    ON performance.adaccount_id = adaccounts.adaccount_id \
    WHERE \
      performance.entity_type = 'CREATIVE' AND \
      performance.date >= date_trunc('month',current_date - interval '12' month) \
      AND performance.date < date_trunc('month',current_date) \
    ORDER BY performance.date;"
  performanceArray = pd.read_sql_query(sql, conn)
  conn = None

  performanceArray['target'] = np.where(performanceArray.d7_roas > performanceArray.d7_target, 1, 0)
  performanceTrainingData = performanceArray[['cpa','cpi','cpm','ctr','impression','installs','spend','target']].apply(pd.to_numeric)
  performanceTrainingData['IPM'] = ((performanceTrainingData.installs * 1000) / performanceTrainingData.impression)
  performanceTrainingData = performanceTrainingData.dropna(axis = 0, how ='any')
  performanceTrainingData = performanceTrainingData[['cpa','spend', 'cpi', 'cpm', 'ctr','IPM','target']]

  performanceInputs = performanceTrainingData.drop(['target'], axis = 1)
  performanceTarget = performanceTrainingData['target']

  # Model definition
  performanceModel = RandomForestClassifier(
    n_estimators = 100,
    criterion = "gini",
    max_depth = None,
    min_samples_split = 2,
    bootstrap = True,
    max_features = 'auto',
    random_state = 42,
    min_samples_leaf = 1
  )
  performanceModel.fit(performanceInputs, performanceTarget.ravel())
  joblib.dump(performanceModel, 'creativePredictionModel.pkl')
  return {
    'success': True
  }

# 'cpa','spend', 'cpi', 'cpm', 'ctr','IPM'
@CreativePerformance.route('/test', methods=['GET'])
def predictPerformance():
  data = request.get_json()
  performanceModel = joblib.load('creativePredictionModel.pkl') 
  performanceInput = [[
    data['cpa'], 
    data['spend'], 
    data['cpi'], 
    data['cpm'],
    data['ctr'],
    data['ipm']
  ]]
  predictedPerformance = performanceModel.predict(performanceInput)
  if predictedPerformance[0] == 0:
    predictedPerformance = False
  else:
    predictedPerformance = True
  return {
    'success': True,
    'is_performing_creative': predictedPerformance
  }

# # add view function to the blueprint
# @CreativePerformance.route('/test', methods=['GET'])
# def test():
#     output = {"msg": "I'm the test endpoint from blueprint_x."}
#     return jsonify(output)

# prediction = predictPerformance({
#   'cpa': 30.32,
#   'spend': 30,
#   'cpi': 30.32,
#   'cpm': 5,
#   'ctr': 1.805,
#   'ipm': 1.65
# })
# print(prediction)