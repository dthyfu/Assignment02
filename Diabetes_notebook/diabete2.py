from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os


app = Flask(__name__)


# =========================
# Model paths
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

PREPROCESSOR_PATH = os.path.join(
    MODEL_DIR,
    "preprocessor.joblib"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "model.joblib"
)


# =========================
# Load saved components
# =========================

preprocessor = joblib.load(
    PREPROCESSOR_PATH
)

model = joblib.load(
    MODEL_PATH
)

print("Preprocessor loaded successfully.")
print("Model loaded successfully.")


# =========================
# Input features
# =========================

FEATURES = [
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "smoking_history",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level"
]


# =========================
# Home endpoint
# =========================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "service": "Diabetes Prediction API",
        "status": "running",
        "endpoint": "POST /predict"
    })


# =========================
# Prediction endpoint
# =========================

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    if data is None:
        return jsonify({
            "error": "Request body must be JSON."
        }), 400

    # Check missing features
    missing_features = [
        feature
        for feature in FEATURES
        if feature not in data
    ]

    if missing_features:
        return jsonify({
            "error": "Missing required features.",
            "missing_features": missing_features
        }), 400

    # Create input DataFrame
    input_data = {
        feature: data[feature]
        for feature in FEATURES
    }

    input_df = pd.DataFrame(
        [input_data]
    )

    # Validate numerical values
    numerical_input_features = [
        "age",
        "hypertension",
        "heart_disease",
        "bmi",
        "HbA1c_level",
        "blood_glucose_level"
    ]

    for feature in numerical_input_features:
        if not isinstance(
            data[feature],
            (int, float)
        ):
            return jsonify({
                "error": f"{feature} must be numeric."
            }), 400

    # Validate binary features
    for feature in [
        "hypertension",
        "heart_disease"
    ]:
        if data[feature] not in [0, 1]:
            return jsonify({
                "error": f"{feature} must be 0 or 1."
            }), 400

    # Validate categorical values
    valid_gender = [
        "Female",
        "Male",
        "Other"
    ]

    valid_smoking_history = [
        "No Info",
        "current",
        "ever",
        "former",
        "never",
        "not current"
    ]

    if data["gender"] not in valid_gender:
        return jsonify({
            "error": "Invalid gender value.",
            "allowed_values": valid_gender
        }), 400

    if data["smoking_history"] not in valid_smoking_history:
        return jsonify({
            "error": "Invalid smoking_history value.",
            "allowed_values": valid_smoking_history
        }), 400

    # Preprocessing
    processed_input = preprocessor.transform(
        input_df
    )

    # Prediction
    prediction = model.predict(
        processed_input
    )[0]

    probability = model.predict_proba(
        processed_input
    )[0, 1]

    return jsonify({
        "prediction": int(prediction),
        "confidence": round(
            float(probability),
            4
        )
    })


# =========================
# Run server
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5010,
        debug=True
    )