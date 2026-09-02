from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)

# 1. Tải Model & Preprocessor đã huấn luyện
preprocessor = joblib.load('saved_model/preprocessor.pkl')
model = joblib.load('saved_model/house_price_model.pkl')

features = [
    'Area',
    'Bedrooms',
    'Bathrooms',
    'Stories',
    'Parking',
    'Age',
    'City',
    'Furnishing',
    'Main Road',
    'Guest Room',
    'Basement',
    'Water Supply',
    'Air Conditioning',
    'Preferred Tenant',
    'Locality Rating'
]

# 2. Tải Dataset
raw_df = pd.read_csv('enhanced_house_price_dataset.csv')

dataset = raw_df[
    [
        'City',
        'Area',
        'Bedrooms',
        'Bathrooms',
        'Stories',
        'Parking',
        'Age',
        'Furnishing',
        'Main Road',
        'Guest Room',
        'Basement',
        'Water Supply',
        'Air Conditioning',
        'Preferred Tenant',
        'Locality Rating',
        'Price'
    ]
].copy()


# 3. Xử lý dữ liệu thiếu
numerical_features = [
    'Area',
    'Bedrooms',
    'Bathrooms',
    'Stories',
    'Parking',
    'Age',
    'Locality Rating'
]

for col in numerical_features:
    dataset[col] = dataset[col].fillna(dataset[col].median())

dataset = dataset.dropna(subset=['Price', 'City'])


# 4. Danh sách thành phố
CITIES = ['Toàn quốc'] + sorted(
    dataset['City'].dropna().unique().tolist()
)


