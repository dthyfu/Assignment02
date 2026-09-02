from flask import Flask, request, jsonify, render_template
from neo4j import GraphDatabase
import requests
import re


# =========================================================
# CONFIGURATION
# =========================================================

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""
DATABASE = "intelligent-system"

DIABETES_API = "http://127.0.0.1:5010"
HOUSE_PRICE_API = "http://127.0.0.1:5011"
ECOMMERCE_API = "http://127.0.0.1:5013"

app = Flask(__name__)

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# =========================================================
# HOUSE PRICE SESSION
# =========================================================

house_sessions = {}

HOUSE_FEATURES = [
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

HOUSE_QUESTIONS = {
    "Area":
        "Diện tích nhà là bao nhiêu m²?",

    "Bedrooms":
        "Số phòng ngủ là bao nhiêu?",

    "Bathrooms":
        "Số phòng tắm là bao nhiêu?",

    "Stories":
        "Số tầng là bao nhiêu?",

    "Parking":
        "Số chỗ đậu xe là bao nhiêu?",

    "Age":
        "Tuổi của căn nhà là bao nhiêu năm?",

    "City":
        "Căn nhà nằm ở thành phố nào?",

    "Furnishing":
        "Tình trạng nội thất là gì?",

    "Main Road":
        "Nhà có nằm trên đường chính không? "
        "Nhập Yes hoặc No.",

    "Guest Room":
        "Nhà có phòng khách dành cho khách không? "
        "Nhập Yes hoặc No.",

    "Basement":
        "Nhà có tầng hầm không? "
        "Nhập Yes hoặc No.",

    "Water Supply":
        "Nguồn cung cấp nước là gì?",

    "Air Conditioning":
        "Nhà có điều hòa không? "
        "Nhập Yes hoặc No.",

    "Preferred Tenant":
        "Đối tượng thuê ưu tiên là gì?",

    "Locality Rating":
        "Điểm đánh giá khu vực từ 0 đến 10 là bao nhiêu?"
}


# =========================================================
# DIABETES - NEO4J
# =========================================================

def get_symptoms():

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (d:Diabetes)-[:HAS_SYMPTOM]->(s:Symptom)
            RETURN s.name AS symptom
            ORDER BY s.name
        """)

        return [
            record["symptom"]
            for record in result
        ]


def get_foods():

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (d:Diabetes)-[:SHOULD_EAT]->(f:Food)
            RETURN f.name AS food
            ORDER BY f.name
        """)

        return [
            record["food"]
            for record in result
        ]


def get_avoid_foods():

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (d:Diabetes)-[:SHOULD_AVOID]->(f:Food)
            RETURN f.name AS food
            ORDER BY f.name
        """)

        return [
            record["food"]
            for record in result
        ]


def get_source():

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (d:Diabetes)-[:INFORMATION_FROM]->(a:Article)
                  -[:FROM_SOURCE]->(s:Source)

            RETURN
                a.title AS article,
                a.url AS url,
                s.name AS source

            LIMIT 1
        """)

        return result.single()


# =========================================================
# E-COMMERCE - NEO4J
# =========================================================

def get_total_products():

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (p:Product)
            RETURN count(p) AS total
        """)

        record = result.single()

        return record["total"] if record else 0


def get_all_categories():

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (c:Category)
            RETURN c.name AS category
            ORDER BY category
        """)

        return [
            record["category"]
            for record in result
        ]


def get_product_info_neo4j(clothing_id):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (p:Product {id: $clothing_id})

            OPTIONAL MATCH
                (p)-[:BELONGS_TO]->(c:Category)

            RETURN
                p.id AS clothing_id,
                p.class_name AS class_name,
                p.department AS department,
                p.average_rating AS average_rating,
                p.total_reviews AS total_reviews,
                p.recommended_rate AS recommended_rate,
                collect(c.name) AS categories

            LIMIT 1
        """,
        clothing_id=clothing_id)

        return result.single()


def get_product_keywords(clothing_id):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH
                (p:Product {id: $clothing_id})
                -[:HAS_REVIEW]->(r:Review)
                -[:HAS_KEYWORD]->(k:Keyword)

            RETURN
                k.name AS keyword,
                count(*) AS frequency

            ORDER BY
                frequency DESC,
                keyword

            LIMIT 5
        """,
        clothing_id=clothing_id)

        return [
            {
                "keyword": record["keyword"],
                "frequency": record["frequency"]
            }
            for record in result
        ]


