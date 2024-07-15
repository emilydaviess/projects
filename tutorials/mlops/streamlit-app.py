import shap
import pandas as pd
import os
import numpy as np
import streamlit
from matplotlib import pyplot as plt
import joblib
from catboost import CatBoostClassifier, Pool

# Path of the trained model and data
MODEL_PATH = "models/catboost_model.cbm" 
DATA_PATH_PARQUET = "data/churn_data_regulated.parquet"
DATA_PATH_CSV = "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"

streamlit.set_page_config(page_title="Churn Project")

@streamlit.cache_resource
def load_model():
    model = CatBoostClassifier()
    model.load_model(MODEL_PATH)
    return model

def load_data():
    # check if the .parquet file exists
    if not os.path.exists(DATA_PATH_PARQUET):
        # if not, read the data from CSV
        data = pd.read_csv(DATA_PATH_CSV)
        # convert and save to .parquet
        data.to_parquet(DATA_PATH_PARQUET)
    else:
        pass
        # if .parquet file exists, load it directly
        data = pd.read_parquet(DATA_PATH_PARQUET)

    return data

def load_train_test_data(file_path):
    data = joblib.load(file_path)
    data.reset_index(drop=True, inplace=True)
    return data

def calculate_shap(model, X_train, X_test):
    # Calculate SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values_cat_train = explainer.shap_values(X_train)
    shap_values_cat_test = explainer.shap_values(X_test)
    return explainer, shap_values_cat_train, shap_values_cat_test

def plot_shap_values(model, explainer, shap_values_cat_train, shap_values_cat_test, customer_id, X_test, X_train):
    # Visualize SHAP values for a specific customer
    customer_index = X_test[X_test['customerID'] == customer_id].index[0]
    fig, ax_2 = plt.subplots(figsize=(6,6), dpi=200)
    shap.decision_plot(explainer.expected_value, shap_values_cat_test[customer_index], X_test[X_test['customerID'] == customer_id], link="logit")
    streamlit.pyplot(fig)
    plt.close()

def display_shap_summary(shap_values_cat_train, X_train):
    # Create the plot summarizing the SHAP values
    shap.summary_plot(shap_values_cat_train, X_train, plot_type="bar", plot_size=(12,12))
    summary_fig, _ = plt.gcf(), plt.gca()
    streamlit.pyplot(summary_fig)
    plt.close()

def display_shap_waterfall_plot(explainer, expected_value, shap_values, feature_names, max_display=20):
    # Create SHAP waterfall drawing
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    shap.plots._waterfall.waterfall_legacy(expected_value, shap_values, feature_names=feature_names, max_display=max_display, show=False)
    streamlit.pyplot(fig)
    plt.close()

def summary(model, data, X_train, X_test):
    # Calculate SHAP values
    explainer, shap_values_cat_train, shap_values_cat_test = calculate_shap(model, X_train, X_test)

    # Summarize and visualize SHAP values
    display_shap_summary(shap_values_cat_train, X_train)

def plot_shap(model, data, customer_id, X_train, X_test):
    # Calculate SHAP values
    explainer, shap_values_cat_train, shap_values_cat_test = calculate_shap(model, X_train, X_test)
    
    # Visualize SHAP values
    plot_shap_values(model, explainer, shap_values_cat_train, shap_values_cat_test, customer_id, X_test, X_train)

    # Waterfall
    customer_index = X_test[X_test['customerID'] == customer_id].index[0]
    display_shap_waterfall_plot(explainer, explainer.expected_value, shap_values_cat_test[customer_index], feature_names=X_test.columns, max_display=20)

streamlit.title("Telco Customer Churn Project")

