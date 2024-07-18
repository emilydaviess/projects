import mlflow
from typing import Any

def create_mlflow_experiment(experiment_name: str, artifact_location: str, tags: dict[str, Any]) -> str:
    '''
    Create a new MLflow experiment with the given name, artifact location, and tags.
    Returns the experiment ID.
    '''

    # check if the experiment already exists
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment:
        print(f"Experiment '{experiment_name}' already exists.")
        experiment_id = experiment.experiment_id
    else:
        experiment_id = mlflow.create_experiment(
            name=experiment_name,
            artifact_location=artifact_location,
            tags=tags
        )
        print("Experiment created. Experiment ID:", experiment_id)

    return experiment_id

def get_mlflow_experiment(experiment_id: str=None, experiment_name: str=None) -> mlflow.entities.Experiment:
    '''
    Get the experiment ID for the given experiment name.
    '''

    if experiment_id is not None:
        try:
            experiment = mlflow.get_experiment(experiment_id)
        except:
            print("Experiment ID not found.")
            raise ValueError("Experiment ID not found.")
    elif experiment_name is not None:
        try: 
            experiment = mlflow.get_experiment_by_name(experiment_name)
        except:
            print("Experiment name not found.")
            raise ValueError("Experiment name not found.")
    else:
        if experiment_id is None and experiment_name is None:
            print("Please provide an experiment ID or experiment name.")
            raise ValueError("Please provide an experiment ID or experiment name.")

    return experiment