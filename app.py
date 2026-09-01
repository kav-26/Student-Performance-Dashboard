import streamlit as st
import pandas as pd
import plotly.express as px
import bcrypt
import jwt

from datetime import datetime, timedelta, timezone


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# SECURITY CONFIGURATION
# ============================================================

# IMPORTANT:
# JWT_SECRET_KEY and user credentials must be stored in
# .streamlit/secrets.toml and NEVER committed to GitHub.

try:
    JWT_SECRET_KEY = st.secrets["JWT_SECRET_KEY"]

    JWT_ALGORITHM = st.secrets.get(
        "JWT_ALGORITHM",
        "HS256"
    )

    JWT_EXPIRATION_MINUTES = int(
        st.secrets.get(
            "JWT_EXPIRATION_MINUTES",
            30
        )
    )

except Exception:
    st.error(
        "Security configuration is missing. "
        "Please configure JWT_SECRET_KEY in "
        ".streamlit/secrets.toml."
    )
    st.stop()


# ============================================================
# USER AUTHENTICATION
# ============================================================

def verify_user(username: str, password: str):
    """
    Verify username and password using bcrypt.

    Returns the user's role if authentication succeeds.
    Returns None if authentication fails.
    """

    try:
        users = st.secrets["users"]
    except Exception:
        return None

    if username not in users:
        return None

    stored_hash = users[username]["password_hash"]
    role = users[username]["role"]

    try:
        password_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )

    except (ValueError, TypeError):
        return None

    if password_valid:
        return role

    return None


# ============================================================
# JWT FUNCTIONS
# ============================================================

def create_access_token(username: str, role: str):
    """
    Create a short-lived JWT access token.
    """

    now = datetime.now(timezone.utc)

    expiration = now + timedelta(
        minutes=JWT_EXPIRATION_MINUTES
    )

    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": expiration
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


def verify_access_token(token: str):
    """
    Verify JWT signature and expiration.

    Returns payload if valid.
    Returns None if invalid or expired.
    """

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.title("🎓 Student Performance Analytics")

    st.subheader("🔐 Secure Login")

    st.write(
        "Please enter your credentials to access "
        "the analytics dashboard."
    )

    username = st.text_input(
        "Username",
        max_chars=50
    )

    password = st.text_input(
        "Password",
        type="password",
        max_chars=100
    )

    login_button = st.button(
        "Login",
        type="primary",
        use_container_width=True
    )

    if login_button:

        # Basic input validation
        if not username or not password:

            st.error(
                "Please enter both username and password."
            )

            return

        role = verify_user(
            username,
            password
        )

        if role:

            token = create_access_token(
                username=username,
                role=role
            )

            st.session_state["authenticated"] = True
            st.session_state["token"] = token

            st.rerun()

        else:

            # Generic error prevents username enumeration
            st.error(
                "Invalid username or password."
            )


# ============================================================
# INITIALIZE SESSION
# ============================================================

if "authenticated" not in st.session_state:

    st.session_state["authenticated"] = False


# ============================================================
# AUTHENTICATION CHECK
# ============================================================

if not st.session_state["authenticated"]:

    login_page()

    st.stop()


# ============================================================
# JWT VALIDATION
# ============================================================

token = st.session_state.get(
    "token"
)

payload = verify_access_token(
    token
)

if payload is None:

    st.session_state.clear()

    st.warning(
        "Your session has expired. "
        "Please log in again."
    )

    st.stop()


# ============================================================
# GET USER INFORMATION FROM JWT
# ============================================================

username = payload.get("sub")
role = payload.get("role")


# ============================================================
# VALIDATE ROLE
# ============================================================

allowed_roles = {
    "admin",
    "analyst"
}

if role not in allowed_roles:

    st.session_state.clear()

    st.error(
        "Invalid user role."
    )

    st.stop()


# ============================================================
# SIDEBAR USER INFORMATION
# ============================================================

st.sidebar.success(
    f"Logged in as: {username}"
)