def main():
    print("Loading model...")
    model = load_model()
    print("Loading data...")
    data = load_data()

    print("Loading train and test data...")
    X_train = load_train_test_data("data/X_train.pkl")
    X_test = load_train_test_data("data/X_test.pkl")
    y_train = load_train_test_data("data/y_train.pkl")
    y_test = load_train_test_data("data/y_test.pkl")
    
    print("Data loaded successfully!")

    max_tenure = data['tenure'].max()
    max_monthly_charges = data['MonthlyCharges'].max()
    max_total_charges = data['TotalCharges'].max()

    # radio buttons for options
    print("Creating radio buttons...")
    election = streamlit.radio("Make Your Choice:", ("Feature Importance", "User-based SHAP", "Calculate the probability of CHURN"))
    available_customer_ids = X_test['customerID'].tolist()
    
    # if Feature Importance is selected
    if election == "Feature Importance":
        summary(model, data, X_train=X_train, X_test=X_test)
    
    # if User-based SHAP option is selected
    elif election == "User-based SHAP":
        # customer ID text input
        customer_id = streamlit.selectbox("Choose the Customer", available_customer_ids)
        customer_index = X_test[X_test['customerID'] == customer_id].index[0]
        streamlit.write(f'Customer {customer_id}: Actual value for the Customer Churn : {y_test.iloc[customer_index]}')
        y_pred = model.predict(X_test)
        streamlit.write(f"Customer {customer_id}: CatBoost Model's prediction for the Customer Churn : {y_pred[customer_index]}")
        plot_shap(model, data, customer_id, X_train=X_train, X_test=X_test)
    

    # if Calculate CHURN Probability option is selected
    elif election == "Calculate the probability of CHURN":
        # Retrieving data from the user
        customerID = "6464-UIAEA"
        gender = streamlit.selectbox("Gender:", ("Female", "Male"))
        senior_citizen = streamlit.number_input("SeniorCitizen (0: No, 1: Yes)", min_value=0, max_value=1, step=1)
        partner = streamlit.selectbox("Partner:", ("No", "Yes"))
        dependents = streamlit.selectbox("Dependents:", ("No", "Yes"))
        tenure = streamlit.number_input("Tenure:", min_value=0, max_value=max_tenure, step=1)
        phone_service = streamlit.selectbox("PhoneService:", ("No", "Yes"))
        multiple_lines = streamlit.selectbox("MultipleLines:", ("No", "Yes"))
        internet_service = streamlit.selectbox("InternetService:", ("No", "DSL", "Fiber optic"))
        online_security = streamlit.selectbox("OnlineSecurity:", ("No", "Yes"))
        online_backup = streamlit.selectbox("OnlineBackup:", ("No", "Yes"))
        device_protection = streamlit.selectbox("DeviceProtection:", ("No", "Yes"))
        tech_support = streamlit.selectbox("TechSupport:", ("No", "Yes"))
        streaming_tv = streamlit.selectbox("StreamingTV:", ("No", "Yes"))
        streaming_movies = streamlit.selectbox("StreamingMovies:", ("No", "Yes"))
        contract = streamlit.selectbox("Contract:", ("Month-to-month", "One year", "Two year"))
        paperless_billing = streamlit.selectbox("PaperlessBilling", ("No", "Yes"))
        payment_method = streamlit.selectbox("PaymentMethod:", ("Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"))
        monthly_charges = streamlit.number_input("Monthly Charges", min_value=0.0, max_value=max_monthly_charges, step=0.01)
        total_charges = streamlit.number_input("Total Charges", min_value=0.0, max_value=float(max_total_charges), step=0.01)
        
        # Confirmation button
        confirmation_button = streamlit.button("Confirm")

    # When the confirmation button is clicked
        if confirmation_button:
            # Convert user-entered data into a data frame
            new_customer_data = pd.DataFrame({
                "customerID": [customerID],
                "gender": [gender],
                "SeniorCitizen": [senior_citizen],
                "Partner": [partner],
                "Dependents": [dependents],
                "tenure": [tenure],
                "PhoneService": [phone_service],
                "MultipleLines": [multiple_lines],
                "InternetService": [internet_service],
                "OnlineSecurity": [online_security],
                "OnlineBackup": [online_backup],
                "DeviceProtection": [device_protection],
                "TechSupport": [tech_support],
                "StreamingTV": [streaming_tv],
                "StreamingMovies": [streaming_movies],
                "Contract": [contract],
                "PaperlessBilling": [paperless_billing],
                "PaymentMethod": [payment_method],
                "MonthlyCharges": [monthly_charges],
                "TotalCharges": [total_charges]
            })

            # predict churn probability using the model
            churn_probability = model.predict_proba(new_customer_data)[:, 1]

            # format churn probability
            formatted_churn_probability = "{:.2%}".format(churn_probability.item())

            big_text = f"<h1>Churn Probability: {formatted_churn_probability}</h1>"
            streamlit.markdown(big_text, unsafe_allow_html=True)
            streamlit.write(new_customer_data.to_dict())

if __name__ == "__main__":
    print("Starting Streamlit app...")
    main()