import mlflow 
from mlflow_utils import create_mlflow_experiment

from mlflow.models.signature import ModelSignature, infer_signature
from mlflow.types.schema import Schema, ParamSchema, ColSpec, ParamSpec

from sklearn.datasets import make_classification
import pandas as pd
from typing import Tuple
from sklearn.ensemble import RandomForestClassifier

def get_train_data()->Tuple[pd.DataFrame]:
    """
    Generate train and test datasets

    :return: x_train, x_test, y_train, y_test
    """

    x, y = make_classification()
    features = [f"feature_{i}" for i in range(x.shape[1])]
    df = pd.DataFrame(x, columns=features)
    df['label'] = y

    return df[features], df['label']

if __name__ == '__main__':
    x_train, y_train = get_train_data()
    # print(x_train.head())
    # cols_spec = []
    # data_map = {
    #     "int64": "integer",
    #     "float64": "double",
    #     "bool": "boolean",
    #     "str": "string",
    #     "date": "datetime"
    # }

    # for name, dtype in x_train.dtypes.to_dict().items():
    #     cols_spec.append(ColSpec(name=name, type=data_map[str(dtype)]))

    # input_schema = Schema(inputs=cols_spec)
    # output_schema = Schema([ColSpec(name="label", type="integer")])

    # parameter = ParamSpec(name="model_name",dtype="string",default="model1")
    # param_schema = ParamSchema(params=[parameter])

    # model_signature = ModelSignature(
    #     inputs=input_schema,
    #     outputs=output_schema,
    #     params=param_schema
    # )

    # infer signature infers the schema from the data (train, label) and the parameters (model_name)
    # it basically automates all the steps commented out above which is defining the schema of the data
    model_signature = infer_signature(x_train, y_train, params={"model_name": "model1"})
    print("model_signature:", model_signature.to_dict())

    experiment_id = create_mlflow_experiment(
        experiment_name='Model Signature', 
        artifact_location='model_signature_artifacts', 
        tags={'env': 'dev', 'version': '1.0.0', 'purpose': 'learning'}
    )

    with mlflow.start_run(run_name='model_signature_run', experiment_id=experiment_id) as run:
        mlflow.sklearn.log_model(
            sk_model=RandomForestClassifier(),
            artifact_path="random_forest_classifier",
            signature=model_signature
        )
