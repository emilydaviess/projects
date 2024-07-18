import mlflow
from mlflow_utils import get_mlflow_experiment

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay, ConfusionMatrixDisplay

import matplotlib.pyplot as plt

if __name__ == '__main__':

    experiment = get_mlflow_experiment(experiment_id='301492217488622248')
    print("Experiment ID:", experiment.experiment_id)

    with mlflow.start_run(run_name="logging_images", experiment_id=experiment.experiment_id) as run:

        random_state = 42
        x, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=random_state)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=random_state)

        # autolog model info to models/ directory in the artifact section
        # mlflow.autolog() 
        # or we could use 
        mlflow.sklearn.autolog() # to log only sklearn models, this also logs params, metrics, and artifacts

        rfc = RandomForestClassifier(n_estimators=100, random_state=random_state)
        rfc.fit(x_train, y_train)
        y_pred = rfc.predict(x_test)

        # log model - there are different types i.e. mlflow.tensorflow.log_model, mlflow.pytorch.log_model, mlflow.sklearn.log_model
        # mlflow.sklearn.log_model(sk_model=rfc, artifact_path="random_forest_classifier")


        # log the precision-recall curve
        fig_pr = plt.figure()
        pr_display = PrecisionRecallDisplay.from_predictions(y_test, y_pred, ax=plt.gca())
        plt.title("Precision-Recall Curve")
        plt.legend(loc="best")

        mlflow.log_figure(fig_pr, "metrics/precision_recall_curve.png")

        # log the ROC curve
        fig_roc = plt.figure()
        roc_display = RocCurveDisplay.from_predictions(y_test, y_pred, ax=plt.gca())
        plt.title("ROC Curve")
        plt.legend(loc="best")

        mlflow.log_figure(fig_roc, "metrics/roc_curve.png")

        # log the confusion matrix
        fig_cm = plt.figure()
        cm_display = ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=plt.gca())
        plt.title("Confusion Matrix")
        plt.legend(loc="best")

        mlflow.log_figure(fig_cm, "metrics/confusion_matrix.png")

        print("Run ID:", run.info.run_id)
        print("Experiment ID:", run.info.experiment_id)
        print("Artifact URI:", run.info.artifact_uri)


