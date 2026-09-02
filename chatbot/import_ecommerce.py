import pandas as pd
from neo4j import GraphDatabase
import re


# =========================================================
# CONFIG
# =========================================================

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"

# Thay bằng password Neo4j của bạn.
PASSWORD = ""

DATABASE = "intelligent-system"

DATA_PATH = "Womens Clothing E-Commerce Reviews.csv"


# =========================================================
# NEO4J DRIVER
# =========================================================

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# =========================================================
# LOAD DATASET
# =========================================================

print("=" * 60)
print("Loading E-commerce dataset...")
print("=" * 60)

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")
print(f"Number of reviews: {len(df)}")

# =========================================================
# CREATE CONSTRAINTS
# =========================================================

def create_constraints():

    with driver.session(
        database=DATABASE
    ) as session:

        constraints = [

            """
            CREATE CONSTRAINT product_id_unique
            IF NOT EXISTS
            FOR (p:Product)
            REQUIRE p.id IS UNIQUE
            """,

            """
            CREATE CONSTRAINT review_id_unique
            IF NOT EXISTS
            FOR (r:Review)
            REQUIRE r.id IS UNIQUE
            """,

            """
            CREATE CONSTRAINT category_name_unique
            IF NOT EXISTS
            FOR (c:Category)
            REQUIRE c.name IS UNIQUE
            """,

            """
            CREATE CONSTRAINT feature_name_unique
            IF NOT EXISTS
            FOR (f:Feature)
            REQUIRE f.name IS UNIQUE
            """,

            """
            CREATE CONSTRAINT keyword_name_unique
            IF NOT EXISTS
            FOR (k:Keyword)
            REQUIRE k.name IS UNIQUE
            """
        ]

        for query in constraints:

            try:

                session.run(query)

            except Exception as e:

                print(
                    "Constraint warning:",
                    e
                )

    print("Constraints created successfully.")

# =========================================================
# IMPORT PRODUCTS
# =========================================================

def import_products():

    products = []

    grouped = df.groupby(
        "Clothing ID"
    )

    for clothing_id, group in grouped:

        first = group.iloc[0]

        division = clean_text(
            first["Division Name"]
        )

        department = clean_text(
            first["Department Name"]
        )

        class_name = clean_text(
            first["Class Name"]
        )

        ratings = pd.to_numeric(
            group["Rating"],
            errors="coerce"
        )

        recommendations = pd.to_numeric(
            group["Recommended IND"],
            errors="coerce"
        )

        average_rating = ratings.mean()

        recommended_rate = recommendations.mean()

        products.append({

            "id": int(clothing_id),

            "division": division,

            "department": department,

            "class_name": class_name,

            "total_reviews": int(
                len(group)
            ),

            "average_rating": round(
                float(average_rating),
                2
            ),

            "recommended_rate": round(
                float(recommended_rate),
                4
            )
        })


    query = """

    UNWIND $products AS product

    MERGE (p:Product {
        id: product.id
    })

    SET
        p.division = product.division,
        p.department = product.department,
        p.class_name = product.class_name,
        p.total_reviews = product.total_reviews,
        p.average_rating = product.average_rating,
        p.recommended_rate = product.recommended_rate

    MERGE (d:Category {
        name: product.division
    })

    MERGE (dep:Category {
        name: product.department
    })

    MERGE (c:Category {
        name: product.class_name
    })

    MERGE (p)-[:BELONGS_TO]->(d)

    MERGE (p)-[:BELONGS_TO]->(dep)

    MERGE (p)-[:BELONGS_TO]->(c)

    """


    with driver.session(
        database=DATABASE
    ) as session:

        session.run(
            query,
            products=products
        )


    print(
        f"Imported {len(products)} products."
    )

# =========================================================
# HELPER FUNCTION
# =========================================================

def clean_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip()

# =========================================================
# IMPORT REVIEWS
# =========================================================

