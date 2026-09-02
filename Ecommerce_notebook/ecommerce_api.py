from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# =========================
# Paths
# =========================
DATA_PATH = "Womens Clothing E-Commerce Reviews.csv"
MODEL_PATH = "ecommerce_model/ecommerce_final_model.pkl"
PREPROCESSOR_PATH = "ecommerce_model/ecommerce_preprocessor.pkl"


# =========================
# Load data and model
# =========================
df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)


# =========================
# Home
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "E-commerce Recommendation API",
        "status": "running"
    })


# =========================
# Get products
# =========================
@app.route("/products", methods=["GET"])
def get_products():

    products = (
        df.groupby("Clothing ID")
        .agg(
            Division_Name=("Division Name", "first"),
            Department_Name=("Department Name", "first"),
            Class_Name=("Class Name", "first"),
            Total_Reviews=("Clothing ID", "size"),
            Average_Rating=("Rating", "mean"),
            Recommended_Rate=("Recommended IND", "mean")
        )
        .reset_index()
    )

    products["Average_Rating"] = (
        products["Average_Rating"]
        .round(2)
    )

    products["Recommended_Rate"] = (
        products["Recommended_Rate"] * 100
    ).round(2)

    products = products.fillna("N/A")

    return jsonify({
        "total_products": len(products),
        "products": products.to_dict("records")
    })


# =========================
# Get reviews of a product
# =========================
@app.route("/products/<int:clothing_id>/reviews", methods=["GET"])
def get_reviews(clothing_id):

    product_reviews = df[
        df["Clothing ID"] == clothing_id
    ].copy()

    if product_reviews.empty:
        return jsonify({
            "error": "Product not found"
        }), 404

    # =========================
    # Filters
    # =========================

    rating = request.args.get("rating", "all")
    recommend = request.args.get("recommend", "all")
    sort = request.args.get("sort", "newest")

    if rating != "all":
        try:
            rating_value = int(rating)

            if rating_value in [1, 2, 3, 4, 5]:
                product_reviews = product_reviews[
                    product_reviews["Rating"] == rating_value
                ]

        except ValueError:
            pass

    if recommend == "recommended":

        product_reviews = product_reviews[
            product_reviews["Recommended IND"] == 1
        ]

    elif recommend == "not_recommended":

        product_reviews = product_reviews[
            product_reviews["Recommended IND"] == 0
        ]

    # =========================
    # Sorting
    # =========================

    if sort == "rating_high":

        product_reviews = product_reviews.sort_values(
            "Rating",
            ascending=False
        )

    elif sort == "rating_low":

        product_reviews = product_reviews.sort_values(
            "Rating",
            ascending=True
        )

    elif sort == "helpful":

        product_reviews = product_reviews.sort_values(
            "Positive Feedback Count",
            ascending=False
        )

    else:

        # Original row index represents
        # the order in the dataset.
        product_reviews = product_reviews.sort_index(
            ascending=False
        )

    # =========================
    # Convert to JSON
    # =========================

    reviews = []

    for index, row in product_reviews.iterrows():

        title = (
            ""
            if pd.isna(row["Title"])
            else str(row["Title"])
        )

        review_text = (
            ""
            if pd.isna(row["Review Text"])
            else str(row["Review Text"])
        )

        reviews.append({
            "review_id": int(index),
            "age": int(row["Age"]),
            "rating": int(row["Rating"]),
            "title": title,
            "review_text": review_text,
            "positive_feedback": int(
                row["Positive Feedback Count"]
            ),
            "recommended": int(
                row["Recommended IND"]
            )
        })

    return jsonify({
        "clothing_id": clothing_id,
        "total_reviews": len(reviews),
        "reviews": reviews
    })


# =========================
# Predict a review
# =========================
@app.route("/predict-review", methods=["POST"])
def predict_review():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "JSON data is required"
            }), 400

        if "review_id" not in data:
            return jsonify({
                "error": "review_id is required"
            }), 400

        review_id = int(data["review_id"])

        if review_id not in df.index:
            return jsonify({
                "error": "Review not found"
            }), 404

        row = df.loc[review_id]

        review_text = (
            ""
            if pd.isna(row["Review Text"])
            else str(row["Review Text"])
        )

        title = (
            ""
            if pd.isna(row["Title"])
            else str(row["Title"])
        )

        input_data = pd.DataFrame({
            "Age": [int(row["Age"])],
            "Rating": [int(row["Rating"])],
            "Positive Feedback Count": [
                int(row["Positive Feedback Count"])
            ],
            "Review Length": [
                len(review_text)
            ],
            "Title Length": [
                len(title)
            ],
            "Has Review": [
                int(bool(review_text))
            ],
            "Has Title": [
                int(bool(title))
            ],
            "Division Name": [
                row["Division Name"]
            ],
            "Department Name": [
                row["Department Name"]
            ],
            "Class Name": [
                row["Class Name"]
            ]
        })

        processed_data = preprocessor.transform(
            input_data
        )

        prediction = model.predict(
            processed_data
        )[0]

        probability = model.predict_proba(
            processed_data
        )[0]

        return jsonify({
            "review_id": review_id,
            "prediction": int(prediction),
            "label": (
                "Recommended"
                if prediction == 1
                else "Not Recommended"
            ),
            "probability": {
                "not_recommended": round(
                    float(probability[0]),
                    4
                ),
                "recommended": round(
                    float(probability[1]),
                    4
                )
            }
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# Run API
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5013,
        debug=True
    )