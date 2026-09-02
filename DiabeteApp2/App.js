import React, { useState } from "react";

import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Pressable,
} from "react-native";


// ============================================================
// Dropdown Component
// ============================================================

function Dropdown({
  label,
  value,
  options,
  onSelect,
}) {

  const [visible, setVisible] = useState(false);

  return (
    <View style={styles.formGroup}>

      <Text style={styles.label}>
        {label}
      </Text>


      {/* Dropdown button */}

      <TouchableOpacity
        style={styles.dropdown}
        onPress={() => setVisible(true)}
        activeOpacity={0.7}
      >

        <Text style={styles.dropdownText}>
          {value}
        </Text>


        <Text style={styles.arrow}>
          ▼
        </Text>

      </TouchableOpacity>


      {/* Dropdown menu */}

      <Modal
        visible={visible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setVisible(false)}
      >

        <Pressable
          style={styles.modalOverlay}
          onPress={() => setVisible(false)}
        >

          <View
            style={styles.dropdownMenu}
            onStartShouldSetResponder={() => true}
          >

            <Text style={styles.dropdownTitle}>
              {label}
            </Text>


            {options.map((option) => (

              <TouchableOpacity
                key={option.value}
                style={styles.option}
                onPress={() => {

                  onSelect(option.value);

                  setVisible(false);

                }}
              >

                <Text style={styles.optionText}>
                  {option.label}
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


  // ============================================================
  // Form states
  // ============================================================

  const [gender, setGender] =
    useState("Male");

  const [age, setAge] =
    useState("");

  const [hypertension, setHypertension] =
    useState("0");

  const [heartDisease, setHeartDisease] =
    useState("0");

  const [smokingHistory, setSmokingHistory] =
    useState("never");

  const [bmi, setBmi] =
    useState("");

  const [hba1c, setHba1c] =
    useState("");

  const [bloodGlucose, setBloodGlucose] =
    useState("");


  // ============================================================
  // Result states
  // ============================================================

  const [prediction, setPrediction] =
    useState(null);

  const [confidence, setConfidence] =
    useState(null);


  // ============================================================
  // Predict
  // ============================================================

const handlePredict = async () => {

  try {

    setPrediction(null);
    setConfidence(null);
//Thay bằng địa chỉ ipv4 của máy mình
    const response = await fetch(
      "http://192.168.1.15:5010/predict",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({

          gender: gender,

          age: Number(age),

          hypertension:
            Number(hypertension),

          heart_disease:
            Number(heartDisease),

          smoking_history:
            smokingHistory,

          bmi: Number(bmi),

          HbA1c_level:
            Number(hba1c),

          blood_glucose_level:
            Number(bloodGlucose),

        }),

      }
    );


    const data = await response.json();


    if (!response.ok) {

      throw new Error(
        data.error || "Prediction failed"
      );

    }


    setPrediction(
      Number(data.prediction)
    );


    setConfidence(
      Number(data.confidence)
    );


  } catch (error) {

    console.log(
      "Prediction error:",
      error
    );

  }

};


  // ============================================================
  // Reset
  // ============================================================

  const handleReset = () => {

    setGender("Male");

    setAge("");

    setHypertension("0");

    setHeartDisease("0");

    setSmokingHistory("never");

    setBmi("");

    setHba1c("");

    setBloodGlucose("");

    setPrediction(null);

    setConfidence(null);

  };


  return (

    <SafeAreaView style={styles.safeArea}>

      <ScrollView
        contentContainerStyle={styles.scrollContainer}
        keyboardShouldPersistTaps="handled"
      >

        <View style={styles.container}>


          {/* ================================================== */}
          {/* Header */}
          {/* ================================================== */}

          <Text style={styles.title}>
            Diabetes Prediction
          </Text>


          <Text style={styles.description}>
            Enter patient information to predict diabetes status.
          </Text>


          {/* ================================================== */}
          {/* Gender Dropdown */}
          {/* ================================================== */}

          <Dropdown

            label="Gender"

            value={gender}

            options={[
              {
                label: "Female",
                value: "Female",
              },

              {
                label: "Male",
                value: "Male",
              },

              {
                label: "Other",
                value: "Other",
              },
            ]}

            onSelect={setGender}

          />


          {/* ================================================== */}
          {/* Age */}
          {/* ================================================== */}

          <View style={styles.formGroup}>

            <Text style={styles.label}>
              Age
            </Text>


            <TextInput
              style={styles.input}
              value={age}
              onChangeText={setAge}
              keyboardType="numeric"
            />

          </View>


          {/* ================================================== */}
          {/* Hypertension Dropdown */}
          {/* ================================================== */}

          <Dropdown

            label="Hypertension"

            value={
              hypertension === "1"
                ? "Yes"
                : "No"
            }

            options={[
              {
                label: "No",
                value: "0",
              },

              {
                label: "Yes",
                value: "1",
              },
            ]}

            onSelect={setHypertension}

          />


          {/* ================================================== */}
          {/* Heart Disease Dropdown */}
          {/* ================================================== */}

          <Dropdown

            label="Heart Disease"

            value={
              heartDisease === "1"
                ? "Yes"
                : "No"
            }

            options={[
              {
                label: "No",
                value: "0",
              },

              {
                label: "Yes",
                value: "1",
              },
            ]}

            onSelect={setHeartDisease}

          />


          {/* ================================================== */}
          {/* Smoking History Dropdown */}
          {/* ================================================== */}

          <Dropdown

            label="Smoking History"

            value={smokingHistory}

            options={[
              {
                label: "No Info",
                value: "No Info",
              },

              {
                label: "Current",
                value: "current",
              },

              {
                label: "Ever",
                value: "ever",
              },

              {
                label: "Former",
                value: "former",
              },

              {
                label: "Never",
                value: "never",
              },

              {
                label: "Not Current",
                value: "not current",
              },
            ]}

            onSelect={setSmokingHistory}

          />


          {/* ================================================== */}
          {/* BMI */}
          {/* ================================================== */}

          <View style={styles.formGroup}>

            <Text style={styles.label}>
              BMI
            </Text>


            <TextInput
              style={styles.input}
              value={bmi}
              onChangeText={setBmi}
              keyboardType="decimal-pad"
            />

          </View>


          {/* ================================================== */}
          {/* HbA1c */}
          {/* ================================================== */}

          <View style={styles.formGroup}>

            <Text style={styles.label}>
              HbA1c Level
            </Text>


            <TextInput
              style={styles.input}
              value={hba1c}
              onChangeText={setHba1c}
              keyboardType="decimal-pad"
            />

          </View>


          {/* ================================================== */}
          {/* Blood Glucose */}
          {/* ================================================== */}

          <View style={styles.formGroup}>

            <Text style={styles.label}>
              Blood Glucose Level
            </Text>


            <TextInput
              style={styles.input}
              value={bloodGlucose}
              onChangeText={setBloodGlucose}
              keyboardType="numeric"
            />

          </View>


          {/* ================================================== */}
          {/* Buttons */}
          {/* ================================================== */}

          <View style={styles.buttonRow}>


            <TouchableOpacity
              style={styles.predictButton}
              onPress={handlePredict}
            >

              <Text style={styles.buttonText}>
                Predict Diabetes
              </Text>

            </TouchableOpacity>


            <TouchableOpacity
              style={styles.resetButton}
              onPress={handleReset}
            >

              <Text style={styles.buttonText}>
                Reset
              </Text>

            </TouchableOpacity>


          </View>


          {/* ================================================== */}
          {/* Result */}
          {/* ================================================== */}

          {prediction !== null && (

            <View style={styles.resultBox}>


              <Text style={styles.resultTitle}>
                Prediction Result
              </Text>


              <Text style={styles.predictionText}>

                Prediction:{" "}

                {prediction === 1
                  ? "Diabetes"
                  : "No Diabetes"}

              </Text>


              <Text style={styles.resultText}>

                Probability of diabetes:{" "}

                {confidence.toFixed(2)}%

              </Text>


              <Text style={styles.resultText}>

                {prediction === 1

                  ? "The model predicts that the patient belongs to the diabetes class."

                  : "The model predicts that the patient does not belong to the diabetes class."

                }

              </Text>


            </View>

          )}


        </View>

      </ScrollView>

    </SafeAreaView>

  );
}


// ============================================================
// Styles
// ============================================================

const styles = StyleSheet.create({

  safeArea: {

    flex: 1,

    backgroundColor: "#f5f7fa",

  },


  scrollContainer: {

    padding: 14,

    paddingBottom: 30,

  },


  container: {

    width: "100%",

    maxWidth: 650,

    alignSelf: "center",

    padding: 22,

    backgroundColor: "#ffffff",

    borderRadius: 12,

    shadowColor: "#000",

    shadowOffset: {
      width: 0,
      height: 3,
    },

    shadowOpacity: 0.1,

    shadowRadius: 8,

    elevation: 4,

  },


  title: {

    fontSize: 25,

    fontWeight: "700",

    textAlign: "center",

    marginBottom: 8,

    color: "#111111",

  },


  description: {

    textAlign: "center",

    color: "#666666",

    fontSize: 14,

    marginBottom: 25,

  },


  formGroup: {

    marginBottom: 16,

  },


  label: {

    fontSize: 14,

    fontWeight: "600",

    color: "#111111",

    marginBottom: 6,

  },


  input: {

    width: "100%",

    height: 44,

    borderWidth: 1,

    borderColor: "#cccccc",

    borderRadius: 6,

    paddingHorizontal: 10,

    fontSize: 15,

    color: "#111111",

    backgroundColor: "#ffffff",

  },


  // ==========================================================
  // Dropdown
  // ==========================================================

  dropdown: {

    width: "100%",

    height: 44,

    borderWidth: 1,

    borderColor: "#cccccc",

    borderRadius: 6,

    paddingHorizontal: 12,

    flexDirection: "row",

    alignItems: "center",

    justifyContent: "space-between",

    backgroundColor: "#ffffff",

  },


  dropdownText: {

    fontSize: 15,

    color: "#111111",

  },


  arrow: {

    fontSize: 12,

    color: "#555555",

  },


  // ==========================================================
  // Dropdown modal
  // ==========================================================

  modalOverlay: {

    flex: 1,

    backgroundColor: "rgba(0, 0, 0, 0.35)",

    justifyContent: "center",

    padding: 25,

  },


  dropdownMenu: {

    backgroundColor: "#ffffff",

    borderRadius: 10,

    padding: 10,

    maxHeight: "80%",

  },


  dropdownTitle: {

    fontSize: 18,

    fontWeight: "700",

    padding: 12,

    marginBottom: 5,

  },


  option: {

    paddingVertical: 14,

    paddingHorizontal: 12,

    borderBottomWidth: 1,

    borderBottomColor: "#eeeeee",

  },


  optionText: {

    fontSize: 16,

    color: "#111111",

  },


  // ==========================================================
  // Buttons
  // ==========================================================

  buttonRow: {

    flexDirection: "row",

    gap: 8,

    marginTop: 2,

  },


  predictButton: {

    flex: 1,

    backgroundColor: "#2563eb",

    paddingVertical: 13,

    borderRadius: 6,

    alignItems: "center",

    justifyContent: "center",

  },


  resetButton: {

    flex: 1,

    backgroundColor: "#6b7280",

    paddingVertical: 13,

    borderRadius: 6,

    alignItems: "center",

    justifyContent: "center",

  },


  buttonText: {

    color: "#ffffff",

    fontSize: 15,

    fontWeight: "600",

  },


  // ==========================================================
  // Result
  // ==========================================================

  resultBox: {

    marginTop: 20,

    padding: 16,

    borderRadius: 8,

    backgroundColor: "#eef6ff",

  },


  resultTitle: {

    fontSize: 20,

    fontWeight: "700",

    color: "#111111",

    marginBottom: 12,

  },


  predictionText: {

    fontSize: 16,

    fontWeight: "700",

    color: "#111111",

    marginBottom: 8,

  },


  resultText: {

    fontSize: 14,

    lineHeight: 22,

    color: "#222222",

    marginBottom: 5,

  },

});