def import_reviews():

    reviews = []

    for index, row in df.iterrows():

        clothing_id = int(row["Clothing ID"])

        review_text = clean_text(
            row["Review Text"]
        )

        title = clean_text(
            row["Title"]
        )

        rating = row["Rating"]

        if pd.isna(rating):
            rating = 0
        else:
            rating = int(rating)

        recommended = row["Recommended IND"]

        if pd.isna(recommended):
            recommended = 0
        else:
            recommended = int(recommended)

        positive_feedback = row[
            "Positive Feedback Count"
        ]

        if pd.isna(positive_feedback):
            positive_feedback = 0
        else:
            positive_feedback = int(
                positive_feedback
            )

        age = row["Age"]

        if pd.isna(age):
            age = 0
        else:
            age = int(age)

        reviews.append({

            "id": int(index),

            "product_id": clothing_id,

            "age": age,

            "rating": rating,

            "title": title,

            "review_text": review_text,

            "positive_feedback": positive_feedback,

            "recommended": recommended
        })


    query = """

    UNWIND $reviews AS review

    MERGE (r:Review {
        id: review.id
    })

    SET
        r.age = review.age,
        r.rating = review.rating,
        r.title = review.title,
        r.review_text = review.review_text,
        r.positive_feedback =
            review.positive_feedback,
        r.recommended =
            review.recommended

    WITH r, review

    MATCH (p:Product {
        id: review.product_id
    })

    MERGE (r)-[:ABOUT]->(p)

    MERGE (p)-[:HAS_REVIEW]->(r)

    """

    batch_size = 1000

    with driver.session(
        database=DATABASE
    ) as session:

        for start in range(
            0,
            len(reviews),
            batch_size
        ):

            batch = reviews[
                start:start + batch_size
            ]

            session.run(
                query,
                reviews=batch
            )

            print(
                f"Imported reviews "
                f"{start + 1}-"
                f"{min(start + batch_size, len(reviews))}"
            )

    print(
        f"Imported {len(reviews)} reviews."
    )

# =========================================================
# IMPORT FEATURES
# =========================================================

def import_features():

    features = [
        "Age",
        "Rating",
        "Positive Feedback Count",
        "Review Length",
        "Title Length",
        "Has Review",
        "Has Title",
        "Recommended"
    ]

    query = """

    UNWIND $features AS feature

    MERGE (f:Feature {
        name: feature
    })

    """

    with driver.session(
        database=DATABASE
    ) as session:

        session.run(
            query,
            features=features
        )

    print(
        f"Imported {len(features)} features."
    )

# =========================================================
# EXTRACT KEYWORDS
# =========================================================

STOP_WORDS = {
    "the",
    "and",
    "for",
    "this",
    "that",
    "with",
    "was",
    "are",
    "have",
    "has",
    "had",
    "very",
    "but",
    "not",
    "you",
    "your",
    "they",
    "them",
    "from",
    "would",
    "could",
    "about",
    "just",
    "dress",
    "top",
    "size",
    "like",
    "look",
    "looks",
    "wear",
    "wearing"
}


def extract_keywords(text):

    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        text.lower()
    )

    keywords = []

    for word in words:

        if word in STOP_WORDS:
            continue

        if word not in keywords:
            keywords.append(word)

        if len(keywords) >= 10:
            break

    return keywords

# =========================================================
# IMPORT KEYWORDS
# =========================================================

def import_keywords():

    keyword_rows = []

    for index, row in df.iterrows():

        review_text = clean_text(
            row["Review Text"]
        )

        if not review_text:
            continue

        keywords = extract_keywords(
            review_text
        )

        for keyword in keywords:

            keyword_rows.append({
                "review_id": int(index),
                "keyword": keyword
            })


    query = """

    UNWIND $rows AS row

    MATCH (r:Review {
        id: row.review_id
    })

    MERGE (k:Keyword {
        name: row.keyword
    })

    MERGE (r)-[:HAS_KEYWORD]->(k)

    """


    batch_size = 1000

    with driver.session(
        database=DATABASE
    ) as session:

        for start in range(
            0,
            len(keyword_rows),
            batch_size
        ):

            batch = keyword_rows[
                start:start + batch_size
            ]

            session.run(
                query,
                rows=batch
            )

            print(
                f"Imported keyword relations "
                f"{start + 1}-"
                f"{min(start + batch_size, len(keyword_rows))}"
            )


    print(
        f"Imported {len(keyword_rows)} "
        f"keyword relations."
    )

# =========================================================
# RUN IMPORT
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("E-COMMERCE KNOWLEDGE GRAPH")
    print("=" * 60)

    print()
    print("Creating constraints...")

    create_constraints()

    print()
    print("Importing products...")

    import_products()

    print()
    print("Product import completed.")

    print()
    print("Importing reviews...")

    import_reviews()

    print()
    print("Review import completed.")

    print()
    print("Importing features...")

    import_features()

    print()
    print("Feature import completed.")

    print()
    print("Importing keywords...")

    import_keywords()

    print()
    print("Keyword import completed.")