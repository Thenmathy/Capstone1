import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import plotly.express as px
import json

# DB Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="09876",
    database="Secureledger"
)
cursor = mydb.cursor()

st.set_page_config(page_title="🚦 Traffic Check Post System", layout="wide")
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "👮 Officer Login", "📋 Vehicle Logs", "🧾 Add Police Log + Predict", "🤮 Advanced Insights", "📢 Creator Info"])

st.sidebar.markdown("## 🔎 SQL Filters")
def fetch_options(col_name):
    cursor.execute(f"SELECT DISTINCT {col_name} FROM policelog")
    return [row[0] for row in cursor.fetchall()]
selected_country = st.sidebar.selectbox("Country", ["All"] + fetch_options("country_name"))
selected_gender = st.sidebar.selectbox("Gender", ["All"] + fetch_options("driver_gender"))
selected_violation = st.sidebar.selectbox("Violation", ["All"] + fetch_options("violation"))

def apply_filters(df):
    if selected_country != "All":
        df = df[df['country_name'] == selected_country]
    if selected_gender != "All":
        df = df[df['driver_gender'] == selected_gender]
    if selected_violation != "All":
        df = df[df['violation'] == selected_violation]
    return df

if page == "🏠 Home":
    st.title("🚦 Traffic Check Post Management Dashboard")
    st.markdown("### Welcome to the Real-Time Traffic Log and Analytics Platform")
    cursor.execute("SELECT * FROM policelog")
    df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)

    st.subheader("📈 Violation Frequency")
    violation_counts = df['violation'].value_counts().reset_index()
    violation_counts.columns = ['violation', 'count']
    violation_fig = px.bar(
        violation_counts,
        x='violation',
        y='count',
        labels={'violation': 'Violation', 'count': 'Count'}
    )
    st.plotly_chart(violation_fig, use_container_width=True)

    st.subheader("📈 Search Conducted Breakdown")
    search_fig = px.pie(df, names='search_conducted', title='Search Conducted Share')
    st.plotly_chart(search_fig, use_container_width=True)

    st.subheader("📈 Arrest Outcome Count")
    arrest_fig = px.histogram(df, x='stop_outcome', color='is_arrested', barmode='group')
    st.plotly_chart(arrest_fig, use_container_width=True)

    st.subheader("🚘 High-Risk Vehicles (Drug-Related Stops)")
    risky_vehicles = df[df['drugs_related_stop'] == "Yes"]['vehicle_number'].value_counts().reset_index()
    risky_vehicles.columns = ['vehicle_number', 'drug_related_stops']
    high_risk_fig = px.bar(risky_vehicles.head(10), x='vehicle_number', y='drug_related_stops',
                           labels={'vehicle_number': 'Vehicle Number', 'drug_related_stops': 'Drug-Related Stops'},
                           title='Top 10 High-Risk Vehicles')
    st.plotly_chart(high_risk_fig, use_container_width=True)

