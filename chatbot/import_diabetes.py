from neo4j import GraphDatabase

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

print("Đã kết nối Neo4j")

def create_diabetes_data(tx):
    tx.run("""
        MERGE (d:Diabetes {name: "Diabetes"})

        MERGE (f1:Food {name: "Rau xanh"})
        SET f1.category = "Vegetable"
        MERGE (d)-[:SHOULD_EAT]->(f1)

        MERGE (f2:Food {name: "Bông cải xanh"})
        SET f2.category = "Vegetable"
        MERGE (d)-[:SHOULD_EAT]->(f2)

        MERGE (f3:Food {name: "Đồ uống có đường"})
        SET f3.category = "Sugary Drink"
        MERGE (d)-[:SHOULD_AVOID]->(f3)

        MERGE (f4:Food {name: "Bánh kẹo"})
        SET f4.category = "Sugary Food"
        MERGE (d)-[:SHOULD_AVOID]->(f4)

        MERGE (s1:Symptom {name: "Khát nước nhiều"})
        MERGE (d)-[:HAS_SYMPTOM]->(s1)

        MERGE (s2:Symptom {name: "Đi tiểu thường xuyên"})
        MERGE (d)-[:HAS_SYMPTOM]->(s2)

        MERGE (s3:Symptom {name: "Sụt cân không rõ nguyên nhân"})
        MERGE (d)-[:HAS_SYMPTOM]->(s3)

        MERGE (s4:Symptom {name: "Mệt mỏi"})
        MERGE (d)-[:HAS_SYMPTOM]->(s4)

        MERGE (s5:Symptom {name: "Nhìn mờ"})
        MERGE (d)-[:HAS_SYMPTOM]->(s5)

        MERGE (s6:Symptom {name: "Vết thương lâu lành"})
        MERGE (d)-[:HAS_SYMPTOM]->(s6)

        MERGE (s7:Symptom {name: "Đói thường xuyên"})
        MERGE (d)-[:HAS_SYMPTOM]->(s7)
    """)


with driver.session(database="intelligent-system") as session:
    session.execute_write(create_diabetes_data)

print("Đã import dữ liệu Diabetes vào Neo4j")

import requests
from bs4 import BeautifulSoup

URL = "https://nhathuoclongchau.com.vn/bai-viet/nhung-kien-thuc-lien-quan-den-benh-tieu-duong-ma-ban-can-biet-51260.html"

response = requests.get(URL, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("\nTIÊU ĐỀ:")
print(soup.title.get_text(strip=True))

print("\nCÁC MỤC TRONG BÀI:")
for heading in soup.find_all(["h2", "h3"]):
    text = heading.get_text(" ", strip=True)
    if text:
        print("-", text)

print("\nNỘI DUNG PHẦN TRIỆU CHỨNG:")

heading = soup.find(
    lambda tag: tag.name in ["h2", "h3"]
    and "Các triệu chứng tiểu đường" in tag.get_text()
)

if heading:
    for element in heading.find_all_next():
        if element.name in ["h2", "h3"] and element != heading:
            break

        text = element.get_text(" ", strip=True)

        if text:
            print(text)
else:
    print("Không tìm thấy phần triệu chứng.")

symptom_mapping = {
    "mệt mỏi": "Mệt mỏi",
    "đói": "Đói thường xuyên",
    "khát thường xuyên": "Khát nước nhiều",
    "đi tiểu nhiều lần": "Đi tiểu thường xuyên",
    "khô miệng": "Khô miệng",
    "ngứa da": "Ngứa da",
    "sụt cân": "Sụt cân không rõ nguyên nhân",
    "nhiễm trùng nấm men": "Nhiễm trùng nấm men",
    "vết thương ngoài da": "Vết thương lâu lành"
}

full_text = ""

if heading:
    for element in heading.find_all_next():
        if element.name in ["h2", "h3"] and element != heading:
            break

        text = element.get_text(" ", strip=True)

        if text:
            full_text += " " + text.lower()

found_symptoms = []

for keyword, symptom_name in symptom_mapping.items():
    if keyword in full_text:
        if symptom_name not in found_symptoms:
            found_symptoms.append(symptom_name)

print("\nCÁC TRIỆU CHỨNG TỰ ĐỘNG PHÁT HIỆN:")

for symptom in found_symptoms:
    print("-", symptom)


def import_symptoms(tx, symptoms):
    for symptom in symptoms:
        tx.run("""
            MERGE (d:Diabetes {name: "Diabetes"})
            MERGE (s:Symptom {name: $symptom})
            MERGE (d)-[:HAS_SYMPTOM]->(s)
        """, symptom=symptom)


with driver.session(database="intelligent-system") as session:
    session.execute_write(import_symptoms, found_symptoms)

print("\nĐã tự động import các triệu chứng vào Neo4j.")

food_mapping = {
    "rau củ quả": "Rau xanh",
    "trái cây": "Trái cây",
    "các loại hạt": "Các loại hạt",
    "ngũ cốc nguyên hạt": "Ngũ cốc nguyên hạt",
    "đồ uống có đường": "Đồ uống có đường",
    "bánh kẹo": "Bánh kẹo"
}

food_text = ""

for paragraph in soup.find_all("p"):
    text = paragraph.get_text(" ", strip=True)

    if any(keyword in text.lower() for keyword in food_mapping):
        food_text += " " + text.lower()

found_foods = []

for keyword, food_name in food_mapping.items():
    if keyword in food_text:
        if food_name not in found_foods:
            found_foods.append(food_name)

print("\nCÁC THỰC PHẨM TỰ ĐỘNG PHÁT HIỆN:")

for food in found_foods:
    print("-", food)

def import_foods(tx, foods):
    for food in foods:
        tx.run("""
            MERGE (d:Diabetes {name: "Diabetes"})
            MERGE (f:Food {name: $food})
            MERGE (d)-[:SHOULD_EAT]->(f)
        """, food=food)


with driver.session(database="intelligent-system") as session:
    session.execute_write(import_foods, found_foods)

print("\nĐã tự động import thực phẩm vào Neo4j.")

print("\nNỘI DUNG LIÊN QUAN ĐẾN THỰC PHẨM:")

for paragraph in soup.find_all("p"):
    text = paragraph.get_text(" ", strip=True)

    if any(keyword in text.lower() for keyword in food_mapping):
    	print("-", text)

def import_article(tx, title, url):
    tx.run("""
        MERGE (d:Diabetes {name: "Diabetes"})

        MERGE (s:Source {name: "Nhà thuốc Long Châu"})
        SET s.type = "Pharmacy Website",
            s.url = "https://nhathuoclongchau.com.vn/"

        MERGE (a:Article {url: $url})
        SET a.title = $title,
            a.type = "Health Article"

        MERGE (d)-[:INFORMATION_FROM]->(a)
        MERGE (a)-[:FROM_SOURCE]->(s)
    """, title=title, url=url)


article_title = soup.title.get_text(strip=True)

with driver.session(database="intelligent-system") as session:
    session.execute_write(
        import_article,
        article_title,
        URL
    )

print("\nĐã tự động import Article và Source vào Neo4j.")