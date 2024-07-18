import mlflow 
from mlflow.models import infer_signature
from mlflow_utils import get_mlflow_experiment

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import pandas as pd

if __name__ == '__main__':
    run_id = "ba490b83ef614cc88ae4b66730d24ede" # choose the run_id from the mlflow ui

    x, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
    X = pd.DataFrame(x, columns=[f"feature_{i}" for i in range(x.shape[1])])
    y = pd.Series(y, name="target")

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # load model 
    model_uri = f"runs:/{run_id}/random_forest_classifier" # random_forest_classifier is the artifact path where the model is saved
    model = mlflow.sklearn.load_model(model_uri=model_uri)

    # infer 
    y_pred = model.predict(x_test)
    y_pred = pd.DataFrame(y_pred, columns=["prediction"])

    print(y_pred.head())

    