def get_all_keywords():

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH
                (p:Product)
                -[:HAS_REVIEW]->(r:Review)
                -[:HAS_KEYWORD]->(k:Keyword)

            RETURN
                k.name AS keyword,
                count(*) AS frequency

            ORDER BY
                frequency DESC,
                keyword

            LIMIT 10
        """)

        return [
            {
                "keyword": record["keyword"],
                "frequency": record["frequency"]
            }
            for record in result
        ]


def get_top_products_by_rating(limit=3):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (p:Product)

            WHERE
                p.total_reviews > 0
                AND p.average_rating IS NOT NULL

            RETURN
                p.id AS clothing_id,
                p.class_name AS class_name,
                p.average_rating AS average_rating,
                p.total_reviews AS total_reviews,
                p.recommended_rate AS recommended_rate

            ORDER BY
                p.average_rating DESC,
                p.total_reviews DESC

            LIMIT $limit
        """,
        limit=limit)

        return [
            dict(record)
            for record in result
        ]


def get_top_products_by_recommended(limit=3):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (p:Product)

            WHERE
                p.total_reviews > 0
                AND p.recommended_rate IS NOT NULL

            RETURN
                p.id AS clothing_id,
                p.class_name AS class_name,
                p.average_rating AS average_rating,
                p.total_reviews AS total_reviews,
                p.recommended_rate AS recommended_rate

            ORDER BY
                p.recommended_rate DESC,
                p.total_reviews DESC

            LIMIT $limit
        """,
        limit=limit)

        return [
            dict(record)
            for record in result
        ]


def get_top_products_by_reviews(limit=3):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (p:Product)

            RETURN
                p.id AS clothing_id,
                p.class_name AS class_name,
                p.average_rating AS average_rating,
                p.total_reviews AS total_reviews,
                p.recommended_rate AS recommended_rate

            ORDER BY
                p.total_reviews DESC

            LIMIT $limit
        """,
        limit=limit)

        return [
            dict(record)
            for record in result
        ]


def search_products_by_category(
    category,
    limit=3
):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH
                (p:Product)-[:BELONGS_TO]->(c:Category)

            WHERE
                toLower(c.name)
                CONTAINS
                toLower($category)

            RETURN
                p.id AS clothing_id,
                p.class_name AS class_name,
                p.average_rating AS average_rating,
                p.total_reviews AS total_reviews,
                p.recommended_rate AS recommended_rate,
                c.name AS category

            ORDER BY
                p.average_rating DESC,
                p.total_reviews DESC

            LIMIT $limit
        """,
        category=category,
        limit=limit)

        return [
            dict(record)
            for record in result
        ]


def search_products_by_keyword(
    keyword,
    limit=5
):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH
                (p:Product)
                -[:HAS_REVIEW]->(r:Review)
                -[:HAS_KEYWORD]->(k:Keyword)

            WHERE
                toLower(k.name)
                CONTAINS
                toLower($keyword)

            WITH
                p,
                count(r) AS keyword_frequency

            RETURN
                p.id AS clothing_id,
                p.class_name AS class_name,
                p.average_rating AS average_rating,
                p.total_reviews AS total_reviews,
                keyword_frequency

            ORDER BY
                keyword_frequency DESC

            LIMIT $limit
        """,
        keyword=keyword,
        limit=limit)

        return [
            dict(record)
            for record in result
        ]


