import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
from utils import prepare_input

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Threat Detection", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True   # TEMP: skip login for testing

# ---------------- DASHBOARD ----------------
st.title("🚨 Threat Detection Dashboard")

# Load model
model = pickle.load(open("model.pkl", "rb"))

# Sidebar
option = st.sidebar.radio("Select Mode", ["Manual Input", "Upload File"])

# ---------------- MANUAL INPUT ----------------
if option == "Manual Input":
    st.subheader("Enter Network Data")

    col1, col2, col3 = st.columns(3)

    duration = col1.number_input("Duration")
    src_bytes = col2.number_input("Source Bytes")
    dst_bytes = col3.number_input("Destination Bytes")

    if st.button("Detect"):
        data = prepare_input(duration, src_bytes, dst_bytes)
        result = model.predict(data)

        if result[0] == 1:
            st.error("⚠️ Threat Detected")
        else:
            st.success("✅ Normal Traffic")

# ---------------- FILE UPLOAD ----------------
else:
    st.subheader("Upload CSV File")

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file is not None:
        data = pd.read_csv(file)

        st.write("### Uploaded Data")
        st.dataframe(data)

        try:
            predictions = model.predict(data)
            data["Result"] = predictions

            normal = sum(predictions == 0)
            threat = sum(predictions == 1)
            total = len(predictions)

            accuracy = (normal / total) * 100

            # -------- TOP CARDS --------
            st.write("## 📊 Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Normal", normal)
            col2.metric("Threat", threat)
            col3.metric("Accuracy", f"{accuracy:.2f}%")

            # -------- PIE CHART --------
            chart_data = pd.DataFrame({
                "Type": ["Normal", "Threat"],
                "Count": [normal, threat]
            })

            fig = px.pie(chart_data, names="Type", values="Count")
            st.plotly_chart(fig, use_container_width=True)

            # -------- BAR GRAPH --------
            st.bar_chart(chart_data.set_index("Type"))

            # -------- TABLE --------
            st.write("### Detection Results")
            st.dataframe(data)

        except Exception as e:
            st.error("Error in prediction")
            st.write(e)