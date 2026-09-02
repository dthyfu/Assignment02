from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# =========================
# Load dataset
# =========================
DATA_PATH = "Womens Clothing E-Commerce Reviews.csv"

df = pd.read_csv(DATA_PATH)

# Create a stable review ID for web interaction
df["review_id"] = df.index

# =========================
# Load trained model
# =========================
MODEL_PATH = "ecommerce_model/ecommerce_final_model.pkl"
PREPROCESSOR_PATH = "ecommerce_model/ecommerce_preprocessor.pkl"

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)


# =========================
# Helper functions
# =========================
def get_product_list():
    products = (
        df.groupby("Clothing ID")
        .agg({
            "Class Name": "first",
            "Department Name": "first",
            "Division Name": "first"
        })
        .reset_index()
    )

    products = products.sort_values("Clothing ID")

    return products.to_dict("records")


def get_product_reviews(product_id):
    product_reviews = df[df["Clothing ID"] == product_id].copy()

    return product_reviews


def calculate_product_stats(product_reviews):
    total_reviews = len(product_reviews)

    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "average_rating": 0,
            "recommended_rate": 0,
            "not_recommended_rate": 0,
            "rating_counts": {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0
            }
        }

    average_rating = product_reviews["Rating"].mean()

    recommended_count = (
        product_reviews["Recommended IND"] == 1
    ).sum()

    recommended_rate = recommended_count / total_reviews * 100
    not_recommended_rate = 100 - recommended_rate

    rating_counts = (
        product_reviews["Rating"]
        .value_counts()
        .reindex([1, 2, 3, 4, 5], fill_value=0)
        .to_dict()
    )

    return {
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 2),
        "recommended_rate": round(recommended_rate, 2),
        "not_recommended_rate": round(not_recommended_rate, 2),
        "rating_counts": rating_counts
    }


def prepare_review_for_model(row):
    review_text = "" if pd.isna(row["Review Text"]) else str(row["Review Text"])
    title = "" if pd.isna(row["Title"]) else str(row["Title"])

    return pd.DataFrame({
        "Age": [int(row["Age"])],
        "Rating": [int(row["Rating"])],
        "Positive Feedback Count": [
            int(row["Positive Feedback Count"])
        ],
        "Review Length": [len(review_text)],
        "Title Length": [len(title)],
        "Has Review": [int(bool(review_text))],
        "Has Title": [int(bool(title))],
        "Division Name": [
            row["Division Name"]
            if not pd.isna(row["Division Name"])
            else None
        ],
        "Department Name": [
            row["Department Name"]
            if not pd.isna(row["Department Name"])
            else None
        ],
        "Class Name": [
            row["Class Name"]
            if not pd.isna(row["Class Name"])
            else None
        ]
    })


# =========================
# Home page
# =========================
@app.route("/", methods=["GET"])
def home():

    products = get_product_list()

    product_id = request.args.get("product_id", type=int)

    rating_filter = request.args.get(
        "rating",
        "all"
    )

    recommend_filter = request.args.get(
        "recommend",
        "all"
    )

    sort_option = request.args.get(
        "sort",
        "newest"
    )

    page = request.args.get(
        "page",
        1,
        type=int
    )

    reviews = pd.DataFrame()
    stats = None
    selected_product = None

    if product_id is not None:

        reviews = get_product_reviews(product_id)

        if len(reviews) > 0:

            selected_product = reviews.iloc[0]

            stats = calculate_product_stats(reviews)

            # =========================
            # Filtering
            # =========================

            if rating_filter != "all":
                reviews = reviews[
                    reviews["Rating"] == int(rating_filter)
                ]

            if recommend_filter == "recommended":
                reviews = reviews[
                    reviews["Recommended IND"] == 1
                ]

            elif recommend_filter == "not_recommended":
                reviews = reviews[
                    reviews["Recommended IND"] == 0
                ]

            # =========================
            # Sorting
            # =========================

            if sort_option == "rating_high":
                reviews = reviews.sort_values(
                    "Rating",
                    ascending=False
                )

            elif sort_option == "rating_low":
                reviews = reviews.sort_values(
                    "Rating",
                    ascending=True
                )

            elif sort_option == "helpful":
                reviews = reviews.sort_values(
                    "Positive Feedback Count",
                    ascending=False
                )

            else:
                reviews = reviews.sort_values(
                    "review_id",
                    ascending=False
                )

    # =========================
    # Pagination
    # =========================

    reviews_per_page = 10

    total_reviews_after_filter = len(reviews)

    total_pages = max(
        1,
        (total_reviews_after_filter + reviews_per_page - 1)
        // reviews_per_page
    )

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * reviews_per_page
    end = start + reviews_per_page

    reviews_page = reviews.iloc[start:end]

    review_list = []

    for _, row in reviews_page.iterrows():

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

        review_list.append({
            "review_id": int(row["review_id"]),
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

    return render_template(
        "ecommerce.html",
        products=products,
        selected_product=selected_product,
        product_id=product_id,
        stats=stats,
        reviews=review_list,
        rating_filter=rating_filter,
        recommend_filter=recommend_filter,
        sort_option=sort_option,
        page=page,
        total_pages=total_pages,
        total_reviews=total_reviews_after_filter
    )


# =========================
# AI prediction
# =========================
@app.route("/predict-review", methods=["POST"])
def predict_review():

    try:

        data = request.get_json()

        if not data or "review_id" not in data:
            return jsonify({
                "error": "Review ID is required"
            }), 400

        review_id = int(data["review_id"])

        review = df[
            df["review_id"] == review_id
        ]

        if review.empty:
            return jsonify({
                "error": "Review not found"
            }), 404

        row = review.iloc[0]

        # Prepare features exactly as used during training
        input_data = prepare_review_for_model(row)

        # Same preprocessing used during training
        processed_data = preprocessor.transform(input_data)

        # Prediction
        prediction = model.predict(
            processed_data
        )[0]

        probability = model.predict_proba(
            processed_data
        )[0]

        return jsonify({
            "prediction": int(prediction),
            "label": (
                "Có khả năng đề xuất"
                if prediction == 1
                else "Có khả năng không đề xuất"
            ),
            "recommended": round(
                float(probability[1]) * 100,
                2
            ),
            "not_recommended": round(
                float(probability[0]) * 100,
                2
            )
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# Run application
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5014,
        debug=True
    )