def compare_products(
    first_id,
    second_id
):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH (p1:Product {id: $first_id})
            MATCH (p2:Product {id: $second_id})

            RETURN
                p1.id AS id1,
                p1.class_name AS class1,
                p1.average_rating AS rating1,
                p1.total_reviews AS reviews1,
                p1.recommended_rate AS recommended1,

                p2.id AS id2,
                p2.class_name AS class2,
                p2.average_rating AS rating2,
                p2.total_reviews AS reviews2,
                p2.recommended_rate AS recommended2
        """,
        first_id=first_id,
        second_id=second_id)

        return result.single()


# =========================================================
# E-COMMERCE - REVIEWS
# =========================================================

def get_product_reviews_neo4j(clothing_id):

    with driver.session(database=DATABASE) as session:

        result = session.run("""
            MATCH
                (p:Product {id: $clothing_id})
                -[:HAS_REVIEW]->(r:Review)

            RETURN
                r.id AS review_id,
                r.rating AS rating,
                r.review_text AS review_text,
                r.positive_feedback AS positive_feedback,
                r.recommended AS recommended

            ORDER BY
                r.positive_feedback DESC

            LIMIT 3
        """,
        clothing_id=clothing_id)

        return [
            dict(record)
            for record in result
        ]


# =========================================================
# FORMAT HELPERS
# =========================================================

def format_recommended_rate(value):

    if value is None:
        return "N/A"

    try:

        value = float(value)

        if value <= 1:
            value *= 100

        return f"{value:.2f}%"

    except (
        ValueError,
        TypeError
    ):

        return str(value)


def short_text(text, max_length=120):

    if not text:
        return ""

    text = str(text).strip()

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."


# =========================================================
# E-COMMERCE - ANSWERS
# =========================================================

def answer_product_info(clothing_id):

    product = get_product_info_neo4j(
        clothing_id
    )

    if not product:

        return (
            f"Không tìm thấy sản phẩm {clothing_id}."
        )

    categories = product["categories"]

    category = (
        categories[0]
        if categories
        else "N/A"
    )

    return (
        f"**Sản phẩm {clothing_id} – "
        f"{product['class_name']}**\n"
        f"Rating: {product['average_rating']}/5.\n"
        f"Review: {product['total_reviews']}.\n"
        f"Recommended: "
        f"{format_recommended_rate(product['recommended_rate'])}.\n"
        f"Category: {category}."
    )


def answer_product_keywords(clothing_id):

    product = get_product_info_neo4j(
        clothing_id
    )

    if not product:

        return (
            f"Không tìm thấy sản phẩm {clothing_id}."
        )

    keywords = get_product_keywords(
        clothing_id
    )

    if not keywords:

        return (
            f"Chưa có keyword cho sản phẩm {clothing_id}."
        )

    text = ", ".join(
        item["keyword"]
        for item in keywords
    )

    return (
        f"Các từ khóa nổi bật của sản phẩm "
        f"{clothing_id}: **{text}**."
    )


def answer_product_opinion(clothing_id):

    product = get_product_info_neo4j(
        clothing_id
    )

    if not product:

        return (
            f"Không tìm thấy sản phẩm {clothing_id}."
        )

    keywords = get_product_keywords(
        clothing_id
    )

    if not keywords:

        return (
            f"Chưa đủ dữ liệu review "
            f"của sản phẩm {clothing_id}."
        )

    text = ", ".join(
        item["keyword"]
        for item in keywords[:5]
    )

    return (
        f"Khách hàng thường nhắc đến "
        f"**{text}** khi đánh giá sản phẩm "
        f"{clothing_id}."
    )


def answer_top_rating():

    products = get_top_products_by_rating(3)

    if not products:
        return "Chưa có dữ liệu rating."

    first = products[0]

    result = (
        f"Sản phẩm có rating cao nhất là "
        f"**ID {first['clothing_id']} – "
        f"{first['class_name']}**, "
        f"rating **{first['average_rating']}/5**."
    )

    if len(products) > 1:

        others = ", ".join(
            f"ID {p['clothing_id']}"
            for p in products[1:]
        )

        result += (
            f"\nMột số sản phẩm khác cũng đạt "
            f"rating cao: {others}."
        )

    return result


def answer_top_recommended():

    products = get_top_products_by_recommended(3)

    if not products:
        return "Chưa có dữ liệu Recommended."

    rate = format_recommended_rate(
        products[0]["recommended_rate"]
    )

    ids = ", ".join(
        f"ID {p['clothing_id']}"
        for p in products
    )

    return (
        f"Các sản phẩm có tỷ lệ Recommended "
        f"cao nhất đạt **{rate}**: {ids}."
    )


def answer_top_reviews():

    products = get_top_products_by_reviews(3)

    if not products:
        return "Chưa có dữ liệu review."

    first = products[0]

    result = (
        f"Sản phẩm có nhiều review nhất là "
        f"**ID {first['clothing_id']} – "
        f"{first['class_name']}**, "
        f"với **{first['total_reviews']} review**."
    )

    if len(products) > 1:

        result += (
            f"\nTiếp theo: "
            f"ID {products[1]['clothing_id']} "
            f"({products[1]['total_reviews']} review) "
            f"và ID {products[2]['clothing_id']} "
            f"({products[2]['total_reviews']} review)."
        )

    return result


def answer_categories():

    categories = get_all_categories()

    if not categories:

        return "Chưa có category."

    return (
        f"Hệ thống có **{len(categories)} category**: "
        + ", ".join(categories)
        + "."
    )


def answer_products_by_category(category):

    products = search_products_by_category(
        category,
        3
    )

    if not products:

        return (
            f"Không tìm thấy sản phẩm thuộc "
            f"category **{category}**."
        )

    lines = [
        f"Một số sản phẩm nổi bật trong "
        f"category **{category}**:"
    ]

    for product in products:

        lines.append(
            f"- **ID {product['clothing_id']} – "
            f"{product['class_name']}**, "
            f"rating {product['average_rating']}/5."
        )

    return "\n".join(lines)


def answer_products_by_keyword(keyword):

    products = search_products_by_keyword(
        keyword,
        5
    )

    if not products:

        return (
            f"Không tìm thấy sản phẩm có review "
            f"liên quan đến **{keyword}**."
        )

    ids = ", ".join(
        f"ID {p['clothing_id']}"
        for p in products
    )

    return (
        f"Có **{len(products)} sản phẩm nổi bật** "
        f"có review liên quan đến **{keyword}**: "
        f"{ids}."
    )


def answer_compare_products(
    first_id,
    second_id
):

    result = compare_products(
        first_id,
        second_id
    )

    if not result:

        return (
            "Không tìm thấy một hoặc cả hai sản phẩm."
        )

    rating1 = float(result["rating1"])
    rating2 = float(result["rating2"])

    recommended1 = format_recommended_rate(
        result["recommended1"]
    )

    recommended2 = format_recommended_rate(
        result["recommended2"]
    )

    answer = (
        f"**Sản phẩm {first_id}:** "
        f"rating {rating1:.2f}, "
        f"{result['reviews1']} review, "
        f"Recommended {recommended1}.\n"

        f"**Sản phẩm {second_id}:** "
        f"rating {rating2:.2f}, "
        f"{result['reviews2']} review, "
        f"Recommended {recommended2}."
    )

    if rating1 > rating2:

        answer += (
            f"\n→ Sản phẩm {first_id} có rating cao hơn."
        )

    elif rating2 > rating1:

        answer += (
            f"\n→ Sản phẩm {second_id} có rating cao hơn."
        )

    else:

        answer += (
            "\n→ Hai sản phẩm có rating bằng nhau."
        )

    return answer


def answer_reviews(clothing_id):

    reviews = get_product_reviews_neo4j(
        clothing_id
    )

    product = get_product_info_neo4j(
        clothing_id
    )

    if not product:

        return (
            f"Không tìm thấy sản phẩm {clothing_id}."
        )

    if not reviews:

        return (
            f"Sản phẩm {clothing_id} chưa có review."
        )

    lines = [
        f"**Sản phẩm {clothing_id}** có "
        f"{product['total_reviews']} review, "
        f"rating {product['average_rating']}/5.",
        ""
    ]

    for review in reviews:

        recommended = (
            "Có"
            if review["recommended"] == 1
            else "Không"
        )

        text = short_text(
            review["review_text"],
            100
        )

        lines.append(
            f"- Rating {review['rating']}/5, "
            f"Recommended: {recommended}. "
            f"{text}"
        )

    return "\n".join(lines)


# =========================================================
# E-COMMERCE - API
# =========================================================

def predict_review(review_id):

    try:

        response = requests.post(
            f"{ECOMMERCE_API}/predict-review",
            json={
                "review_id": review_id
            },
            timeout=10
        )

        return (
            response.json(),
            response.status_code
        )

    except requests.exceptions.RequestException as e:

        return (
            {
                "error":
                    f"Không thể kết nối E-commerce API: {str(e)}"
            },
            500
        )


def get_products_api():

    try:

        response = requests.get(
            f"{ECOMMERCE_API}/products",
            timeout=10
        )

        return (
            response.json(),
            response.status_code
        )

    except requests.exceptions.RequestException as e:

        return (
            {
                "error":
                    f"Không thể kết nối E-commerce API: {str(e)}"
            },
            500
        )


# =========================================================
# HOUSE PRICE API
# =========================================================

def house_price_prediction(data):

    try:

        response = requests.post(
            f"{HOUSE_PRICE_API}/predict",
            json=data,
            timeout=10
        )

        return (
            response.json(),
            response.status_code
        )

    except requests.exceptions.RequestException as e:

        return (
            {
                "error":
                    f"Không thể kết nối House Price API: {str(e)}"
            },
            500
        )


def start_house_prediction(session_id):

    house_sessions[session_id] = {
        "current_feature": 0,
        "data": {}
    }

    return (
        "Được. Mình sẽ giúp bạn dự đoán giá nhà.\n\n"
        + HOUSE_QUESTIONS["Area"]
    )


def process_house_prediction(
    session_id,
    answer
):

    session = house_sessions[session_id]

    current_index = session[
        "current_feature"
    ]

    feature = HOUSE_FEATURES[
        current_index
    ]

    numerical_features = [
        "Area",
        "Bedrooms",
        "Bathrooms",
        "Stories",
        "Parking",
        "Age",
        "Locality Rating"
    ]

    if feature in numerical_features:

        try:

            value = float(
                answer.strip()
            )

        except ValueError:

            return (
                "Vui lòng nhập một giá trị số.\n\n"
                + HOUSE_QUESTIONS[feature]
            )

        if feature == "Area" and value <= 0:

            return (
                "Diện tích phải lớn hơn 0.\n\n"
                + HOUSE_QUESTIONS[feature]
            )

        if feature in [
            "Bedrooms",
            "Bathrooms",
            "Stories"
        ] and value <= 0:

            return (
                "Giá trị phải lớn hơn 0.\n\n"
                + HOUSE_QUESTIONS[feature]
            )

        if feature in [
            "Parking",
            "Age"
        ] and value < 0:

            return (
                "Giá trị không được âm.\n\n"
                + HOUSE_QUESTIONS[feature]
            )

        if feature == "Locality Rating":

            if value < 0 or value > 10:

                return (
                    "Locality Rating phải từ 0 đến 10.\n\n"
                    + HOUSE_QUESTIONS[feature]
                )

        if value.is_integer():

            value = int(value)

        session["data"][feature] = value

    else:

        value = answer.strip()

        if not value:

            return (
                "Vui lòng nhập thông tin.\n\n"
                + HOUSE_QUESTIONS[feature]
            )

        binary_features = [
            "Main Road",
            "Guest Room",
            "Basement",
            "Air Conditioning"
        ]

        if feature in binary_features:

            normalized = value.lower()

            if normalized in [
                "yes",
                "y",
                "có",
                "co"
            ]:

                value = "Yes"

            elif normalized in [
                "no",
                "n",
                "không",
                "khong"
            ]:

                value = "No"

            else:

                return (
                    "Vui lòng nhập Yes hoặc No.\n\n"
                    + HOUSE_QUESTIONS[feature]
                )

        session["data"][feature] = value

    session["current_feature"] += 1

    next_index = session[
        "current_feature"
    ]

    if next_index >= len(
        HOUSE_FEATURES
    ):

        result, status = house_price_prediction(
            session["data"]
        )

        del house_sessions[
            session_id
        ]

        if status != 200:

            return result.get(
                "error",
                "Không thể dự đoán giá nhà."
            )

        price = result.get(
            "predicted_price"
        )

        if price is None:

            return (
                "API không trả về giá dự đoán."
            )

        return (
            f"Giá nhà dự đoán: "
            f"**{price:,.0f}**."
        )

    next_feature = HOUSE_FEATURES[
        next_index
    ]

    return HOUSE_QUESTIONS[
        next_feature
    ]


# =========================================================
# MAIN CHATBOT
# =========================================================

def answer_question(question):

    original_question = question

    question = question.lower().strip()


    # =====================================================
    # DIABETES
    # =====================================================

    if (
        "triệu chứng" in question
        or "dấu hiệu" in question
        or "biểu hiện" in question
    ):

        symptoms = get_symptoms()

        return (
            "Một số triệu chứng có thể gặp: "
            + ", ".join(symptoms)
            + "."
        )


    if (
        "ăn gì" in question
        or "nên ăn" in question
        or "ăn được gì" in question
    ):

        foods = get_foods()

        return (
            "Bạn có thể tham khảo: "
            + ", ".join(foods)
            + "."
        )


    if (
        "tránh gì" in question
        or "nên tránh" in question
        or "kiêng gì" in question
        or "hạn chế gì" in question
    ):

        foods = get_avoid_foods()

        return (
            "Bạn nên hạn chế: "
            + ", ".join(foods)
            + "."
        )


    if (
        "nguồn" in question
        or "lấy từ đâu" in question
        or "tham khảo ở đâu" in question
    ):

        source = get_source()

        if source:

            return (
                f"Nguồn tham khảo: "
                f"{source['source']}.\n"
                f"Bài viết: {source['article']}.\n"
                f"{source['url']}"
            )

        return "Chưa xác định được nguồn."


    # =====================================================
    # HOUSE PRICE
    # =====================================================

    if (
        "dự đoán giá nhà" in question
        or "dự đoán giá" in question
        or "house price" in question
        or "ước tính giá nhà" in question
    ):

        return start_house_prediction(
            request.remote_addr
        )


    # =====================================================
    # E-COMMERCE - COMPARE
    # =====================================================

    if (
        "so sánh" in question
        or "so sanh" in question
        or "compare" in question
    ):

        numbers = re.findall(
            r"\b\d+\b",
            original_question
        )

        if len(numbers) >= 2:

            return answer_compare_products(
                int(numbers[0]),
                int(numbers[1])
            )

        return (
            "Bạn hãy cung cấp hai Clothing ID.\n"
            "Ví dụ: So sánh sản phẩm 1078 và 1080."
        )


    # =====================================================
    # E-COMMERCE - REVIEW PREDICTION
    # =====================================================

    if (
        "dự đoán review" in question
        or "review có được recommend" in question
        or "review có được đề xuất" in question
    ):

        numbers = re.findall(
            r"\b\d+\b",
            original_question
        )

        if not numbers:

            return (
                "Bạn hãy cung cấp review_id."
            )

        review_id = int(
            numbers[0]
        )

        result, status = predict_review(
            review_id
        )

        if status != 200:

            return result.get(
                "error",
                "Không thể dự đoán review."
            )

        label = result.get(
            "label",
            "Unknown"
        )

        probability = result.get(
            "probability",
            {}
        )

        return (
            f"Review {review_id}: **{label}**.\n"
            f"Not Recommended: "
            f"{probability.get('not_recommended', 0):.2%}.\n"
            f"Recommended: "
            f"{probability.get('recommended', 0):.2%}."
        )


    # =====================================================
    # E-COMMERCE - REVIEWS
    # =====================================================

    if (
        (
            "xem review" in question
            or "xem đánh giá" in question
            or "review sản phẩm" in question
            or "đánh giá sản phẩm" in question
        )
        and re.search(
            r"\b\d+\b",
            original_question
        )
    ):

        numbers = re.findall(
            r"\b\d+\b",
            original_question
        )

        return answer_reviews(
            int(numbers[0])
        )


    # =====================================================
    # E-COMMERCE - PRODUCT KEYWORDS
    # =====================================================

    if (
        (
            "từ khóa" in question
            or "keyword" in question
        )
        and "sản phẩm" in question
    ):

        numbers = re.findall(
            r"\b\d+\b",
            original_question
        )

        if numbers:

            return answer_product_keywords(
                int(numbers[0])
            )

        keywords = get_all_keywords()

        return (
            "Một số keyword nổi bật: "
            + ", ".join(
                item["keyword"]
                for item in keywords
            )
            + "."
        )


    # =====================================================
    # E-COMMERCE - CUSTOMER OPINION
    # =====================================================

    if (
        "khách hàng thường nhận xét" in question
        or "khách hàng nhận xét" in question
        or "nhận xét gì" in question
        or "ý kiến khách hàng" in question
    ):

        numbers = re.findall(
            r"\b\d+\b",
            original_question
        )

        if numbers:

            return answer_product_opinion(
                int(numbers[0])
            )

        return (
            "Bạn hãy cung cấp Clothing ID "
            "để mình phân tích review."
        )


    # =====================================================
    # E-COMMERCE - TOP RATING
    # =====================================================

    if (
        "rating cao nhất" in question
        or "đánh giá cao nhất" in question
    ):

        return answer_top_rating()


    # =====================================================
    # E-COMMERCE - TOP RECOMMENDED
    # =====================================================

    if (
        "recommend nhiều nhất" in question
        or "được recommend nhiều nhất" in question
        or "recommend cao nhất" in question
        or "được đề xuất nhiều nhất" in question
    ):

        return answer_top_recommended()


    # =====================================================
    # E-COMMERCE - MOST REVIEWS
    # =====================================================

    if (
        "nhiều review nhất" in question
        or "nhiều đánh giá nhất" in question
    ):

        return answer_top_reviews()


    # =====================================================
    # E-COMMERCE - CATEGORIES
    # =====================================================

    if (
        "có những category nào" in question
        or "có những danh mục nào" in question
        or "danh sách category" in question
        or "các category" in question
    ):

        return answer_categories()


    # =====================================================
    # E-COMMERCE - CATEGORY
    # =====================================================

    category_match = re.search(
        r"sản phẩm\s+thuộc\s+"
        r"(?:category\s+)?"
        r"([a-zA-Z][a-zA-Z\s]*?)"
        r"[?.!]*$",
        original_question,
        re.IGNORECASE
    )

    if category_match:

        category = category_match.group(1).strip()

        return answer_products_by_category(
            category
        )


    # =====================================================
    # E-COMMERCE - KEYWORD SEARCH
    # =====================================================

    keyword_match = re.search(
        r"(?:review\s+)?"
        r"(?:nói về|liên quan đến)\s+"
        r"([a-zA-Z]+)",
        original_question,
        re.IGNORECASE
    )

    if keyword_match:

        keyword = keyword_match.group(1).strip()

        return answer_products_by_keyword(
            keyword
        )


    # =====================================================
    # E-COMMERCE - PRODUCT INFO
    # =====================================================

    if (
        (
            "thông tin sản phẩm" in question
            or "chi tiết sản phẩm" in question
            or "thông tin product" in question
        )
        and re.search(
            r"\b\d+\b",
            original_question
        )
    ):

        numbers = re.findall(
            r"\b\d+\b",
            original_question
        )

        return answer_product_info(
            int(numbers[0])
        )


    # =====================================================
    # E-COMMERCE - COUNT
    # =====================================================

    if (
        "bao nhiêu sản phẩm" in question
        or "tổng số sản phẩm" in question
        or "số lượng sản phẩm" in question
    ):

        total = get_total_products()

        return (
            f"Hệ thống hiện có **{total} sản phẩm**."
        )


    # =====================================================
    # DEFAULT
    # =====================================================

    return (
        "Mình chưa hiểu câu hỏi này.\n\n"
        "Bạn có thể hỏi về Diabetes, "
        "dự đoán giá nhà hoặc sản phẩm E-commerce."
    )


# =========================================================
# ROUTES
# =========================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json()

    if not data or "question" not in data:

        return jsonify({
            "error": "Question is required"
        }), 400

    question = str(
        data["question"]
    ).strip()

    if not question:

        return jsonify({
            "error": "Question cannot be empty"
        }), 400

    session_id = data.get(
        "session_id",
        request.remote_addr
    )

    if session_id in house_sessions:

        answer = process_house_prediction(
            session_id,
            question
        )

    else:

        answer = answer_question(
            question
        )

    return jsonify({

        "question": question,

        "answer": answer,

        "session_id": session_id
    })


@app.route(
    "/health",
    methods=["GET"]
)
def health():

    neo4j_status = "connected"

    try:

        with driver.session(
            database=DATABASE
        ) as session:

            session.run(
                "RETURN 1"
            ).single()

    except Exception:

        neo4j_status = "disconnected"

    return jsonify({

        "status": "running",

        "neo4j": neo4j_status,

        "database": DATABASE,

        "diabetes_api": DIABETES_API,

        "house_price_api": HOUSE_PRICE_API,

        "ecommerce_api": ECOMMERCE_API,

        "chatbot_port": 5016
    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CHATBOT SERVER")
    print("=" * 60)

    print(
        "Neo4j:",
        URI
    )

    print(
        "Database:",
        DATABASE
    )

    print(
        "Diabetes API:",
        DIABETES_API
    )

    print(
        "House Price API:",
        HOUSE_PRICE_API
    )

    print(
        "E-commerce API:",
        ECOMMERCE_API
    )

    print(
        "Chatbot:",
        "http://127.0.0.1:5016"
    )

    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5016,
        debug=True
    )