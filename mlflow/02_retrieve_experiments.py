import mlflow
from mlflow_utils import get_mlflow_experiment

if __name__ == '__main__':
    experiment_id = get_mlflow_experiment(experiment_id='124189884952485366')
    print("Experiment ID:", experiment_id)

    print("Name: {}".format(mlflow.get_experiment_by_name('testing_ml_flow1').name))
    print("Artifact Location: {}".format(mlflow.get_experiment_by_name('testing_ml_flow1').artifact_location))
    print("Tags: {}".format(mlflow.get_experiment_by_name('testing_ml_flow1').tags))
    print("Experiment ID: {}".format(mlflow.get_experiment_by_name('testing_ml_flow1').experiment_id))
    print("Lifecycle_stage: {}".format(mlflow.get_experiment_by_name('testing_ml_flow1').lifecycle_stage))
    print("Creation Time: {}".format(mlflow.get_experiment_by_name('testing_ml_flow1').creation_time))