import mlflow
from mlflow_utils import create_mlflow_experiment

if __name__ == '__main__':
   
    experiment_id = create_mlflow_experiment(experiment_name='testing_ml_flow2', artifact_location='testing_mlflow_artifacts', tags={'env': 'dev', 'version': '1.0.0'})

    # we can also use with mlflow.start_run(experiment_id=experiment_id) as run: 
    # so that we don't have to call mlflow.end_run() explicitly

    # start a new run (we could also set_experiment(experiment_id) before starting the run, but it's not necessary as we are passing the experiment_id to start_run)
    # mlflow.set_experiment(experiment_id)
    with mlflow.start_run(experiment_id=experiment_id, run_name='mlflow_run1') as run:
        # your machine learning code goes here
        # hyperparameters
        parameters = {
            "learning_rate": 0.01,
            "optimizer": "adam",
            "loss_function": "mse",
            "batch_size": 100,
            "epochs": 10
        }
        mlflow.log_params(parameters)

        metrics = {
            "mse": 0.01,
            "rmse": 0.01,
            "mae": 0.01,
            "r2": 0.01
        }
        mlflow.log_metrics(metrics)

        # log artifacts
        # create a text file and write some text to it
        with open("helloworld.txt", "w") as f:
            f.write("Hello World!")

        # log the text file as an artifact
        mlflow.log_artifact(local_path="helloworld.txt", artifact_path="test_files")

        # if we want to log all the files in a directory as artifacts we can use below - you can also include things like images,text files in that folder and it will log all of them in mlflow
        # mlflow.log_artifacts(local_dir="./run_artifacts", artifact_path="run_artifacts")

        print("Run ID:", run.info.run_id)
        print("Experiment ID:", run.info.experiment_id)
        print("Artifact URI:", run.info.artifact_uri)