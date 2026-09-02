import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Modal,
  Pressable,
  Alert,
} from "react-native";

const API_URL = "http://192.168.1.15:5011/predict";
const DATASET_URL = "http://192.168.1.15:5011/dataset";

// ============================================================
// Dropdown options
// ============================================================

const cities = [
  "Pune",
  "Kolkata",
  "Chennai",
  "Delhi",
  "Mumbai",
  "Hyderabad",
  "Bangalore",
];

const furnishingOptions = [
  {
    value: "Unfurnished",
    label: "Không nội thất",
  },
  {
    value: "Semi-Furnished",
    label: "Nội thất cơ bản",
  },
  {
    value: "Furnished",
    label: "Đầy đủ nội thất",
  },
];

const yesNoOptions = [
  {
    value: "Yes",
    label: "Có",
  },
  {
    value: "No",
    label: "Không",
  },
];

const waterSupplyOptions = [
  {
    value: "Both",
    label: "Cả hai",
  },
  {
    value: "Corporation",
    label: "Nước máy",
  },
  {
    value: "Borewell",
    label: "Giếng khoan",
  },
];

const tenantOptions = [
  {
    value: "Family",
    label: "Gia đình",
  },
  {
    value: "Company",
    label: "Công ty",
  },
  {
    value: "Bachelor",
    label: "Người độc thân",
  },
];

// ============================================================
// Dropdown component
// ============================================================