# 5. Giao diện
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Dự đoán giá nhà</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
          rel="stylesheet">

    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
          rel="stylesheet">

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet">


    <style>

        * {
            font-family: 'Inter', -apple-system, sans-serif;
        }

        body {
            background-color: #f8fafc;
            color: #1e293b;
        }

        .main-container {
            max-width: 1150px;
            margin: 30px auto;
            padding: 0 15px;
        }

        .card-custom {
            background: #ffffff;
            border-radius: 14px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        }

        .form-label {
            font-size: 13.5px;
            font-weight: 600;
            color: #475569;
            margin-bottom: 5px;
        }

        .form-control,
        .form-select {
            height: 44px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            font-size: 14px;
        }

        .form-control:focus,
        .form-select:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
        }

        .result-panel {
            background: linear-gradient(
                145deg,
                #ffffff 0%,
                #f1f5f9 100%
            );

            border-radius: 14px;
            border: 1px solid #cbd5e1;

            padding: 24px;

            height: 100%;

            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .price-highlight {
            font-size: 2.2rem;
            font-weight: 800;
            color: #0f172a;
        }

        .price-text {
            color: #2563eb;
            font-weight: 700;
            font-size: 1.15rem;
        }

        .market-range {
            background: #ffffff;
            border-radius: 8px;
            padding: 10px 14px;
            border: 1px dashed #cbd5e1;
            font-size: 13px;
        }

        .table-custom th {
            background-color: #f1f5f9;
            font-size: 12px;
            font-weight: 700;
            color: #475569;
            white-space: nowrap;
        }

        .table-custom td {
            font-size: 13px;
            white-space: nowrap;
        }

    </style>

</head>


<body>


<div class="main-container">


    <!-- TIÊU ĐỀ -->

    <div class="text-center mb-4">

        <h3 class="fw-bold text-dark mb-1">

            <i class="bi bi-buildings-fill text-primary me-2"></i>

            Dự đoán giá nhà

        </h3>


        <p class="text-muted small">

            Dự đoán giá nhà bằng mô hình học máy

        </p>

    </div>



    <div class="row g-4 mb-4">


        <!-- CỘT TRÁI -->

        <div class="col-lg-7">


            <div class="card card-custom p-4">


                <div class="d-flex justify-content-between align-items-center mb-3">


                    <h6 class="fw-bold text-dark mb-0">

                        <i class="bi bi-sliders text-primary me-2"></i>

                        Thông tin căn nhà

                    </h6>


                    <span class="badge bg-light text-secondary border">

                        15 đặc trưng

                    </span>


                </div>



                <form method="POST" action="/">


                    <div class="row g-3">


                        <!-- THÀNH PHỐ -->

                        <div class="col-12">

                            <label class="form-label text-primary">

                                <i class="bi bi-geo-alt-fill me-1"></i>

                                Thành phố

                            </label>


                            <select name="city"
                                    class="form-select fw-semibold"
                                    required>
                            
                                {% for c in cities %}
                            
                                <option value="{{ c }}"
                                    {% if inputs and inputs.City == c %}
                                    selected
                                    {% endif %}>
                            
                                    {{ c }}
                            
                                </option>
                            
                                {% endfor %}
                            
                            </select>

                        </div>



                        <!-- DIỆN TÍCH -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Diện tích (m²)

                            </label>


                            <input type="number"
                                   step="0.1"
                                   name="area"
                                   class="form-control"
                                   placeholder="Ví dụ: 1260"
                                   value="{{ inputs.Area if inputs else '' }}"
                                   required>

                        </div>



                        <!-- PHÒNG NGỦ -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Số phòng ngủ

                            </label>


                            <input type="number"
                                   name="bedrooms"
                                   class="form-control"
                                   placeholder="Ví dụ: 4"
                                   value="{{ inputs.Bedrooms if inputs else '' }}"
                                   required>

                        </div>



                        <!-- PHÒNG TẮM -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Số phòng tắm

                            </label>


                            <input type="number"
                                   name="bathrooms"
                                   class="form-control"
                                   placeholder="Ví dụ: 3"
                                   value="{{ inputs.Bathrooms if inputs else '' }}"
                                   required>

                        </div>



                        <!-- SỐ TẦNG -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Số tầng

                            </label>


                            <input type="number"
                                   name="stories"
                                   class="form-control"
                                   placeholder="Ví dụ: 2"
                                   value="{{ inputs.Stories if inputs else '' }}"
                                   required>

                        </div>



                        <!-- CHỖ ĐẬU XE -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Chỗ đậu xe

                            </label>


                            <input type="number"
                                   name="parking"
                                   class="form-control"
                                   placeholder="Ví dụ: 1"
                                   value="{{ inputs.Parking if inputs else '' }}"
                                   required>

                        </div>



                        <!-- TUỔI NHÀ -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Tuổi nhà

                            </label>


                            <input type="number"
                                   step="0.1"
                                   name="age"
                                   class="form-control"
                                   placeholder="Ví dụ: 24"
                                   value="{{ inputs.Age if inputs else '' }}"
                                   required>

                        </div>



                        <!-- NỘI THẤT -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Nội thất

                            </label>


                            <select name="furnishing"
                                    class="form-select"
                                    required>
                            
                                <option value="Unfurnished"
                                    {% if inputs and inputs.Furnishing == 'Unfurnished' %}
                                    selected
                                    {% endif %}>
                                    Không nội thất
                                </option>
                            
                                <option value="Semi-Furnished"
                                    {% if inputs and inputs.Furnishing == 'Semi-Furnished' %}
                                    selected
                                    {% endif %}>
                                    Nội thất cơ bản
                                </option>
                            
                                <option value="Furnished"
                                    {% if inputs and inputs.Furnishing == 'Furnished' %}
                                    selected
                                    {% endif %}>
                                    Đầy đủ nội thất
                                </option>
                            
                            </select>

                        </div>



                        <!-- ĐƯỜNG CHÍNH -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Đường chính

                            </label>


                            <select name="main_road"
                                    class="form-select"
                                    required>
                            
                                <option value="Yes"
                                    {% if inputs and inputs['Main Road'] == 'Yes' %}
                                    selected
                                    {% endif %}>
                                    Có
                                </option>
                            
                                <option value="No"
                                    {% if inputs and inputs['Main Road'] == 'No' %}
                                    selected
                                    {% endif %}>
                                    Không
                                </option>
                            
                            </select>

                        </div>



                        <!-- PHÒNG KHÁCH -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Phòng khách

                            </label>


                            <select name="guest_room"
                                    class="form-select"
                                    required>
                            
                                <option value="Yes"
                                    {% if inputs and inputs['Guest Room'] == 'Yes' %}
                                    selected
                                    {% endif %}>
                                    Có
                                </option>
                            
                                <option value="No"
                                    {% if inputs and inputs['Guest Room'] == 'No' %}
                                    selected
                                    {% endif %}>
                                    Không
                                </option>
                            
                            </select>

                        </div>



                        <!-- TẦNG HẦM -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Tầng hầm

                            </label>


                            <select name="basement"
                                    class="form-select"
                                    required>
                            
                                <option value="Yes"
                                    {% if inputs and inputs['Basement'] == 'Yes' %}
                                    selected
                                    {% endif %}>
                                    Có
                                </option>
                            
                                <option value="No"
                                    {% if inputs and inputs['Basement'] == 'No' %}
                                    selected
                                    {% endif %}>
                                    Không
                                </option>
                            
                            </select>

                        </div>



                        <!-- NGUỒN NƯỚC -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Nguồn nước

                            </label>


                            <select name="water_supply"
                                    class="form-select"
                                    required>
                            
                                <option value="Both"
                                    {% if inputs and inputs['Water Supply'] == 'Both' %}
                                    selected
                                    {% endif %}>
                                    Cả hai
                                </option>
                            
                                <option value="Corporation"
                                    {% if inputs and inputs['Water Supply'] == 'Corporation' %}
                                    selected
                                    {% endif %}>
                                    Nước máy
                                </option>
                            
                                <option value="Borewell"
                                    {% if inputs and inputs['Water Supply'] == 'Borewell' %}
                                    selected
                                    {% endif %}>
                                    Giếng khoan
                                </option>
                            
                            </select>

                        </div>



                        <!-- ĐIỀU HÒA -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Điều hòa

                            </label>


                            <select name="air_conditioning"
                                    class="form-select"
                                    required>
                            
                                <option value="Yes"
                                    {% if inputs and inputs['Air Conditioning'] == 'Yes' %}
                                    selected
                                    {% endif %}>
                                    Có
                                </option>
                            
                                <option value="No"
                                    {% if inputs and inputs['Air Conditioning'] == 'No' %}
                                    selected
                                    {% endif %}>
                                    Không
                                </option>
                            
                            </select>

                        </div>



                        <!-- ĐỐI TƯỢNG THUÊ -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Đối tượng thuê

                            </label>


                            <select name="preferred_tenant"
                                    class="form-select"
                                    required>
                            
                                <option value="Family"
                                    {% if inputs and inputs['Preferred Tenant'] == 'Family' %}
                                    selected
                                    {% endif %}>
                                    Gia đình
                                </option>
                            
                                <option value="Company"
                                    {% if inputs and inputs['Preferred Tenant'] == 'Company' %}
                                    selected
                                    {% endif %}>
                                    Công ty
                                </option>
                            
                                <option value="Bachelor"
                                    {% if inputs and inputs['Preferred Tenant'] == 'Bachelor' %}
                                    selected
                                    {% endif %}>
                                    Người độc thân
                                </option>
                            
                            </select>

                        </div>



                        <!-- ĐÁNH GIÁ KHU VỰC -->

                        <div class="col-sm-6">

                            <label class="form-label">

                                Đánh giá khu vực (0-10)

                            </label>


                            <input type="number"
                                   step="0.1"
                                   min="0"
                                   max="10"
                                   name="locality_rating"
                                   class="form-control"
                                   placeholder="Ví dụ: 4"
                                   value="{{ inputs['Locality Rating'] if inputs else '' }}"
                                   required>

                        </div>


                    </div>



                    <!-- LỌC GIÁ -->

                    <div class="row g-2 mt-3 pt-3 border-top">

                        <div class="col-12">

                            <small class="text-muted fw-bold">

                                <i class="bi bi-funnel me-1"></i>

                                Lọc danh sách theo khoảng giá (tùy chọn)

                            </small>

                        </div>


                        <div class="col-sm-6">

                            <input type="number"
                                   step="0.1"
                                   name="min_price"
                                   class="form-control"
                                   style="height:40px; font-size:13.5px;"
                                   placeholder="Giá tối thiểu (₹)"
                                   value="{{ filters.min_price if filters and filters.min_price else '' }}">

                        </div>


                        <div class="col-sm-6">

                            <input type="number"
                                   step="0.1"
                                   name="max_price"
                                   class="form-control"
                                   style="height:40px; font-size:13.5px;"
                                   placeholder="Giá tối đa (₹)"
                                   value="{{ filters.max_price if filters and filters.max_price else '' }}">

                        </div>

                    </div>



                    <!-- NÚT -->

                    <div class="d-flex gap-2 mt-4">


                        <button type="submit"
                                class="btn btn-primary flex-grow-1 fw-bold py-2">

                            <i class="bi bi-calculator me-1"></i>

                            Dự đoán giá

                        </button>


                        <a href="{{ url_for('reset') }}"
                           class="btn btn-light border px-4 py-2 text-secondary fw-semibold">

                            <i class="bi bi-arrow-counterclockwise me-1"></i>

                            Xóa dữ liệu

                        </a>


                    </div>

                </form>

            </div>

        </div>



        <!-- CỘT PHẢI: KẾT QUẢ -->

        <div class="col-lg-5">

            <div class="result-panel">


                {% if predicted_raw is not none %}


                    <div class="text-secondary small fw-bold text-uppercase mb-1">

                        <i class="bi bi-check-circle-fill text-success me-1"></i>

                        Giá dự đoán tại {{ inputs.City }}

                    </div>


                    <div class="price-highlight">

                        {{ predicted_formatted }}

                    </div>


                    <div class="price-text mb-3">

                        Giá dự đoán theo mô hình

                    </div>


                    {% if market_min is not none and market_max is not none %}

                    <div class="market-range mb-3">

                        <div class="text-muted small mb-1">

                            Khoảng giá của các căn nhà tương tự:

                        </div>


                        <div class="fw-bold text-dark">

                            ₹{{ "{:,.0f}".format(market_min) }}

                            &nbsp;&mdash;&nbsp;

                            ₹{{ "{:,.0f}".format(market_max) }}

                        </div>

                    </div>

                    {% endif %}


                    <div class="small text-muted">

                        <i class="bi bi-info-circle me-1"></i>

                        Giá được dự đoán bởi mô hình học máy.

                    </div>


                {% else %}


                    <div class="text-center py-4 text-muted">


                        <i class="bi bi-house display-4 text-secondary mb-2 opacity-50"></i>


                        <h6 class="fw-bold text-dark mt-2">

                            Chưa có kết quả

                        </h6>


                        <p class="small mb-0">

                            Nhập thông tin căn nhà và bấm

                            <b>"Dự đoán giá"</b>

                            để xem kết quả.

                        </p>


                    </div>


                {% endif %}


            </div>

        </div>

    </div>



    <!-- BẢNG DATASET -->

    {% if matched_houses is not none %}


    <div class="card card-custom p-4">


        <div class="d-flex justify-content-between align-items-center mb-3">


            <div>


                <h6 class="fw-bold text-dark mb-1">

                    <i class="bi bi-house-fill text-danger me-2"></i>

                    Các căn nhà phù hợp trong Dataset

                </h6>


                <span class="text-muted small">

                    Thành phố:

                    <b>{{ inputs.City }}</b>

                </span>


            </div>


            <span class="badge bg-primary px-3 py-2">

                Tìm thấy {{ matched_houses|length }} căn

            </span>


        </div>



        {% if matched_houses %}


        <div class="table-responsive">


            <table class="table table-custom table-hover align-middle mb-0">


                <thead>

                    <tr>

                        <th>Thành phố</th>

                        <th>Diện tích</th>

                        <th>Phòng ngủ</th>

                        <th>Phòng tắm</th>

                        <th>Số tầng</th>

                        <th>Chỗ đậu xe</th>

                        <th>Tuổi nhà</th>

                        <th>Nội thất</th>

                        <th>Đường chính</th>

                        <th>Phòng khách</th>

                        <th>Tầng hầm</th>

                        <th>Nguồn nước</th>

                        <th>Điều hòa</th>

                        <th>Đối tượng thuê</th>

                        <th>Đánh giá khu vực</th>

                        <th>Giá nhà</th>

                    </tr>

                </thead>



                <tbody>


                    {% for item in matched_houses %}


                    <tr>


                        <td class="fw-semibold">

                            {{ item['City'] }}

                        </td>


                        <td class="text-center">

                            {{ item['Area'] }} m²

                        </td>


                        <td class="text-center">

                            {{ item['Bedrooms'] }}

                        </td>


                        <td class="text-center">

                            {{ item['Bathrooms'] }}

                        </td>


                        <td class="text-center">

                            {{ item['Stories'] }}

                        </td>


                        <td class="text-center">

                            {{ item['Parking'] }}

                        </td>


                        <td class="text-center">

                            {{ item['Age'] }}

                        </td>


                        <td>

                            {% if item['Furnishing'] == 'Furnished' %}

                                Đầy đủ nội thất

                            {% elif item['Furnishing'] == 'Semi-Furnished' %}

                                Nội thất cơ bản

                            {% else %}

                                Không nội thất

                            {% endif %}

                        </td>


                        <td class="text-center">

                            {% if item['Main Road'] == 'Yes' %}

                                Có

                            {% else %}

                                Không

                            {% endif %}

                        </td>


                        <td class="text-center">

                            {% if item['Guest Room'] == 'Yes' %}

                                Có

                            {% else %}

                                Không

                            {% endif %}

                        </td>


                        <td class="text-center">

                            {% if item['Basement'] == 'Yes' %}

                                Có

                            {% else %}

                                Không

                            {% endif %}

                        </td>


                        <td>

                            {% if item['Water Supply'] == 'Both' %}

                                Cả hai

                            {% elif item['Water Supply'] == 'Corporation' %}

                                Nước máy

                            {% else %}

                                Giếng khoan

                            {% endif %}

                        </td>


                        <td class="text-center">

                            {% if item['Air Conditioning'] == 'Yes' %}

                                Có

                            {% else %}

                                Không

                            {% endif %}

                        </td>


                        <td>

                            {% if item['Preferred Tenant'] == 'Family' %}

                                Gia đình

                            {% elif item['Preferred Tenant'] == 'Company' %}

                                Công ty

                            {% else %}

                                Người độc thân

                            {% endif %}

                        </td>


                        <td class="text-center">

                            {{ item['Locality Rating'] }}

                        </td>


                        <td class="text-center fw-bold text-success">

                            ₹{{ "{:,.0f}".format(item['Price']) }}

                        </td>


                    </tr>


                    {% endfor %}


                </tbody>

            </table>

        </div>


        {% else %}


        <div class="text-center py-4 text-muted">

            <i class="bi bi-search display-6 opacity-50 mb-2"></i>

            <p class="mb-0">

                Không tìm thấy căn nhà phù hợp.

            </p>

        </div>


        {% endif %}


    </div>

    {% endif %}


</div>


</body>

</html>
"""


# 6. Định dạng giá
def format_real_price(price):

    return f"₹{price:,.0f}"


# 7. Tìm các căn nhà tương tự
def find_similar_houses(user_inputs, filters, top_n=8):

    # Lọc theo thành phố
    if user_inputs['City'] != 'Toàn quốc':

        subset = dataset[
            dataset['City'] == user_inputs['City']
        ].copy()

        if len(subset) == 0:
            subset = dataset.copy()

    else:

        subset = dataset.copy()


    # Lọc theo khoảng giá
    if filters.get('min_price') is not None:

        subset = subset[
            subset['Price'] >= filters['min_price']
        ]


    if filters.get('max_price') is not None:

        subset = subset[
            subset['Price'] <= filters['max_price']
        ]


    if len(subset) == 0:

        return []


    # Các đặc trưng số dùng để tìm căn tương tự
    similarity_features = [
        'Area',
        'Bedrooms',
        'Bathrooms',
        'Stories',
        'Parking',
        'Age',
        'Locality Rating'
    ]


    input_df = pd.DataFrame([[
        user_inputs['Area'],
        user_inputs['Bedrooms'],
        user_inputs['Bathrooms'],
        user_inputs['Stories'],
        user_inputs['Parking'],
        user_inputs['Age'],
        user_inputs['Locality Rating']
    ]], columns=similarity_features)


    # Chuẩn hóa dữ liệu để tính khoảng cách
    from sklearn.preprocessing import StandardScaler

    similarity_scaler = StandardScaler()


    combined = pd.concat(
        [
            subset[similarity_features],
            input_df
        ],
        ignore_index=True
    )


    combined_scaled = similarity_scaler.fit_transform(
        combined
    )


    subset_scaled = combined_scaled[:-1]

    input_scaled = combined_scaled[-1]


    distances = np.linalg.norm(
        subset_scaled - input_scaled,
        axis=1
    )


    top_indices = np.argsort(distances)[:top_n]


    return subset.iloc[
        top_indices
    ].to_dict(
        orient='records'
    )


# 8. Route chính
@app.route("/", methods=["GET", "POST"])
def index():

    predicted_raw = None

    predicted_formatted = None

    market_min = None

    market_max = None

    matched_houses = None

    user_inputs = None

    filters = {}


    if request.method == "POST":


        user_inputs = {

            'City': request.form.get(
                "city",
                "Pune"
            ),

            'Area': float(
                request.form.get(
                    "area",
                    0
                )
            ),

            'Bedrooms': int(
                request.form.get(
                    "bedrooms",
                    1
                )
            ),

            'Bathrooms': int(
                request.form.get(
                    "bathrooms",
                    1
                )
            ),

            'Stories': int(
                request.form.get(
                    "stories",
                    1
                )
            ),

            'Parking': int(
                request.form.get(
                    "parking",
                    0
                )
            ),

            'Age': float(
                request.form.get(
                    "age",
                    0
                )
            ),

            'Furnishing': request.form.get(
                "furnishing",
                "Unfurnished"
            ),

            'Main Road': request.form.get(
                "main_road",
                "Yes"
            ),

            'Guest Room': request.form.get(
                "guest_room",
                "No"
            ),

            'Basement': request.form.get(
                "basement",
                "No"
            ),

            'Water Supply': request.form.get(
                "water_supply",
                "Corporation"
            ),

            'Air Conditioning': request.form.get(
                "air_conditioning",
                "No"
            ),

            'Preferred Tenant': request.form.get(
                "preferred_tenant",
                "Family"
            ),

            'Locality Rating': float(
                request.form.get(
                    "locality_rating",
                    5
                )
            )

        }


        # Bộ lọc giá
        min_p = request.form.get(
            "min_price",
            ""
        ).strip()


        max_p = request.form.get(
            "max_price",
            ""
        ).strip()


        filters = {

            'min_price':
                float(min_p)
                if min_p
                else None,

            'max_price':
                float(max_p)
                if max_p
                else None

        }


        # 9. Tạo dữ liệu đầu vào cho model
        df_input = pd.DataFrame([[
            user_inputs['Area'],
            user_inputs['Bedrooms'],
            user_inputs['Bathrooms'],
            user_inputs['Stories'],
            user_inputs['Parking'],
            user_inputs['Age'],
            user_inputs['City'],
            user_inputs['Furnishing'],
            user_inputs['Main Road'],
            user_inputs['Guest Room'],
            user_inputs['Basement'],
            user_inputs['Water Supply'],
            user_inputs['Air Conditioning'],
            user_inputs['Preferred Tenant'],
            user_inputs['Locality Rating']
        ]], columns=features)


        # 10. Tiền xử lý
        processed_input = preprocessor.transform(
            df_input
        )


        # 11. Dự đoán
        ml_pred = model.predict(
            processed_input
        )[0]


        # 12. Tìm các căn nhà tương tự
        matched_houses = find_similar_houses(
            user_inputs,
            filters,
            top_n=8
        )


        # Giá dự đoán chính thức
        predicted_raw = ml_pred


        predicted_formatted = format_real_price(
            predicted_raw
        )


        # Khoảng giá tham khảo
        if matched_houses:

            similar_prices = [
                house['Price']
                for house in matched_houses
            ]


            market_min = min(
                similar_prices
            )


            market_max = max(
                similar_prices
            )


    return render_template_string(

        HTML_TEMPLATE,

        cities=CITIES,

        inputs=user_inputs,

        filters=filters,

        predicted_raw=predicted_raw,

        predicted_formatted=predicted_formatted,

        market_min=market_min,

        market_max=market_max,

        matched_houses=matched_houses

    )


# 13. Reset
@app.route("/reset")
def reset():

    return redirect(
        url_for('index')
    )


# 14. Chạy Web
if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5012,
        debug=True
    )