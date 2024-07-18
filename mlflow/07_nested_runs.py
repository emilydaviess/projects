import mlflow 
from mlflow_utils import create_mlflow_experiment

experiment_id = create_mlflow_experiment(
    experiment_name='nested runs',
    artifact_location='nested_runs_artifacts',
    tags= {
        'env': 'dev',
        'version': '1.0.0',
        'purpose': 'learning'
    }
)
print("experiment_id:", experiment_id)
with mlflow.start_run(run_name="parent_run", experiment_id=experiment_id) as parent_run:
    print("Parent Run ID:", parent_run.info.run_id)
    mlflow.log_param("parent_run", "parent_value")

    with mlflow.start_run(run_name="child_run1", nested=True, experiment_id=experiment_id) as child_run1:
        print("Child Run1 ID:", child_run1.info.run_id)
        mlflow.log_param("child_run1", "child_value1")

        with mlflow.start_run(run_name="child_run11", nested=True, experiment_id=experiment_id) as child_run11:
            print("Child Run11 ID:", child_run11.info.run_id)
            mlflow.log_param("child_run11", "child_value11")

        with mlflow.start_run(run_name="child_run12", nested=True, experiment_id=experiment_id) as child_run12:
            print("Child Run12 ID:", child_run12.info.run_id)
            mlflow.log_param("child_run12", "child_value12")

    with mlflow.start_run(run_name="child_run2", nested=True, experiment_id=experiment_id) as child_run2:
        print("Child Run2 ID:", child_run2.info.run_id)
        mlflow.log_param("child_run2", "child_value2")
