import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Student Performance Analytics",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("student_academic_performance_dataset.csv")

data = load_data()

# ---------------- RISK CLASSIFICATION ----------------
def assign_risk(row):
    if row["Final_Grade"] < 50 or row["Attendance_Percentage"] < 60:
        return "High Risk"
    elif row["Final_Grade"] < 65 or row["Attendance_Percentage"] < 75:
        return "Medium Risk"
    else:
        return "Low Risk"

data["Risk_Level"] = data.apply(assign_risk, axis=1)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🎓 Dashboard Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "At-Risk Analysis",
        "Student Drill-Down",
        "Visual Analysis",
        "Performance Heatmap",
        "Insights"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("🔎 Filters")

gender_filter = st.sidebar.multiselect(
    "Gender",
    options=data["Gender"].unique(),
    default=data["Gender"].unique()
)

risk_filter = st.sidebar.multiselect(
    "Risk Level",
    options=data["Risk_Level"].unique(),
    default=data["Risk_Level"].unique()
)

attendance_range = st.sidebar.slider(
    "Attendance (%)",
    int(data["Attendance_Percentage"].min()),
    int(data["Attendance_Percentage"].max()),
    (60, 100)
)

grade_range = st.sidebar.slider(
    "Final Grade",
    int(data["Final_Grade"].min()),
    int(data["Final_Grade"].max()),
    (40, 100)
)

filtered_data = data[
    (data["Gender"].isin(gender_filter)) &
    (data["Risk_Level"].isin(risk_filter)) &
    (data["Attendance_Percentage"].between(*attendance_range)) &
    (data["Final_Grade"].between(*grade_range))
]

# ---------------- OVERVIEW ----------------
if page == "Overview":
    st.title("📊 Academic Performance Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", len(filtered_data))
    col2.metric(
        "High-Risk Students",
        len(filtered_data[filtered_data["Risk_Level"] == "High Risk"])
    )
    col3.metric(
        "Average Grade",
        round(filtered_data["Final_Grade"].mean(), 2)
    )

    fig = px.histogram(
        filtered_data,
        x="Final_Grade",
        color="Risk_Level",
        nbins=20,
        title="Grade Distribution by Risk Level"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- AT-RISK ANALYSIS ----------------
elif page == "At-Risk Analysis":
    st.title("🚨 At-Risk Students")

    st.dataframe(
        filtered_data[filtered_data["Risk_Level"] != "Low Risk"][
            [
                "Student_ID",
                "Gender",
                "Attendance_Percentage",
                "Study_Hours_per_Week",
                "Final_Grade",
                "Risk_Level"
            ]
        ],
        use_container_width=True
    )

# ---------------- STUDENT DRILL-DOWN ----------------
elif page == "Student Drill-Down":
    st.title("🔍 Student Drill-Down")

    student_id = st.selectbox(
        "Select Student",
        filtered_data["Student_ID"].unique()
    )

    student = filtered_data[
        filtered_data["Student_ID"] == student_id
    ].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Attendance (%)", student["Attendance_Percentage"])
    col2.metric("Study Hours / Week", student["Study_Hours_per_Week"])
    col3.metric("Final Grade", student["Final_Grade"])

    st.info(f"📌 Risk Level: **{student['Risk_Level']}**")

# ---------------- VISUAL ANALYSIS ----------------
elif page == "Visual Analysis":
    st.title("📈 Visual Analysis")

    st.subheader("🎯 Attendance vs Final Grade")
    fig1 = px.scatter(
        filtered_data,
        x="Attendance_Percentage",
        y="Final_Grade",
        color="Risk_Level",
        hover_data=["Student_ID"]
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📘 Study Hours vs Final Grade")
    fig2 = px.scatter(
        filtered_data,
        x="Study_Hours_per_Week",
        y="Final_Grade",
        color="Risk_Level"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📊 Average Grade by Risk Level")
    avg = (
        filtered_data
        .groupby("Risk_Level")["Final_Grade"]
        .mean()
        .reset_index()
    )
    fig3 = px.bar(
        avg,
        x="Risk_Level",
        y="Final_Grade",
        color="Risk_Level"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🎭 When Averages Mislead")
    fig4 = px.box(
        filtered_data,
        x="Risk_Level",
        y="Final_Grade",
        color="Risk_Level",
        points="all",
        title="Grade Spread Within Each Risk Level"
    )
    st.plotly_chart(fig4, use_container_width=True)

# ---------------- HEATMAP ----------------
elif page == "Performance Heatmap":
    st.title("🔥 Performance Correlation Heatmap")

    heatmap_cols = [
        "Attendance_Percentage",
        "Study_Hours_per_Week",
        "LMS_Hours",
        "Internal_Marks",
        "Final_Grade"
    ]

    heatmap_data = filtered_data[heatmap_cols].dropna()

    if heatmap_data.empty:
        st.warning("⚠️ Not enough data for heatmap with current filters.")
    else:
        corr = heatmap_data.corr()
        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------- INSIGHTS ----------------
elif page == "Insights":
    st.title("🧠 Key Insights")

    st.markdown("""
    **What this dashboard reveals**
    - Attendance alone is not a success guarantee  
    - Consistency beats intensity  
    - Early decline predicts final failure  
    - Medium-risk students are the **best intervention targets**
    """)

    st.subheader("🚦 Early Warning Signals")
    st.markdown("""
    - Attendance below **75%**  
    - Grades trending below **65**  
    - Low LMS engagement  
    """)

    