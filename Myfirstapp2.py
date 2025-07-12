# traffic_app.py
import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- DB CONNECTION ---
def get_data(query, params=None):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="09876",  
        database="Secureledger"
    )
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    columns = [i[0] for i in cursor.description]
    df = pd.DataFrame(result, columns=columns)
    cursor.close()
    conn.close()
    return df

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚓 Traffic Stop Dashboard", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["📌 Introduction", "📊 Traffic Visualizer", "📋 SQL Insights", "🙋 Creator Info"])

# --- PAGE 1: INTRODUCTION ---
if page == "📌 Introduction":
    st.title("🚦 Police Traffic Stop Dashboard")
    st.subheader("👮 An interactive SQL-powered dashboard for analyzing police traffic stops")
    st.markdown("""
    This dashboard uses data stored in a MySQL database (`Secureledger.policelog`)  
    It allows you to:
    - View traffic stop records
    - Filter by country, gender, violation
    - Run pre-built SQL queries
    - Understand driver patterns and enforcement behavior
    """)

# --- PAGE 2: TRAFFIC VISUALIZER ---
elif page == "📊 Traffic Visualizer":
    st.title("📊 Traffic Stop Visualization")

    countries = get_data("SELECT DISTINCT country_name FROM policelog")['country_name'].dropna().tolist()
    genders = get_data("SELECT DISTINCT driver_gender FROM policelog")['driver_gender'].dropna().tolist()

    selected_country = st.selectbox("Select Country", countries)
    selected_gender = st.radio("Select Gender", genders)

    df = get_data("SELECT * FROM policelog WHERE country_name = %s AND driver_gender = %s", (selected_country, selected_gender))

    if not df.empty:
        st.dataframe(df)

        st.markdown("### 🚗 Stop Duration Distribution")
        plt.figure(figsize=(10, 4))
        sns.countplot(data=df, x='stop_duration', palette="Blues")
        st.pyplot(plt)
    else:
        st.warning("No data found for the selected filters.")

# --- PAGE 3: SQL QUERIES ---
elif page == "📋 SQL Insights":
    st.title("🧠 Advanced SQL Insights")

    queries = {
        "1. Top 5 Most Frequent Search Types": "SELECT search_type, COUNT(*) as count FROM policelog GROUP BY search_type ORDER BY count DESC LIMIT 5;",
        "2. Top 5 Violations": "SELECT violation, COUNT(*) as count FROM policelog GROUP BY violation ORDER BY count DESC LIMIT 5;",
        "3. Arrest Rate by Country": "SELECT country_name, ROUND(SUM(is_arrested)/COUNT(*)*100, 2) as arrest_rate FROM policelog GROUP BY country_name;",
        "4. Top 5 Drug-Related Vehicles": "SELECT vehicle_number, COUNT(*) as drug_stops FROM policelog WHERE drugs_related_stop = 1 GROUP BY vehicle_number ORDER BY drug_stops DESC LIMIT 5;"
    }

    selected_query = st.selectbox("Choose a Query", list(queries.keys()))
    df_query = get_data(queries[selected_query])
    st.dataframe(df_query)

# --- PAGE 4: CREATOR INFO ---
elif page == "🙋 Creator Info":
    st.title("👩‍💻 Creator Info")
    st.markdown("""
    **Name:** S.Thenmathy 
    **Skills:** Python, SQL, Streamlit, Data Analytics  
    **Project:** Traffic Stop Prediction Dashboard  
    """)
    st.image("https://via.placeholder.com/150", caption="Project Creator", width=150)
