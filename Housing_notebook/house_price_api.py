from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os

app = Flask(__name__)

# =========================
# Load model, preprocessor and dataset
# =========================

MODEL_PATH = os.path.join(
    "saved_model",
    "house_price_model.pkl"
)

PREPROCESSOR_PATH = os.path.join(
    "saved_model",
    "preprocessor.pkl"
)

DATA_PATH = os.path.join(
    "enhanced_house_price_dataset.csv"
)

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)
df = pd.read_csv(DATA_PATH)


# =========================
# Expected input features
# =========================

FEATURES = [
    "Area",
    "Bedrooms",
    "Bathrooms",
    "Stories",
    "Parking",
    "Age",
    "City",
    "Furnishing",
    "Main Road",
    "Guest Room",
    "Basement",
    "Water Supply",
    "Air Conditioning",
    "Preferred Tenant",
    "Locality Rating"
]

NUMERICAL_FEATURES = [
    "Area",
    "Bedrooms",
    "Bathrooms",
    "Stories",
    "Parking",
    "Age",
    "Locality Rating"
]


# =========================
# Home endpoint
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "House Price Prediction API is running"
    })


# =========================
# Dataset endpoint
# =========================

@app.route("/dataset", methods=["GET"])
def dataset():
    rows = df[
        [
            "City",
            "Area",
            "Bedrooms",
            "Bathrooms",
            "Stories",
            "Furnishing",
            "Age",
            "Price"
        ]
    ].to_dict(orient="records")

    return jsonify(rows)


# =========================
# Prediction endpoint
# =========================

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if data is None:
            return jsonify({
                "error": "Request body must be valid JSON"
            }), 400

        # Check missing features
        missing_features = [
            feature for feature in FEATURES
            if feature not in data
        ]

        if missing_features:
            return jsonify({
                "error": "Missing required features",
                "missing_features": missing_features
            }), 400

        # Keep only expected features
        input_data = {
            feature: data[feature]
            for feature in FEATURES
        }

        # Convert input to DataFrame
        input_df = pd.DataFrame([input_data])

        # Validate numerical values
        for feature in NUMERICAL_FEATURES:
            try:
                input_df[feature] = pd.to_numeric(
                    input_df[feature]
                )
            except (ValueError, TypeError):
                return jsonify({
                    "error": f"{feature} must be a numeric value"
                }), 400

        # Validate numerical ranges
        if input_df["Area"].iloc[0] <= 0:
            return jsonify({
                "error": "Area must be greater than 0"
            }), 400

        if input_df["Bedrooms"].iloc[0] <= 0:
            return jsonify({
                "error": "Bedrooms must be greater than 0"
            }), 400

        if input_df["Bathrooms"].iloc[0] <= 0:
            return jsonify({
                "error": "Bathrooms must be greater than 0"
            }), 400

        if input_df["Stories"].iloc[0] <= 0:
            return jsonify({
                "error": "Stories must be greater than 0"
            }), 400

        if input_df["Parking"].iloc[0] < 0:
            return jsonify({
                "error": "Parking cannot be negative"
            }), 400

        if input_df["Age"].iloc[0] < 0:
            return jsonify({
                "error": "Age cannot be negative"
            }), 400

        locality_rating = input_df["Locality Rating"].iloc[0]

        if locality_rating < 0 or locality_rating > 10:
            return jsonify({
                "error": "Locality Rating must be between 0 and 10"
            }), 400

        # =========================
        # Preprocessing
        # =========================

        processed_data = preprocessor.transform(input_df)

        # =========================
        # Prediction
        # =========================

        prediction = model.predict(processed_data)[0]

        return jsonify({
            "predicted_price": float(prediction)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# =========================
# Run Flask
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5011,
        debug=True
    )