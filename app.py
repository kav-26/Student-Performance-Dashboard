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
# ADDITIONAL SECURITY SETTINGS
# ============================================================

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 5
INACTIVITY_TIMEOUT_MINUTES = 15


def initialize_security_state():
    """Initialize security-related session values."""
    if "failed_attempts" not in st.session_state:
        st.session_state["failed_attempts"] = 0

    if "locked_until" not in st.session_state:
        st.session_state["locked_until"] = None

    if "audit_log" not in st.session_state:
        st.session_state["audit_log"] = []

    if "last_activity" not in st.session_state:
        st.session_state["last_activity"] = None


def add_audit_event(event: str, username: str = "Unknown", status: str = "INFO"):
    """Store a security event for the current Streamlit session."""
    if "audit_log" not in st.session_state:
        st.session_state["audit_log"] = []

    st.session_state["audit_log"].append(
        {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Username": username,
            "Event": event,
            "Status": status
        }
    )


def validate_login_input(username: str, password: str):
    """Validate login form input before authentication."""
    if not username or not password:
        return False, "Please enter both username and password."

    if len(username) > 50:
        return False, "Username must not exceed 50 characters."

    if len(password) > 100:
        return False, "Password must not exceed 100 characters."

    return True, ""


initialize_security_state()


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