function Dropdown({ label, value, options, onChange }) {
  const [visible, setVisible] = useState(false);

  const selectedOption = options.find(
    (item) => item.value === value
  );

  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>

      <TouchableOpacity
        style={styles.dropdown}
        onPress={() => setVisible(true)}
      >
        <Text style={styles.dropdownText}>
          {selectedOption
            ? selectedOption.label
            : value}
        </Text>

        <Text style={styles.arrow}>▼</Text>
      </TouchableOpacity>

      <Modal
        visible={visible}
        transparent
        animationType="fade"
        onRequestClose={() => setVisible(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setVisible(false)}
        >
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>
              {label}
            </Text>

            {options.map((item) => (
              <TouchableOpacity
                key={item.value}
                style={[
                  styles.option,
                  item.value === value &&
                    styles.selectedOption,
                ]}
                onPress={() => {
                  onChange(item.value);
                  setVisible(false);
                }}
              >
                <Text
                  style={[
                    styles.optionText,
                    item.value === value &&
                      styles.selectedOptionText,
                  ]}
                >
                  {item.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Pressable>
      </Modal>
    </View>
  );
}

// ============================================================
// Main App
// ============================================================

export default function App() {
  // Numerical features
  const [area, setArea] = useState("");
  const [bedrooms, setBedrooms] = useState("");
  const [bathrooms, setBathrooms] = useState("");
  const [stories, setStories] = useState("");
  const [parking, setParking] = useState("");
  const [age, setAge] = useState("");
  const [localityRating, setLocalityRating] = useState("");

  // Categorical features
  const [city, setCity] = useState("Pune");
  const [furnishing, setFurnishing] =
    useState("Unfurnished");
  const [mainRoad, setMainRoad] = useState("Yes");
  const [guestRoom, setGuestRoom] = useState("No");
  const [basement, setBasement] = useState("No");
  const [waterSupply, setWaterSupply] =
    useState("Both");
  const [airConditioning, setAirConditioning] =
    useState("No");
  const [preferredTenant, setPreferredTenant] =
    useState("Family");

  // Prediction
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  // Dataset
  const [similarHouses, setSimilarHouses] =
    useState([]);

  // ============================================================
  // Predict
  // ============================================================

  const handlePredict = async () => {
    // Validate numerical fields
    if (
      !area ||
      !bedrooms ||
      !bathrooms ||
      !stories ||
      !parking ||
      !age ||
      !localityRating
    ) {
      Alert.alert(
        "Thiếu thông tin",
        "Vui lòng nhập đầy đủ thông tin."
      );
      return;
    }

    const data = {
      Area: Number(area),
      Bedrooms: Number(bedrooms),
      Bathrooms: Number(bathrooms),
      Stories: Number(stories),
      Parking: Number(parking),
      Age: Number(age),

      City: city,
      Furnishing: furnishing,
      "Main Road": mainRoad,
      "Guest Room": guestRoom,
      Basement: basement,
      "Water Supply": waterSupply,
      "Air Conditioning": airConditioning,
      "Preferred Tenant": preferredTenant,

      "Locality Rating": Number(localityRating),
    };

    try {
      setLoading(true);
      setPrediction(null);
      setSimilarHouses([]);

      // ========================================================
      // 1. Call prediction API
      // ========================================================

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.error || "Có lỗi xảy ra khi dự đoán."
        );
      }

      const predictedPrice =
        Number(result.predicted_price);

      setPrediction(predictedPrice);

      // ========================================================
      // 2. Get dataset
      // ========================================================

      const datasetResponse =
        await fetch(DATASET_URL);

      const dataset =
        await datasetResponse.json();

      if (!datasetResponse.ok) {
        throw new Error(
          "Không thể tải dữ liệu dataset."
        );
      }

      // ========================================================
      // 3. Find suitable houses
      //
      // Same city
      // Price within ±20% of predicted price
      // ========================================================

      const minPrice =
        predictedPrice * 0.8;

      const maxPrice =
        predictedPrice * 1.2;

      const matched = dataset
        .filter((house) => {
          const housePrice =
            Number(house.Price);

          return (
            house.City === city &&
            housePrice >= minPrice &&
            housePrice <= maxPrice
          );
        })
        .sort((a, b) => {
          const priceA = Number(a.Price);
          const priceB = Number(b.Price);

          return (
            Math.abs(priceA - predictedPrice) -
            Math.abs(priceB - predictedPrice)
          );
        })
        .slice(0, 20);

      setSimilarHouses(matched);

    } catch (error) {
      Alert.alert(
        "Lỗi kết nối",
        "Không thể kết nối đến Flask API.\n\n" +
          error.message
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // Format price
  // ============================================================

  const formatPrice = (price) => {
    return `₹${Number(price).toLocaleString(
      "en-US",
      {
        maximumFractionDigits: 0,
      }
    )}`;
  };

  // ============================================================
  // Render
  // ============================================================

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >

        {/* ====================================================
            Header
        ==================================================== */}

        <Text style={styles.title}>
          Dự đoán giá nhà
        </Text>

        <Text style={styles.subtitle}>
          Nhập thông tin căn nhà để dự đoán giá
        </Text>

        {/* ====================================================
            Form
        ==================================================== */}

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>
            Thông tin căn nhà
          </Text>

          {/* Area + Bedrooms */}

          <View style={styles.row}>
            <View style={styles.half}>
              <Text style={styles.label}>
                Diện tích
              </Text>

              <TextInput
                style={styles.input}
                value={area}
                onChangeText={setArea}
                keyboardType="numeric"
                placeholder="m²"
              />
            </View>

            <View style={styles.half}>
              <Text style={styles.label}>
                Số phòng ngủ
              </Text>

              <TextInput
                style={styles.input}
                value={bedrooms}
                onChangeText={setBedrooms}
                keyboardType="numeric"
                placeholder="Ví dụ: 3"
              />
            </View>
          </View>

          {/* Bathrooms + Stories */}

          <View style={styles.row}>
            <View style={styles.half}>
              <Text style={styles.label}>
                Số phòng tắm
              </Text>

              <TextInput
                style={styles.input}
                value={bathrooms}
                onChangeText={setBathrooms}
                keyboardType="numeric"
                placeholder="Ví dụ: 2"
              />
            </View>

            <View style={styles.half}>
              <Text style={styles.label}>
                Số tầng
              </Text>

              <TextInput
                style={styles.input}
                value={stories}
                onChangeText={setStories}
                keyboardType="numeric"
                placeholder="Ví dụ: 2"
              />
            </View>
          </View>

          {/* Parking + Age */}

          <View style={styles.row}>
            <View style={styles.half}>
              <Text style={styles.label}>
                Chỗ đậu xe
              </Text>

              <TextInput
                style={styles.input}
                value={parking}
                onChangeText={setParking}
                keyboardType="numeric"
                placeholder="Ví dụ: 1"
              />
            </View>

            <View style={styles.half}>
              <Text style={styles.label}>
                Tuổi căn nhà
              </Text>

              <TextInput
                style={styles.input}
                value={age}
                onChangeText={setAge}
                keyboardType="numeric"
                placeholder="Năm"
              />
            </View>
          </View>

          {/* City */}

          <Dropdown
            label="Thành phố"
            value={city}
            options={cities.map((item) => ({
              value: item,
              label: item,
            }))}
            onChange={setCity}
          />

          {/* Furnishing */}

          <Dropdown
            label="Nội thất"
            value={furnishing}
            options={furnishingOptions}
            onChange={setFurnishing}
          />

          {/* Main Road */}

          <Dropdown
            label="Đường chính"
            value={mainRoad}
            options={yesNoOptions}
            onChange={setMainRoad}
          />

          {/* Guest Room */}

          <Dropdown
            label="Phòng khách"
            value={guestRoom}
            options={yesNoOptions}
            onChange={setGuestRoom}
          />

          {/* Basement */}

          <Dropdown
            label="Tầng hầm"
            value={basement}
            options={yesNoOptions}
            onChange={setBasement}
          />

          {/* Water Supply */}

          <Dropdown
            label="Nguồn nước"
            value={waterSupply}
            options={waterSupplyOptions}
            onChange={setWaterSupply}
          />

          {/* Air Conditioning */}

          <Dropdown
            label="Điều hòa"
            value={airConditioning}
            options={yesNoOptions}
            onChange={setAirConditioning}
          />

          {/* Preferred Tenant */}

          <Dropdown
            label="Đối tượng thuê"
            value={preferredTenant}
            options={tenantOptions}
            onChange={setPreferredTenant}
          />

          {/* Locality Rating */}

          <Text style={styles.label}>
            Đánh giá khu vực
          </Text>

          <TextInput
            style={styles.input}
            value={localityRating}
            onChangeText={setLocalityRating}
            keyboardType="numeric"
            placeholder="Ví dụ: 4.5"
          />

          {/* Predict button */}

          <TouchableOpacity
            style={styles.button}
            onPress={handlePredict}
            disabled={loading}
          >
            <Text style={styles.buttonText}>
              {loading
                ? "Đang dự đoán..."
                : "Dự đoán giá"}
            </Text>
          </TouchableOpacity>
        </View>

        {/* ====================================================
            Prediction result
        ==================================================== */}

        {prediction !== null && (
          <View style={styles.resultCard}>

            <Text style={styles.resultTitle}>
              Giá nhà dự đoán
            </Text>

            <Text style={styles.price}>
              {formatPrice(prediction)}
            </Text>

            <Text style={styles.resultNote}>
              Giá được dự đoán bởi mô hình
              Machine Learning
            </Text>

          </View>
        )}

        {/* ====================================================
            Similar houses
        ==================================================== */}

        {prediction !== null && (
          <View style={styles.datasetCard}>

            {/* Dataset header */}

            <View style={styles.datasetHeader}>

              <Text style={styles.datasetTitle}>
                🏠 Nhà phù hợp trong Dataset
              </Text>

              <View style={styles.countBadge}>
                <Text style={styles.countText}>
                  {similarHouses.length}
                </Text>
              </View>

            </View>

            <Text style={styles.datasetSubtitle}>
              Các căn cùng thành phố và có giá
              thực tế gần với giá dự đoán
            </Text>

            {/* No result */}

            {similarHouses.length === 0 ? (

              <Text style={styles.emptyText}>
                Không tìm thấy căn nhà phù hợp.
              </Text>

            ) : (

              /* House list */

              similarHouses.map((house, index) => (

                <View
                  style={styles.houseItem}
                  key={index}
                >

                  {/* City + Price */}

                  <View
                    style={styles.houseHeader}
                  >

                    <Text style={styles.houseCity}>
                      {house.City}
                    </Text>

                    <Text style={styles.housePrice}>
                      {formatPrice(house.Price)}
                    </Text>

                  </View>

                  {/* Area + Bedrooms + Bathrooms */}

                  <View style={styles.houseInfo}>

                    <Text
                      style={styles.houseInfoText}
                    >
                      📐{" "}
                      {Number(
                        house.Area
                      ).toLocaleString("en-US")}{" "}
                      m²
                    </Text>

                    <Text
                      style={styles.houseInfoText}
                    >
                      🛏 {house.Bedrooms} phòng ngủ
                    </Text>

                    <Text
                      style={styles.houseInfoText}
                    >
                      🚿 {house.Bathrooms} phòng tắm
                    </Text>

                  </View>

                  {/* Stories + Furnishing + Age */}

                  <View style={styles.houseInfo}>

                    <Text
                      style={styles.houseInfoText}
                    >
                      🏢 {house.Stories} tầng
                    </Text>

                    <Text
                      style={styles.houseInfoText}
                    >
                      🛋 {house.Furnishing}
                    </Text>

                    <Text
                      style={styles.houseInfoText}
                    >
                      🕐 {house.Age} năm
                    </Text>

                  </View>

                </View>

              ))

            )}

          </View>
        )}

      </ScrollView>
    </View>
  );
}

// ============================================================
// Styles
// ============================================================

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: "#f5f7fa",
  },

  content: {
    padding: 20,
    paddingTop: 55,
    paddingBottom: 40,
  },

  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#1f2937",
    marginBottom: 6,
  },

  subtitle: {
    fontSize: 15,
    color: "#6b7280",
    marginBottom: 20,
  },

  // ==========================================================
  // Form card
  // ==========================================================

  card: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 18,
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#1f2937",
    marginBottom: 18,
  },

  row: {
    flexDirection: "row",
    gap: 10,
  },

  half: {
    flex: 1,
  },

  field: {
    marginBottom: 15,
  },

  label: {
    fontSize: 14,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 7,
  },

  input: {
    height: 46,
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 9,
    paddingHorizontal: 12,
    fontSize: 15,
    backgroundColor: "#fff",
    marginBottom: 15,
  },

  // ==========================================================
  // Dropdown
  // ==========================================================

  dropdown: {
    height: 46,
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 9,
    paddingHorizontal: 12,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: "#fff",
  },

  dropdownText: {
    fontSize: 15,
    color: "#1f2937",
  },

  arrow: {
    fontSize: 12,
    color: "#6b7280",
  },

  // ==========================================================
  // Predict button
  // ==========================================================

  button: {
    height: 50,
    borderRadius: 10,
    backgroundColor: "#2563eb",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 5,
  },

  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "bold",
  },

  // ==========================================================
  // Prediction result
  // ==========================================================

  resultCard: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 22,
    marginTop: 18,
    alignItems: "center",
  },

  resultTitle: {
    fontSize: 16,
    color: "#6b7280",
    marginBottom: 8,
  },

  price: {
    fontSize: 30,
    fontWeight: "bold",
    color: "#2563eb",
    marginBottom: 8,
  },

  resultNote: {
    fontSize: 13,
    color: "#6b7280",
    textAlign: "center",
  },

  // ==========================================================
  // Dataset
  // ==========================================================

  datasetCard: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 18,
    marginTop: 18,
  },

  datasetHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 8,
  },

  datasetTitle: {
    fontSize: 19,
    fontWeight: "bold",
    color: "#1f2937",
    flex: 1,
  },

  countBadge: {
    backgroundColor: "#2563eb",
    minWidth: 34,
    height: 30,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 8,
  },

  countText: {
    color: "#ffffff",
    fontSize: 14,
    fontWeight: "bold",
  },

  datasetSubtitle: {
    fontSize: 13,
    color: "#6b7280",
    marginBottom: 14,
    lineHeight: 19,
  },

  emptyText: {
    textAlign: "center",
    color: "#94a3b8",
    paddingVertical: 25,
  },

  // ==========================================================
  // House item
  // ==========================================================

  houseItem: {
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
  },

  houseHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },

  houseCity: {
    fontSize: 17,
    fontWeight: "bold",
    color: "#1f2937",
  },

  housePrice: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#16a34a",
  },

  houseInfo: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginBottom: 5,
  },

  houseInfoText: {
    fontSize: 13,
    color: "#64748b",
    marginRight: 12,
    marginBottom: 4,
  },

  // ==========================================================
  // Modal dropdown
  // ==========================================================

  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.45)",
    justifyContent: "center",
    padding: 25,
  },

  modalBox: {
    backgroundColor: "#fff",
    borderRadius: 15,
    padding: 18,
  },

  modalTitle: {
    fontSize: 19,
    fontWeight: "bold",
    color: "#1f2937",
    marginBottom: 12,
  },

  option: {
    paddingVertical: 14,
    paddingHorizontal: 12,
    borderRadius: 8,
  },

  selectedOption: {
    backgroundColor: "#eef2ff",
  },

  optionText: {
    fontSize: 16,
    color: "#374151",
  },

  selectedOptionText: {
    fontWeight: "bold",
    color: "#2563eb",
  },

});