elif page == "👮 Officer Login":
    st.header("👮 Officer Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "officer" and password == "1234":
            st.success(f"Welcome Officer: {username.upper()} 👮‍♂️")
        else:
            st.error("Invalid credentials. Try 'officer' / '1234'")

elif page == "📋 Vehicle Logs":
    st.header("📋 Traffic Stop Logs, Violations, and Officer Reports")
    cursor.execute("SELECT * FROM policelog")
    df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
    df_filtered = apply_filters(df)
    st.dataframe(df_filtered, use_container_width=True)

    if not df_filtered.empty:
        st.download_button("📅 Export Filtered Data", data=df_filtered.to_csv(index=False), file_name="filtered_logs.csv", mime="text/csv")

        st.subheader("📈 Violation Frequency")
        violation_counts_filtered = df_filtered['violation'].value_counts().reset_index()
        violation_counts_filtered.columns = ['violation', 'count']
        fig = px.bar(violation_counts_filtered, x='violation', y='count', labels={'violation': 'Violation', 'count': 'Count'})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📰 Officer Narrative Report")
        selected_row = st.selectbox("Select a row to generate a narrative:", df_filtered.index)
        row = df_filtered.loc[selected_row]

        narrative = f"🚗 A {row['driver_age']}-year-old {row['driver_gender']} driver was stopped for {row['violation']} at {row['stop_time']}. "
        narrative += "No search was conducted, " if row['search_conducted'] == "No" else "A search was conducted, "
        narrative += f"and he received a {row['stop_outcome'].lower()}. "
        narrative += f"The stop lasted {row['stop_duration']} and was "
        narrative += "drug-related." if row['drugs_related_stop'] == "Yes" else "not drug-related."
        st.success(narrative)
    else:
        st.warning("No records match the selected filters.")

elif page == "🧾 Add Police Log + Predict":
    st.header("📝 Add New Police Log & Predict Outcome and Violation")
    with st.form("police_log_form"):
        stop_date = st.date_input("Stop Date")
        stop_time = st.time_input("Stop Time")
        country_name = st.text_input("Country Name")
        driver_gender = st.selectbox("Driver Gender", ["male", "female"])
        driver_age = st.number_input("Driver Age", min_value=16, max_value=100, step=1)
        driver_race = st.text_input("Driver Race")
        violation_raw = st.text_input("Violation Raw")
        violation = st.text_input("Violation")
        search_conducted = st.selectbox("Was a Search Conducted?", ["Yes", "No"])
        search_type = st.text_input("Search Type")
        is_arrested = st.selectbox("Was Arrest Made?", ["Yes", "No"])
        drugs_related_stop = st.selectbox("Was it Drug Related?", ["Yes", "No"])
        stop_duration = st.text_input("Stop Duration (e.g., 0-15 Min)")
        vehicle_number = st.text_input("Vehicle Number")
        submitted = st.form_submit_button("Predict Stop Outcome & Violation")

        if submitted:
            st.success("✅ Prediction complete (this is a placeholder). ML model will be integrated here.")

            try:
                gender_short = "M" if driver_gender.lower().startswith("m") else "F"
                summary_query = """
                    SELECT violation, stop_outcome, COUNT(*) as freq
                    FROM policelog
                    WHERE driver_gender = %s AND driver_race = %s AND country_name = %s
                    GROUP BY violation, stop_outcome
                    ORDER BY freq DESC
                    LIMIT 1;
                """
                cursor.execute(summary_query, (gender_short, driver_race, country_name))
                result = cursor.fetchone()
                if result:
                    top_violation, top_outcome, freq = result
                    search_phrase = "A search was conducted" if search_conducted == "Yes" else "No search was conducted"
                    drug_phrase = "and was drug-related." if drugs_related_stop == "Yes" else "and was not drug-related."
                    detailed_summary = f"🚗 A {driver_age}-year-old {driver_race} {driver_gender} driver was stopped for {top_violation} at {stop_time}. "
                    detailed_summary += f"{search_phrase}, and received a {top_outcome.lower()}. "
                    detailed_summary += f"The stop lasted {stop_duration} {drug_phrase}"
                    st.success(detailed_summary)
                else:
                    st.info("No historical data found to summarize this combination.")
            except Exception as e:
                st.error(f"❌ Error generating summary: {e}")

elif page == "🤮 Advanced Insights":
    st.header("📈 Advanced SQL-Based Traffic Insights")
    with open("single_line_query_map.json", "r") as f:
        query_map = json.load(f)
    query_selected = st.selectbox("Select a Query to Run", list(query_map.keys()))
    if st.button("Run Query"):
        sql_query = query_map[query_selected]
        cursor.execute(sql_query)
        results = cursor.fetchall()
        df_result = pd.DataFrame(results, columns=cursor.column_names)
        st.dataframe(df_result, use_container_width=True)

elif page == "📢 Creator Info":
    st.header("👤 Project Created By")
    st.markdown("""
    **Name:** Then  
    **Project:** SecureLedger Traffic Stop Analytics  
    **Tools Used:** Streamlit, MySQL, Python, Plotly  
    **Features:**  
    - Real-Time Police Log Entry  
    - SQL-Based Advanced Querying  
    - Predictive Modeling (ML model coming)  
    - Officer Login & Interactive Filters  
    """)
