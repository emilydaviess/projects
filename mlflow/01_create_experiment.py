from mlflow_utils import create_mlflow_experiment

if __name__ == '__main__':
    experiment_id = create_mlflow_experiment(
        experiment_name='testing_ml_flow1',
        artifact_location='testing_mlflow_artifacts',
        tags= {
            'env': 'dev',
            'version': '1.0.0'
        }
    )
    print("Experiment ID:", experiment_id)