def test_jwt_tampering(token: str):
    """Return True when a modified JWT is correctly rejected."""
    if not token or len(token) < 2:
        return False

    # Change the final character of the signature without changing the
    # application's active authentication token. A valid verifier should reject it.
    replacement_char = "A" if token[-1] != "A" else "B"
    tampered_token = token[:-1] + replacement_char

    return verify_access_token(tampered_token) is None


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

    # Temporary lockout after repeated failed login attempts
    locked_until = st.session_state.get("locked_until")

    if locked_until is not None:
        now = datetime.now()

        if now < locked_until:
            remaining_seconds = int((locked_until - now).total_seconds())
            remaining_minutes = max(1, (remaining_seconds + 59) // 60)

            st.error(
                "🔒 Too many failed login attempts. "
                f"Please try again in approximately {remaining_minutes} minute(s)."
            )
            return

        st.session_state["failed_attempts"] = 0
        st.session_state["locked_until"] = None

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

        valid_input, validation_message = validate_login_input(
            username,
            password
        )

        if not valid_input:
            st.error(validation_message)

            add_audit_event(
                "Invalid login input",
                username or "Unknown",
                "FAILED"
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
            st.session_state["failed_attempts"] = 0
            st.session_state["locked_until"] = None
            st.session_state["last_activity"] = datetime.now()

            add_audit_event(
                "Successful login",
                username,
                "SUCCESS"
            )

            st.rerun()

        else:

            st.session_state["failed_attempts"] += 1

            attempts = st.session_state["failed_attempts"]

            add_audit_event(
                "Failed login attempt",
                username,
                "FAILED"
            )

            if attempts >= MAX_LOGIN_ATTEMPTS:

                st.session_state["locked_until"] = (
                    datetime.now()
                    + timedelta(minutes=LOCKOUT_MINUTES)
                )

                add_audit_event(
                    "Temporary login lockout",
                    username,
                    "SECURITY"
                )

                st.error(
                    "🔒 Too many failed attempts. "
                    f"Login has been locked for {LOCKOUT_MINUTES} minutes."
                )

            else:

                remaining_attempts = MAX_LOGIN_ATTEMPTS - attempts

                # Generic error prevents username enumeration
                st.error(
                    "Invalid username or password."
                )

                st.warning(
                    f"Remaining attempts before temporary lockout: "
                    f"{remaining_attempts}"
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

    add_audit_event(
        "Expired or invalid JWT",
        "Unknown",
        "SECURITY"
    )

    preserved_audit_log = st.session_state.get("audit_log", [])
    st.session_state.clear()
    st.session_state["audit_log"] = preserved_audit_log
    st.session_state["failed_attempts"] = 0
    st.session_state["locked_until"] = None
    st.session_state["authenticated"] = False

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
# INACTIVITY SESSION TIMEOUT
# ============================================================

last_activity = st.session_state.get("last_activity")
now = datetime.now()

if last_activity is not None:

    inactive_minutes = (
        now - last_activity
    ).total_seconds() / 60

    if inactive_minutes >= INACTIVITY_TIMEOUT_MINUTES:

        add_audit_event(
            "Automatic logout due to inactivity",
            username,
            "SECURITY"
        )

        preserved_audit_log = st.session_state.get("audit_log", [])
        st.session_state.clear()
        st.session_state["audit_log"] = preserved_audit_log
        st.session_state["failed_attempts"] = 0
        st.session_state["locked_until"] = None
        st.session_state["authenticated"] = False

        st.warning(
            "Your session expired due to inactivity. "
            "Please log in again."
        )

        st.stop()

st.session_state["last_activity"] = now


# ============================================================
# SIDEBAR USER INFORMATION
# ============================================================

st.sidebar.success(
    f"Logged in as: {username}"
)

st.sidebar.caption(
    f"Role: {role.capitalize()}"
)


if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True,
    key="sidebar_logout"
):
    add_audit_event(
        "User logout",
        username,
        "SUCCESS"
    )

    preserved_audit_log = st.session_state.get("audit_log", [])
    st.session_state.clear()
    st.session_state["audit_log"] = preserved_audit_log
    st.session_state["failed_attempts"] = 0
    st.session_state["locked_until"] = None
    st.session_state["authenticated"] = False

    st.rerun()


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
        "Testing & Security",
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


if data.empty:

    st.error(
        "The dataset is empty."
    )

    st.stop()


numeric_columns = [
    "Attendance_Percentage",
    "Study_Hours_per_Week",
    "LMS_Hours",
    "Internal_Marks",
    "Final_Grade"
]

invalid_numeric_columns = [
    column
    for column in numeric_columns
    if not pd.api.types.is_numeric_dtype(data[column])
]

if invalid_numeric_columns:

    st.error(
        "The following columns must contain numeric values: "
        + ", ".join(invalid_numeric_columns)
    )

    st.stop()


# ============================================================
# DATA QUALITY VALIDATION
# ============================================================

validation_issues = []

if data["Student_ID"].duplicated().any():
    duplicate_count = int(data["Student_ID"].duplicated().sum())
    validation_issues.append(
        f"Duplicate Student_ID values detected: {duplicate_count}"
    )

if data[required_columns].isnull().any().any():
    missing_value_count = int(data[required_columns].isnull().sum().sum())
    validation_issues.append(
        f"Missing values detected in required columns: {missing_value_count}"
    )

range_rules = {
    "Attendance_Percentage": (0, 100),
    "Internal_Marks": (0, 100),
    "Final_Grade": (0, 100),
    "Study_Hours_per_Week": (0, None),
    "LMS_Hours": (0, None)
}

for column, (minimum, maximum) in range_rules.items():

    if minimum is not None and (data[column] < minimum).any():
        validation_issues.append(
            f"Invalid negative/out-of-range values in {column}"
        )

    if maximum is not None and (data[column] > maximum).any():
        validation_issues.append(
            f"Values above the allowed maximum detected in {column}"
        )

if validation_issues:

    st.warning(
        "⚠️ Data quality checks detected potential issues."
    )

    st.dataframe(
        pd.DataFrame({"Validation Issue": validation_issues}),
        use_container_width=True,
        hide_index=True
    )


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

if filtered_data.empty and page not in {"Admin", "Testing & Security"}:

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

    # Log access to an individual student record once per selection.
    access_key = f"{username}:{student_id}"
    if st.session_state.get("last_student_access_key") != access_key:
        add_audit_event(
            f"Student data accessed: {student_id}",
            username,
            "DATA_ACCESS"
        )
        st.session_state["last_student_access_key"] = access_key


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
# TESTING & SECURITY
# ============================================================

elif page == "Testing & Security":

    if role != "admin":

        add_audit_event(
            "Unauthorized Testing & Security access attempt",
            username,
            "DENIED"
        )

        st.error(
            "🚫 Access Denied"
        )

        st.warning(
            "Only administrators can access "
            "the Testing & Security page."
        )

        st.stop()

    st.title(
        "🧪 Testing & Security"
    )

    st.caption(
        "Verification of application functionality, "
        "authentication, authorization, validation, and security controls."
    )

    st.subheader(
        "🟢 Security Status"
    )

    jwt_tamper_passed = test_jwt_tampering(token)

    security_status = pd.DataFrame(
        {
            "Security Area": [
                "Authentication",
                "Password Hashing",
                "JWT Authentication",
                "JWT Expiration",
                "JWT Tampering Detection",
                "Role-Based Authorization",
                "Failed Login Protection",
                "Session Inactivity Timeout",
                "Input Validation",
                "Dataset Validation",
                "Audit Logging",
                "Student Data Access Logging",
                "Secret Management"
            ],
            "Status": [
                "✅ Active" if st.session_state.get("authenticated") else "❌ Inactive",
                "✅ Implemented",
                "✅ Active" if payload is not None else "❌ Failed",
                "✅ Implemented",
                "✅ PASS" if jwt_tamper_passed else "❌ FAIL",
                "✅ Active" if role in allowed_roles else "❌ Failed",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented"
            ]
        }
    )

    st.dataframe(
        security_status,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "🛡️ Implemented Security Controls"
    )

    security_controls = pd.DataFrame(
        {
            "Security Control": [
                "Password Hashing",
                "JWT Authentication",
                "JWT Expiration",
                "Role-Based Access Control",
                "Secret Management",
                "Failed Login Protection",
                "Audit Logging",
                "Session Logout",
                "Inactivity Timeout"
            ],
            "Implementation": [
                "bcrypt",
                "PyJWT",
                f"{JWT_EXPIRATION_MINUTES} minutes",
                "Admin / Analyst roles",
                "Streamlit Secrets",
                f"{MAX_LOGIN_ATTEMPTS} attempts / {LOCKOUT_MINUTES} min lockout",
                "Session security event log",
                "Session state cleared on logout",
                f"{INACTIVITY_TIMEOUT_MINUTES} minutes"
            ],
            "Status": [
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented",
                "✅ Implemented"
            ]
        }
    )

    st.dataframe(
        security_controls,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "🧪 Test Cases"
    )

    st.info(
        "Run these cases manually before your final demonstration. "
        "Mark a test as PASS only after you have actually verified it."
    )

    test_cases = pd.DataFrame(
        {
            "Test Case": [
                "Valid admin login",
                "Valid analyst login",
                "Invalid username",
                "Invalid password",
                "Empty login fields",
                "Five failed login attempts",
                "JWT validation",
                "JWT expiration",
                "Admin page authorization",
                "Analyst admin restriction",
                "Logout",
                "Dataset file validation",
                "Required-column validation",
                "Numeric-column validation",
                "Empty filter result"
            ],
            "Expected Result": [
                "Admin dashboard opens",
                "Analyst dashboard opens",
                "Login is rejected",
                "Login is rejected",
                "Validation message is displayed",
                "Temporary login lockout is triggered",
                "Valid token permits access",
                "Expired token requires a new login",
                "Admin can access administration",
                "Analyst cannot access administration",
                "Session is cleared",
                "Missing dataset shows an error",
                "Missing columns show an error",
                "Invalid numeric columns show an error",
                "Warning is displayed without crashing"
            ]
        }
    )

    st.dataframe(
        test_cases,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "🔐 Security & Authorization Test Matrix"
    )

    security_test_matrix = pd.DataFrame(
        {
            "Test": [
                "Correct credentials",
                "Wrong username",
                "Wrong password",
                "Repeated failed login",
                "Analyst opens Admin page",
                "Tampered JWT",
                "Expired JWT",
                "Logout",
                "Inactivity timeout"
            ],
            "Expected Result": [
                "Login succeeds",
                "Login rejected without revealing account details",
                "Login rejected without revealing account details",
                "Temporary lockout after 5 failures",
                "Access denied",
                "Token rejected and session ended",
                "Token rejected and login required",
                "Authentication state cleared",
                "Automatic logout after 15 minutes"
            ],
            "Status": [
                "PASS - Live",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "PASS" if jwt_tamper_passed else "FAIL",
                "Not Run",
                "Not Run",
                "Not Run"
            ]
        }
    )

    st.dataframe(
        security_test_matrix,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "📏 Risk Classification Boundary Tests"
    )

    boundary_tests = pd.DataFrame(
        {
            "Test Input": [
                "Final Grade = 49",
                "Final Grade = 50",
                "Final Grade = 64",
                "Final Grade = 65",
                "Attendance = 59",
                "Attendance = 60",
                "Attendance = 74",
                "Attendance = 75"
            ],
            "Expected Rule Behavior": [
                "High Risk",
                "Not High due to grade alone",
                "Medium Risk",
                "Low Risk if attendance is safe",
                "High Risk",
                "Not High due to attendance alone",
                "Medium Risk",
                "Low Risk if grade is also safe"
            ],
            "Status": [
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run"
            ]
        }
    )

    st.dataframe(
        boundary_tests,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "📊 Data Quality Tests"
    )

    data_quality_tests = pd.DataFrame(
        {
            "Test": [
                "Missing dataset",
                "Missing required column",
                "Invalid numeric type",
                "Missing values",
                "Duplicate Student_ID",
                "Negative study/LMS hours",
                "Attendance below 0 or above 100",
                "Marks/grade below 0 or above 100"
            ],
            "Expected Result": [
                "Controlled error message",
                "Controlled validation error",
                "Controlled validation error",
                "Warning identifies missing values",
                "Warning identifies duplicates",
                "Warning identifies invalid values",
                "Warning identifies invalid range",
                "Warning identifies invalid range"
            ],
            "Status": [
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run"
            ]
        }
    )

    st.dataframe(
        data_quality_tests,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "🖥️ Functional Dashboard Tests"
    )

    functional_tests = pd.DataFrame(
        {
            "Test": [
                "Sidebar navigation",
                "Gender filter",
                "Attendance filter",
                "Grade filter",
                "Study-hours filter",
                "Student drill-down",
                "Charts and visualizations",
                "Performance heatmap",
                "Empty filter result",
                "Admin page",
                "Logout"
            ],
            "Expected Result": [
                "Each page opens correctly",
                "Results update correctly",
                "Results update correctly",
                "Results update correctly",
                "Results update correctly",
                "Selected student details display",
                "Charts render without errors",
                "Heatmap renders correctly",
                "Controlled warning is shown",
                "Admin information is accessible only to admin",
                "User is returned to login"
            ],
            "Status": [
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run",
                "Not Run"
            ]
        }
    )

    st.dataframe(
        functional_tests,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "👩‍🎓 Student Data Access Logging"
    )

    data_access_events = [
        event for event in st.session_state.get("audit_log", [])
        if event.get("Event", "").startswith("Student data accessed")
    ]

    if data_access_events:
        st.dataframe(
            pd.DataFrame(data_access_events),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No student-record access has been logged during the current session. "
            "Open Student Drill-Down and select a student to generate an access event."
        )

    st.markdown("---")

    st.subheader(
        "📊 Current Runtime Checks"
    )

    runtime_checks = pd.DataFrame(
        {
            "Check": [
                "User Authenticated",
                "JWT Valid",
                "Role Valid",
                "Dataset Loaded",
                "Required Columns Present",
                "Dataset Contains Records"
            ],
            "Result": [
                "PASS" if st.session_state.get("authenticated") else "FAIL",
                "PASS" if payload is not None else "FAIL",
                "PASS" if role in allowed_roles else "FAIL",
                "PASS" if data is not None else "FAIL",
                "PASS" if not missing_columns else "FAIL",
                "PASS" if not data.empty else "FAIL"
            ]
        }
    )

    st.dataframe(
        runtime_checks,
        use_container_width=True,
        hide_index=True
    )

    passed_runtime = (
        runtime_checks["Result"] == "PASS"
    ).sum()

    col1, col2 = st.columns(2)

    col1.metric(
        "Runtime Checks",
        len(runtime_checks)
    )

    col2.metric(
        "Runtime Checks Passed",
        int(passed_runtime)
    )

    st.markdown("---")

    st.subheader(
        "📋 Security Audit Log"
    )

    audit_log = st.session_state.get(
        "audit_log",
        []
    )

    if audit_log:

        audit_df = pd.DataFrame(
            audit_log
        )

        st.dataframe(
            audit_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No security events have been recorded "
            "during the current application session."
        )


# ============================================================
# ADMINISTRATION
# ============================================================

elif page == "Admin":

    # ========================================================
    # SERVER-SIDE AUTHORIZATION
    # ========================================================

    if role != "admin":

        add_audit_event(
            "Unauthorized Admin access attempt",
            username,
            "DENIED"
        )

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

        st.write(
            "🚫 **Failed Login Protection**"
        )

        st.success(
            f"{MAX_LOGIN_ATTEMPTS} attempts / "
            f"{LOCKOUT_MINUTES} min lockout"
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

        st.write(
            "📋 **Audit Logging**"
        )

        st.success(
            "Enabled"
        )

        st.write(
            "⏳ **Inactivity Timeout**"
        )

        st.success(
            f"{INACTIVITY_TIMEOUT_MINUTES} minutes"
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
    