st.sidebar.caption(
    f"Role: {role.capitalize()}"
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title(
    "🎓 Dashboard Navigation"
)


if role == "admin":

    pages = [
        "Overview",
        "At-Risk Analysis",
        "Student Drill-Down",
        "Visual Analysis",
        "Performance Heatmap",
        "Insights",
        "Admin"
    ]

else:

    pages = [
        "Overview",
        "At-Risk Analysis",
        "Student Drill-Down",
        "Visual Analysis",
        "Performance Heatmap",
        "Insights"
    ]


page = st.sidebar.radio(
    "Go to",
    pages
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    return pd.read_csv(
        "student_academic_performance_dataset.csv"
    )


try:

    data = load_data()

except FileNotFoundError:

    st.error(
        "Dataset file not found. "
        "Please make sure "
        "'student_academic_performance_dataset.csv' "
        "is present in the project folder."
    )

    st.stop()

except Exception:

    st.error(
        "Unable to load the dataset."
    )

    st.stop()


# ============================================================
# BASIC DATA VALIDATION
# ============================================================

required_columns = [
    "Student_ID",
    "Gender",
    "Attendance_Percentage",
    "Study_Hours_per_Week",
    "LMS_Hours",
    "Internal_Marks",
    "Final_Grade"
]


missing_columns = [
    column
    for column in required_columns
    if column not in data.columns
]


if missing_columns:

    st.error(
        "Dataset is missing required columns: "
        + ", ".join(missing_columns)
    )

    st.stop()


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def assign_risk(row):

    if (
        row["Final_Grade"] < 50
        or row["Attendance_Percentage"] < 60
    ):

        return "High Risk"

    elif (
        row["Final_Grade"] < 65
        or row["Attendance_Percentage"] < 75
    ):

        return "Medium Risk"

    else:

        return "Low Risk"


data["Risk_Level"] = data.apply(
    assign_risk,
    axis=1
)


# ============================================================
# FILTERS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.header(
    "🔎 Filters"
)


gender_options = sorted(
    data["Gender"]
    .dropna()
    .unique()
    .tolist()
)


risk_options = [
    "High Risk",
    "Medium Risk",
    "Low Risk"
]


gender_filter = st.sidebar.multiselect(
    "Gender",
    options=gender_options,
    default=gender_options
)


risk_filter = st.sidebar.multiselect(
    "Risk Level",
    options=risk_options,
    default=risk_options
)


attendance_min = int(
    data["Attendance_Percentage"].min()
)

attendance_max = int(
    data["Attendance_Percentage"].max()
)


attendance_range = st.sidebar.slider(
    "Attendance (%)",
    attendance_min,
    attendance_max,
    (
        max(attendance_min, 60),
        attendance_max
    )
)


grade_min = int(
    data["Final_Grade"].min()
)

grade_max = int(
    data["Final_Grade"].max()
)


grade_range = st.sidebar.slider(
    "Final Grade",
    grade_min,
    grade_max,
    (
        max(grade_min, 40),
        grade_max
    )
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_data = data[
    (data["Gender"].isin(gender_filter))
    &
    (data["Risk_Level"].isin(risk_filter))
    &
    (
        data["Attendance_Percentage"].between(
            *attendance_range
        )
    )
    &
    (
        data["Final_Grade"].between(
            *grade_range
        )
    )
].copy()


# ============================================================
# EMPTY DATA PROTECTION
# ============================================================

if filtered_data.empty and page != "Admin":

    st.warning(
        "⚠️ No students match the selected filters. "
        "Please adjust the filters."
    )

    st.stop()


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.title(
        "📊 Academic Performance Overview"
    )

    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Total Students",
        len(filtered_data)
    )


    high_risk_count = len(
        filtered_data[
            filtered_data["Risk_Level"]
            == "High Risk"
        ]
    )


    col2.metric(
        "High-Risk Students",
        high_risk_count
    )


    average_grade = filtered_data[
        "Final_Grade"
    ].mean()


    col3.metric(
        "Average Grade",
        round(average_grade, 2)
    )


    fig = px.histogram(
        filtered_data,
        x="Final_Grade",
        color="Risk_Level",
        nbins=20,
        title="Grade Distribution by Risk Level"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# AT-RISK ANALYSIS
# ============================================================

elif page == "At-Risk Analysis":

    st.title(
        "🚨 At-Risk Students"
    )


    at_risk_data = filtered_data[
        filtered_data["Risk_Level"]
        != "Low Risk"
    ]


    display_columns = [
        "Student_ID",
        "Gender",
        "Attendance_Percentage",
        "Study_Hours_per_Week",
        "Final_Grade",
        "Risk_Level"
    ]


    st.dataframe(
        at_risk_data[display_columns],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# STUDENT DRILL-DOWN
# ============================================================

elif page == "Student Drill-Down":

    st.title(
        "🔍 Student Drill-Down"
    )


    student_ids = (
        filtered_data["Student_ID"]
        .dropna()
        .unique()
    )


    if len(student_ids) == 0:

        st.warning(
            "No students available "
            "with the selected filters."
        )

        st.stop()


    student_id = st.selectbox(
        "Select Student",
        student_ids
    )


    student_rows = filtered_data[
        filtered_data["Student_ID"]
        == student_id
    ]


    if student_rows.empty:

        st.warning(
            "Student information is unavailable."
        )

        st.stop()


    student = student_rows.iloc[0]


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Attendance (%)",
        student["Attendance_Percentage"]
    )


    col2.metric(
        "Study Hours / Week",
        student["Study_Hours_per_Week"]
    )


    col3.metric(
        "Final Grade",
        student["Final_Grade"]
    )


    st.info(
        f"📌 Risk Level: "
        f"**{student['Risk_Level']}**"
    )


# ============================================================
# VISUAL ANALYSIS
# ============================================================

elif page == "Visual Analysis":

    st.title(
        "📈 Visual Analysis"
    )


    # Attendance vs Final Grade

    st.subheader(
        "🎯 Attendance vs Final Grade"
    )


    fig1 = px.scatter(
        filtered_data,
        x="Attendance_Percentage",
        y="Final_Grade",
        color="Risk_Level",
        hover_data=["Student_ID"],
        title=(
            "Attendance vs Final Grade "
            "by Risk Level"
        )
    )


    st.plotly_chart(
        fig1,
        use_container_width=True
    )


    # Study Hours vs Final Grade

    st.subheader(
        "📘 Study Hours vs Final Grade"
    )


    fig2 = px.scatter(
        filtered_data,
        x="Study_Hours_per_Week",
        y="Final_Grade",
        color="Risk_Level",
        title="Study Hours vs Final Grade"
    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )


    # Average Grade by Risk Level

    st.subheader(
        "📊 Average Grade by Risk Level"
    )


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
        color="Risk_Level",
        title="Average Grade by Risk Level"
    )


    st.plotly_chart(
        fig3,
        use_container_width=True
    )


    # Box Plot

    st.subheader(
        "🎭 When Averages Mislead"
    )


    fig4 = px.box(
        filtered_data,
        x="Risk_Level",
        y="Final_Grade",
        color="Risk_Level",
        points="all",
        title=(
            "Grade Spread Within Each Risk Level"
        )
    )


    st.plotly_chart(
        fig4,
        use_container_width=True
    )


# ============================================================
# PERFORMANCE HEATMAP
# ============================================================

elif page == "Performance Heatmap":

    st.title(
        "🔥 Performance Correlation Heatmap"
    )


    heatmap_cols = [
        "Attendance_Percentage",
        "Study_Hours_per_Week",
        "LMS_Hours",
        "Internal_Marks",
        "Final_Grade"
    ]


    heatmap_data = (
        filtered_data[heatmap_cols]
        .dropna()
    )


    if heatmap_data.empty:

        st.warning(
            "⚠️ Not enough data for heatmap "
            "with current filters."
        )

    else:

        corr = heatmap_data.corr()


        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdYlGn",
            title=(
                "Correlation Between "
                "Academic Factors"
            )
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# INSIGHTS
# ============================================================

elif page == "Insights":

    st.title(
        "🧠 Key Insights"
    )


    st.markdown(
        """
        **What this dashboard reveals**

        - Attendance alone is not a success guarantee
        - Consistency beats intensity
        - Early decline can indicate potential academic difficulty
        - Medium-risk students can be important intervention targets
        """
    )


    st.subheader(
        "🚦 Early Warning Signals"
    )


    st.markdown(
        """
        - Attendance below **75%**
        - Grades below **65**
        - Low LMS engagement
        """
    )


# ============================================================
# ADMINISTRATION
# ============================================================

elif page == "Admin":

    # ========================================================
    # SERVER-SIDE AUTHORIZATION
    # ========================================================

    if role != "admin":

        st.error(
            "🚫 Access Denied"
        )

        st.warning(
            "Only administrators can access "
            "this page."
        )

        st.stop()


    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.title(
        "🔐 Administration"
    )

    st.caption(
        "System, access, and security management"
    )


    # ========================================================
    # ADMINISTRATOR SESSION
    # ========================================================

    st.subheader(
        "👤 Administrator Session"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Username",
            username
        )


    with col2:

        st.metric(
            "Role",
            "Administrator"
        )


    with col3:

        st.metric(
            "Session Status",
            "🟢 Active"
        )


    st.markdown("---")


    # ========================================================
    # SECURITY CONFIGURATION
    # ========================================================

    st.subheader(
        "🛡️ Security Configuration"
    )


    security_col1, security_col2 = st.columns(2)


    with security_col1:

        st.write(
            "🔐 **Authentication**"
        )

        st.success(
            "Enabled"
        )


        st.write(
            "🔑 **Password Hashing**"
        )

        st.success(
            "bcrypt"
        )


        st.write(
            "🎟️ **Token Authentication**"
        )

        st.success(
            "JWT"
        )


    with security_col2:

        st.write(
            "👥 **Role-Based Authorization**"
        )

        st.success(
            "Enabled"
        )


        st.write(
            "⏱️ **JWT Expiration**"
        )

        st.info(
            f"{JWT_EXPIRATION_MINUTES} minutes"
        )


        st.write(
            "🔒 **Secret Management**"
        )

        st.success(
            "Externalized"
        )


    st.markdown("---")


    # ========================================================
    # APPLICATION HEALTH
    # ========================================================

    st.subheader(
        "🟢 Application Health"
    )


    health_col1, health_col2, health_col3 = st.columns(3)


    with health_col1:

        st.success(
            "Dashboard\n\nOperational"
        )


    with health_col2:

        st.success(
            "Dataset\n\nLoaded"
        )


    with health_col3:

        st.success(
            "Authentication\n\nOperational"
        )


    st.markdown("---")


    # ========================================================
    # ACCESS CONTROL
    # ========================================================

    st.subheader(
        "👥 Access Control"
    )


    access_data = pd.DataFrame({

        "Role": [
            "Administrator",
            "Analyst"
        ],

        "Dashboard Access": [
            "✅ Full",
            "✅ Full"
        ],

        "Administration": [
            "✅ Allowed",
            "❌ Restricted"
        ],

        "Student Analytics": [
            "✅ Allowed",
            "✅ Allowed"
        ]

    })


    st.dataframe(
        access_data,
        use_container_width=True,
        hide_index=True
    )


    st.markdown("---")


    # ========================================================
    # SESSION INFORMATION
    # ========================================================

    st.subheader(
        "🎫 Session Information"
    )


    session_col1, session_col2 = st.columns(2)


    with session_col1:

        st.write(
            f"**Authenticated User:** {username}"
        )

        st.write(
            f"**Current Role:** {role}"
        )


    with session_col2:

        st.write(
            "**Token Type:** JWT"
        )

        st.write(
            f"**Session Lifetime:** "
            f"{JWT_EXPIRATION_MINUTES} minutes"
        )


    st.markdown("---")


    # ========================================================
    # ADMINISTRATIVE ACTIONS
    # ========================================================

    st.subheader(
        "⚙️ Administrative Actions"
    )


    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.clear()

        st.rerun()

    