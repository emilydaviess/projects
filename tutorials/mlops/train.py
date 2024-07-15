################################################## Import Libraries ##################################################

import numpy as np
import pandas as pd
import os
from sklearn import metrics
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit
from sklearn.metrics import (
    accuracy_score, classification_report, recall_score, confusion_matrix,
    roc_auc_score, precision_score, f1_score, roc_curve, auc
)
from sklearn.preprocessing import OrdinalEncoder
from catboost import CatBoostClassifier, Pool
import pickle

################################################## Data Loading and Editing ##################################################
print("Loading data...")
data_path = "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
df = pd.read_csv(data_path)
print("Data loaded successfully!")
print("Data shape: ", df.shape)

# convert TotalCharges to numeric, filling NaN values
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'].fillna(df['tenure'] * df['MonthlyCharges'], inplace=True)

# convert SeniorCitizen to object
df['SeniorCitizen'] = df['SeniorCitizen'].astype(object)

# replace 'No phone service' and 'No internet service' with 'No' for certain columns
df['MultipleLines'] = df['MultipleLines'].replace('No phone service', 'No')
columns_to_replace = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
for column in columns_to_replace:
    df[column] = df[column].replace('No internet service', 'No')

# convert 'Churn' categorical variable to numeric
df['Churn'] = df['Churn'].replace({'No': 0, 'Yes': 1})

################################################## StratifiedShuffleSplit ##################################################

# create the StratifiedShuffleSplit object
print("Splitting data...")
strat_split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=64)
train_index, test_index = next(strat_split.split(df, df["Churn"]))

# create train and test sets
strat_train_set = df.loc[train_index]
strat_test_set = df.loc[test_index]

X_train = strat_train_set.drop("Churn", axis=1)
y_train = strat_train_set["Churn"].copy()

X_test = strat_test_set.drop("Churn", axis=1)
y_test = strat_test_set["Churn"].copy()

# save the train and test sets as pkl files so that they can be used in the streamlit app
datasets = {'X_train.pkl': X_train, 'y_train.pkl': y_train, 'X_test.pkl': X_test, 'y_test.pkl': y_test}
for filename, data in datasets.items():
    with open(os.path.join('data', filename), 'wb') as file:
        pickle.dump(data, file)

################################################## CATBOOST ##################################################

# identify categorical columns
categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

# initialize and fit CatBoostClassifier
print("Training model...")
cat_model = CatBoostClassifier(verbose=False, random_state=0, scale_pos_weight=3)
cat_model.fit(X_train, y_train, cat_features=categorical_columns, eval_set=(X_test, y_test))

# predict on test set
print("Predicting on test set...")
y_pred = cat_model.predict(X_test)

# calculate evaluation metrics
accuracy, recall, roc_auc, precision = [round(metric(y_test, y_pred), 4) for metric in [accuracy_score, recall_score, roc_auc_score, precision_score]]

# create a DataFrame to store results
model_names = ['CatBoost_Model']
result = pd.DataFrame({'Accuracy': accuracy, 'Recall': recall, 'Roc_Auc': roc_auc, 'Precision': precision}, index=model_names)

# Print results
print(result)

# Save the model in the 'model' directory
print("Saving model...")
model_dir = "models"
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

model_path = os.path.join(model_dir, "catboost_model.cbm")
cat_model.save_model(model_path)