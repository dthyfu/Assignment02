import React, { useEffect, useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Alert,
} from "react-native";

const API_URL = "http://192.168.1.15:5013";

export default function App() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [reviews, setReviews] = useState([]);

  const [searchText, setSearchText] = useState("");

  const [ratingFilter, setRatingFilter] = useState("all");
  const [recommendFilter, setRecommendFilter] = useState("all");
  const [sortOption, setSortOption] = useState("newest");

  const [loadingProducts, setLoadingProducts] = useState(true);
  const [loadingReviews, setLoadingReviews] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  // =========================
  // Load products
  // =========================

  const loadProducts = async () => {
    try {
      setLoadingProducts(true);

      const response = await fetch(
        `${API_URL}/products`
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      setProducts(data.products || []);

    } catch (error) {

      console.log(
        "Load products error:",
        error
      );

      Alert.alert(
        "Lỗi kết nối",
        "Không thể tải danh sách sản phẩm."
      );

    } finally {
      setLoadingProducts(false);
    }
  };


  // =========================
  // Load reviews
  // =========================

  const loadReviews = async (
    productId,
    rating = ratingFilter,
    recommend = recommendFilter,
    sort = sortOption
  ) => {

    try {

      setLoadingReviews(true);

      const url =
        `${API_URL}/products/${productId}/reviews` +
        `?rating=${rating}` +
        `&recommend=${recommend}` +
        `&sort=${sort}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      setReviews(data.reviews || []);

    } catch (error) {

      console.log(
        "Load reviews error:",
        error
      );

      Alert.alert(
        "Lỗi",
        "Không thể tải đánh giá."
      );

    } finally {

      setLoadingReviews(false);

    }
  };


  // =========================
  // Select product
  // =========================

  const selectProduct = (product) => {

    setSelectedProduct(product);

    setRatingFilter("all");
    setRecommendFilter("all");
    setSortOption("newest");

    loadReviews(
      product["Clothing ID"],
      "all",
      "all",
      "newest"
    );
  };


  // =========================
  // Apply filters
  // =========================

  const applyFilters = (
    rating,
    recommend,
    sort
  ) => {

    setRatingFilter(rating);
    setRecommendFilter(recommend);
    setSortOption(sort);

    if (selectedProduct) {

      loadReviews(
        selectedProduct["Clothing ID"],
        rating,
        recommend,
        sort
      );

    }
  };


  // =========================
  // Search
  // =========================

  const filteredProducts =
    products.filter((product) => {

      const keyword =
        searchText
          .toLowerCase()
          .trim();

      if (!keyword) {
        return true;
      }

      return (
        String(
          product["Clothing ID"]
        )
          .toLowerCase()
          .includes(keyword)

        ||

        String(
          product["Class_Name"] || ""
        )
          .toLowerCase()
          .includes(keyword)

        ||

        String(
          product["Department_Name"] || ""
        )
          .toLowerCase()
          .includes(keyword)

        ||

        String(
          product["Division_Name"] || ""
        )
          .toLowerCase()
          .includes(keyword)
      );
    });


  return (

    <SafeAreaView
      style={styles.container}
    >

      <ScrollView
        showsVerticalScrollIndicator={false}
      >

        {/* =========================
            HEADER
        ========================= */}

        <View style={styles.header}>

          <Text style={styles.headerTitle}>
            🛍️ E-COMMERCE AI
          </Text>

          <Text style={styles.headerSubtitle}>
            Khám phá sản phẩm & đánh giá khách hàng
          </Text>

        </View>


        <View style={styles.content}>


          {/* =========================
              PRODUCT SELECTION
          ========================= */}

          <View style={styles.card}>

            <Text style={styles.sectionTitle}>
              Chọn sản phẩm
            </Text>


            <TextInput
              style={styles.searchInput}
              placeholder="🔎 Tìm Clothing ID, Class..."
              placeholderTextColor="#94a3b8"
              value={searchText}
              onChangeText={setSearchText}
            />


            {loadingProducts ? (

              <View
                style={
                  styles.loadingContainer
                }
              >

                <ActivityIndicator
                  size="large"
                />

                <Text
                  style={styles.loadingText}
                >
                  Đang tải sản phẩm...
                </Text>

              </View>

            ) : (

              <>

                <Text
                  style={styles.productCount}
                >
                  {filteredProducts.length}
                  {" "}sản phẩm tìm thấy
                </Text>


                <View style={styles.productGrid}>

                  {filteredProducts
                    .slice(0, 20)
                    .map((product) => (

                    <TouchableOpacity
                      key={
                        product["Clothing ID"]
                      }
                      style={[
                        styles.productButton,

                        selectedProduct &&
                        selectedProduct[
                          "Clothing ID"
                        ] ===
                        product["Clothing ID"] &&
                        styles.productButtonSelected,
                      ]}

                      onPress={() =>
                        selectProduct(product)
                      }
                    >

                      <Text
                        style={[
                          styles.productButtonText,

                          selectedProduct &&
                          selectedProduct[
                            "Clothing ID"
                          ] ===
                          product["Clothing ID"] &&
                          styles.productButtonTextSelected,
                        ]}
                      >
                        ID {product["Clothing ID"]}
                      </Text>


                      <Text
                        style={[
                          styles.productButtonSubtext,

                          selectedProduct &&
                          selectedProduct[
                            "Clothing ID"
                          ] ===
                          product["Clothing ID"] &&
                          styles.productButtonTextSelected,
                        ]}
                      >
                        {product["Class_Name"]
                          || "Unknown"}
                      </Text>

                    </TouchableOpacity>

                  ))}

                </View>


                {filteredProducts.length > 20 && (

                  <Text
                    style={styles.moreText}
                  >
                    Đang hiển thị 20 sản phẩm.
                    Hãy tìm kiếm để tìm sản phẩm khác.
                  </Text>

                )}

              </>

            )}

          </View>


          {/* =========================
              PRODUCT INFORMATION
          ========================= */}

          {selectedProduct && (

            <View style={styles.card}>

              <Text
                style={styles.productTitle}
              >
                👗 Clothing ID{" "}
                {selectedProduct["Clothing ID"]}
              </Text>


              <View style={styles.infoGrid}>

                <InfoBox
                  label="Division"
                  value={
                    selectedProduct[
                      "Division_Name"
                    ]
                  }
                />

                <InfoBox
                  label="Department"
                  value={
                    selectedProduct[
                      "Department_Name"
                    ]
                  }
                />

                <InfoBox
                  label="Class"
                  value={
                    selectedProduct[
                      "Class_Name"
                    ]
                  }
                />

                <InfoBox
                  label="Tổng đánh giá"
                  value={
                    selectedProduct[
                      "Total_Reviews"
                    ]
                  }
                />

              </View>


              <View
                style={styles.statsContainer}
              >

                <StatBox
                  value={`⭐ ${
                    selectedProduct[
                      "Average_Rating"
                    ]
                  }`}
                  label="Rating trung bình"
                />

                <StatBox
                  value={`${
                    selectedProduct[
                      "Recommended_Rate"
                    ]
                  }%`}
                  label="Khách hàng đề xuất"
                />

              </View>

            </View>

          )}


          {/* =========================
              FILTERS
          ========================= */}

          {selectedProduct && (

            <View style={styles.card}>

              <Text style={styles.filterTitle}>
                Bộ lọc đánh giá
              </Text>


              <Text style={styles.filterLabel}>
                Rating
              </Text>

              <View style={styles.filterRow}>

                {[
                  ["all", "Tất cả"],
                  ["5", "5★"],
                  ["4", "4★"],
                  ["3", "3★"],
                  ["2", "2★"],
                  ["1", "1★"],
                ].map(([value, label]) => (

                  <TouchableOpacity
                    key={value}
                    style={[
                      styles.filterButton,

                      ratingFilter === value &&
                      styles.filterButtonSelected,
                    ]}

                    onPress={() =>
                      applyFilters(
                        value,
                        recommendFilter,
                        sortOption
                      )
                    }
                  >

                    <Text
                      style={[
                        styles.filterButtonText,

                        ratingFilter === value &&
                        styles.filterButtonTextSelected,
                      ]}
                    >
                      {label}
                    </Text>

                  </TouchableOpacity>

                ))}

              </View>


              <Text style={styles.filterLabel}>
                Đề xuất
              </Text>

              <View style={styles.filterRow}>

                {[
                  ["all", "Tất cả"],
                  [
                    "recommended",
                    "✓ Đề xuất"
                  ],
                  [
                    "not_recommended",
                    "✕ Không đề xuất"
                  ],
                ].map(([value, label]) => (

                  <TouchableOpacity
                    key={value}
                    style={[
                      styles.filterButton,

                      recommendFilter === value &&
                      styles.filterButtonSelected,
                    ]}

                    onPress={() =>
                      applyFilters(
                        ratingFilter,
                        value,
                        sortOption
                      )
                    }
                  >

                    <Text
                      style={[
                        styles.filterButtonText,

                        recommendFilter === value &&
                        styles.filterButtonTextSelected,
                      ]}
                    >
                      {label}
                    </Text>

                  </TouchableOpacity>

                ))}

              </View>


              <Text style={styles.filterLabel}>
                Sắp xếp
              </Text>

              <View style={styles.filterRow}>

                {[
                  ["newest", "Mới nhất"],
                  [
                    "rating_high",
                    "Rating cao ↓"
                  ],
                  [
                    "rating_low",
                    "Rating thấp ↑"
                  ],
                  [
                    "helpful",
                    "👍 Hữu ích"
                  ],
                ].map(([value, label]) => (

                  <TouchableOpacity
                    key={value}
                    style={[
                      styles.filterButton,

                      sortOption === value &&
                      styles.filterButtonSelected,
                    ]}

                    onPress={() =>
                      applyFilters(
                        ratingFilter,
                        recommendFilter,
                        value
                      )
                    }
                  >

                    <Text
                      style={[
                        styles.filterButtonText,

                        sortOption === value &&
                        styles.filterButtonTextSelected,
                      ]}
                    >
                      {label}
                    </Text>

                  </TouchableOpacity>

                ))}

              </View>

            </View>

          )}


          {/* =========================
              REVIEWS
          ========================= */}

          {selectedProduct && (

            <View style={styles.card}>

              <View
                style={styles.reviewHeader}
              >

                <Text
                  style={styles.sectionTitle}
                >
                  💬 Đánh giá khách hàng
                </Text>

                <Text
                  style={styles.reviewCount}
                >
                  {reviews.length} đánh giá
                </Text>

              </View>


              {loadingReviews ? (

                <View
                  style={
                    styles.loadingContainer
                  }
                >

                  <ActivityIndicator
                    size="large"
                  />

                  <Text
                    style={styles.loadingText}
                  >
                    Đang tải đánh giá...
                  </Text>

                </View>

              ) : reviews.length === 0 ? (

                <Text style={styles.emptyText}>
                  Không có đánh giá phù hợp.
                </Text>

              ) : (

                reviews.map((review) => (

                  <Review
                    key={review.review_id}
                    review={review}
                  />

                ))

              )}

            </View>

          )}


          {/* =========================
              EMPTY STATE
          ========================= */}

          {!selectedProduct &&
            !loadingProducts && (

            <View style={styles.emptyState}>

              <Text style={styles.emptyIcon}>
                🛍️
              </Text>

              <Text style={styles.emptyTitle}>
                Chưa chọn sản phẩm
              </Text>

              <Text style={styles.emptyText}>
                Hãy chọn một Clothing ID để xem
                thông tin và đánh giá.
              </Text>

            </View>

          )}

        </View>

      </ScrollView>

    </SafeAreaView>
  );
}


/* =========================
   Info Box
========================= */

function InfoBox({ label, value }) {

  return (

    <View style={styles.infoBox}>

      <Text style={styles.infoLabel}>
        {label}
      </Text>

      <Text style={styles.infoValue}>
        {value || "N/A"}
      </Text>

    </View>

  );
}


/* =========================
   Stat Box
========================= */

function StatBox({ value, label }) {

  return (

    <View style={styles.statBox}>

      <Text style={styles.statNumber}>
        {value}
      </Text>

      <Text style={styles.statLabel}>
        {label}
      </Text>

    </View>

  );
}


/* =========================
   Review
========================= */

function Review({ review }) {

  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const stars =
    "★".repeat(review.rating) +
    "☆".repeat(5 - review.rating);


  const analyzeReview = async () => {

    try {

      setAnalyzing(true);
      setResult(null);

      const response = await fetch(
        `${API_URL}/predict-review`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            review_id: review.review_id,
          }),
        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.error ||
          "Không thể phân tích review"
        );

      }


      setResult(data);

    } catch (error) {

      Alert.alert(
        "Lỗi",
        error.message
      );

      console.log(
        "Prediction error:",
        error
      );

    } finally {

      setAnalyzing(false);

    }
  };


  return (

    <View style={styles.review}>

      {/* =========================
          Review header
      ========================= */}

      <View style={styles.reviewTop}>

        <Text style={styles.stars}>
          {stars}
        </Text>


        {review.recommended === 1 ? (

          <View
            style={styles.recommendedBadge}
          >

            <Text
              style={styles.recommendedText}
            >
              ✓ Đề xuất
            </Text>

          </View>

        ) : (

          <View
            style={styles.notRecommendedBadge}
          >

            <Text
              style={styles.notRecommendedText}
            >
              ✕ Không đề xuất
            </Text>

          </View>

        )}

      </View>


      {/* =========================
          Title
      ========================= */}

      <Text style={styles.reviewTitle}>

        {review.title
          ? review.title
          : "Không có tiêu đề"}

      </Text>


      {/* =========================
          Review text
      ========================= */}

      <Text style={styles.reviewText}>

        {review.review_text
          ? review.review_text
          : "Không có nội dung đánh giá."}

      </Text>


      {/* =========================
          Metadata
      ========================= */}

      <View style={styles.reviewMeta}>

        <Text style={styles.metaText}>
          👤 Tuổi: {review.age}
        </Text>

        <Text style={styles.metaText}>
          👍 {review.positive_feedback}
          {" "}người thấy hữu ích
        </Text>

      </View>


      {/* =========================
          AI button
      ========================= */}

      <TouchableOpacity
        style={styles.aiButton}
        onPress={analyzeReview}
        disabled={analyzing}
      >

        {analyzing ? (

          <View style={styles.aiButtonLoading}>

            <ActivityIndicator
              size="small"
              color="#ffffff"
            />

            <Text
              style={styles.aiButtonText}
            >
              Đang phân tích...
            </Text>

          </View>

        ) : (

          <Text style={styles.aiButtonText}>
            🔮 Phân tích bằng AI
          </Text>

        )}

      </TouchableOpacity>


      {/* =========================
          AI result
      ========================= */}

      {result && (

        <View style={styles.aiResult}>

          <Text style={styles.aiResultTitle}>
            🔮 Kết quả phân tích
          </Text>


          <View
            style={[
              styles.predictionBox,

              result.prediction === 1
                ? styles.predictionRecommended
                : styles.predictionNotRecommended,
            ]}
          >

            <Text
              style={
                result.prediction === 1
                  ? styles.predictionRecommendedText
                  : styles.predictionNotRecommendedText
              }
            >

              {result.prediction === 1
                ? "✓ CÓ KHẢ NĂNG ĐỀ XUẤT"
                : "✕ CÓ KHẢ NĂNG KHÔNG ĐỀ XUẤT"}

            </Text>

          </View>


          {/* Recommended probability */}

          <View style={styles.probabilityRow}>

            <View
              style={styles.probabilityHeader}
            >

              <Text>
                Khả năng đề xuất
              </Text>

              <Text style={styles.probabilityValue}>
                {
                  (
                    result.probability
                      .recommended * 100
                  ).toFixed(2)
                }%
              </Text>

            </View>


            <View
              style={styles.probabilityBar}
            >

              <View
                style={[
                  styles.probabilityFillRecommended,

                  {
                    width:
                      `${
                        result.probability
                          .recommended * 100
                      }%`,
                  },
                ]}
              />

            </View>

          </View>


          {/* Not recommended probability */}

          <View style={styles.probabilityRow}>

            <View
              style={styles.probabilityHeader}
            >

              <Text>
                Khả năng không đề xuất
              </Text>

              <Text style={styles.probabilityValue}>
                {
                  (
                    result.probability
                      .not_recommended * 100
                  ).toFixed(2)
                }%
              </Text>

            </View>


            <View
              style={styles.probabilityBar}
            >

              <View
                style={[
                  styles.probabilityFillNotRecommended,

                  {
                    width:
                      `${
                        result.probability
                          .not_recommended * 100
                      }%`,
                  },
                ]}
              />

            </View>

          </View>

        </View>

      )}

    </View>

  );
}


/* =========================
   Styles
========================= */

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: "#f5f7fb",
  },

  header: {
    backgroundColor: "#111827",
    paddingHorizontal: 20,
    paddingVertical: 25,
  },

  headerTitle: {
    color: "#ffffff",
    fontSize: 25,
    fontWeight: "bold",
  },

  headerSubtitle: {
    color: "#cbd5e1",
    fontSize: 14,
    marginTop: 6,
  },

  content: {
    padding: 16,
  },

  card: {
    backgroundColor: "#ffffff",
    borderRadius: 14,
    padding: 18,
    marginBottom: 16,

    shadowColor: "#000",
    shadowOpacity: 0.06,
    shadowRadius: 8,
    shadowOffset: {
      width: 0,
      height: 3,
    },

    elevation: 2,
  },

  sectionTitle: {
    fontSize: 19,
    fontWeight: "bold",
    color: "#1f2937",
    marginBottom: 15,
  },

  searchInput: {
    height: 45,
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 9,
    paddingHorizontal: 14,
    marginBottom: 10,
    fontSize: 14,
  },

  productCount: {
    color: "#64748b",
    fontSize: 12,
    marginBottom: 10,
  },

  productGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },

  productButton: {
    width: "48%",
    paddingVertical: 13,
    paddingHorizontal: 12,
    borderRadius: 10,
    backgroundColor: "#f1f5f9",
  },

  productButtonSelected: {
    backgroundColor: "#111827",
  },

  productButtonText: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#1f2937",
  },

  productButtonTextSelected: {
    color: "#ffffff",
  },

  productButtonSubtext: {
    marginTop: 4,
    fontSize: 12,
    color: "#64748b",
  },

  moreText: {
    marginTop: 10,
    fontSize: 12,
    color: "#64748b",
  },

  loadingContainer: {
    alignItems: "center",
    paddingVertical: 25,
  },

  loadingText: {
    marginTop: 10,
    color: "#64748b",
  },

  productTitle: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 18,
    color: "#111827",
  },

  infoGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },

  infoBox: {
    width: "48%",
    backgroundColor: "#f8fafc",
    padding: 13,
    borderRadius: 9,
  },

  infoLabel: {
    fontSize: 12,
    color: "#64748b",
    marginBottom: 5,
  },

  infoValue: {
    fontSize: 15,
    fontWeight: "bold",
    color: "#1f2937",
  },

  statsContainer: {
    flexDirection: "row",
    gap: 10,
    marginTop: 15,
  },

  statBox: {
    flex: 1,
    backgroundColor: "#f8fafc",
    borderRadius: 10,
    padding: 18,
    alignItems: "center",
  },

  statNumber: {
    fontSize: 23,
    fontWeight: "bold",
    color: "#111827",
  },

  statLabel: {
    marginTop: 5,
    color: "#64748b",
    fontSize: 12,
    textAlign: "center",
  },

  filterTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 15,
  },

  filterLabel: {
    fontSize: 13,
    fontWeight: "bold",
    color: "#475569",
    marginBottom: 8,
    marginTop: 8,
  },

  filterRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },

  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 9,
    borderRadius: 8,
    backgroundColor: "#f1f5f9",
  },

  filterButtonSelected: {
    backgroundColor: "#111827",
  },

  filterButtonText: {
    color: "#334155",
    fontSize: 12,
    fontWeight: "bold",
  },

  filterButtonTextSelected: {
    color: "#ffffff",
  },

  reviewHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },

  reviewCount: {
    color: "#64748b",
    fontSize: 12,
  },

  review: {
    borderTopWidth: 1,
    borderTopColor: "#e5e7eb",
    paddingTop: 18,
    marginTop: 10,
  },

  reviewTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },

  stars: {
    color: "#f59e0b",
    fontSize: 18,
  },

  recommendedBadge: {
    backgroundColor: "#dcfce7",
    paddingHorizontal: 9,
    paddingVertical: 5,
    borderRadius: 20,
  },

  recommendedText: {
    color: "#166534",
    fontSize: 11,
    fontWeight: "bold",
  },

  notRecommendedBadge: {
    backgroundColor: "#fee2e2",
    paddingHorizontal: 9,
    paddingVertical: 5,
    borderRadius: 20,
  },

  notRecommendedText: {
    color: "#991b1b",
    fontSize: 11,
    fontWeight: "bold",
  },

  reviewTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginTop: 10,
    color: "#1f2937",
  },

  reviewText: {
    color: "#475569",
    lineHeight: 21,
    marginTop: 7,
    fontSize: 14,
  },

  reviewMeta: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 15,
    marginTop: 10,
  },

  metaText: {
    color: "#64748b",
    fontSize: 12,
  },

  aiButton: {
    backgroundColor: "#111827",
    paddingVertical: 11,
    paddingHorizontal: 15,
    borderRadius: 8,
    alignSelf: "flex-start",
    marginTop: 13,
  },

  aiButtonText: {
    color: "#ffffff",
    fontSize: 13,
    fontWeight: "bold",
  },

    aiButtonLoading: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },

  aiResult: {
    marginTop: 15,
    padding: 16,
    borderRadius: 12,
    backgroundColor: "#f8fafc",
  },

  aiResultTitle: {
    fontSize: 17,
    fontWeight: "bold",
    color: "#111827",
    marginBottom: 12,
  },

  predictionBox: {
    padding: 13,
    borderRadius: 9,
    alignItems: "center",
    marginBottom: 15,
  },

  predictionRecommended: {
    backgroundColor: "#dcfce7",
  },

  predictionNotRecommended: {
    backgroundColor: "#fee2e2",
  },

  predictionRecommendedText: {
    color: "#166534",
    fontWeight: "bold",
    fontSize: 14,
  },

  predictionNotRecommendedText: {
    color: "#991b1b",
    fontWeight: "bold",
    fontSize: 14,
  },

  probabilityRow: {
    marginTop: 8,
  },

  probabilityHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 6,
  },

  probabilityValue: {
    fontWeight: "bold",
  },

  probabilityBar: {
    height: 10,
    backgroundColor: "#e5e7eb",
    borderRadius: 10,
    overflow: "hidden",
  },

  probabilityFillRecommended: {
    height: "100%",
    backgroundColor: "#22c55e",
  },

  probabilityFillNotRecommended: {
    height: "100%",
    backgroundColor: "#ef4444",
  },

  emptyState: {
    backgroundColor: "#ffffff",
    borderRadius: 14,
    padding: 40,
    alignItems: "center",
    marginTop: 10,
  },

  emptyIcon: {
    fontSize: 50,
  },

  emptyTitle: {
    fontSize: 19,
    fontWeight: "bold",
    marginTop: 12,
  },

  emptyText: {
    textAlign: "center",
    color: "#64748b",
    marginTop: 8,
    lineHeight: 20,
  },

});