# 🎓 Student Performance Analytics Dashboard

An interactive web-based dashboard built with **Python and Streamlit** to analyze student academic performance, identify at-risk students, explore relationships between academic factors, and provide interactive visual insights.

🔗 **Live Demo:** https://kav-26-student-performance-dashboard-app-ghfwnu.streamlit.app/

---

## 📌 Project Overview

Educational institutions collect large amounts of information about student attendance, study habits, LMS engagement, internal assessments, and final grades. However, raw academic data can be difficult to interpret without an interactive analytical interface.

The **Student Performance Analytics Dashboard** transforms student academic data into an interactive application that allows users to:

* Monitor overall academic performance
* Identify students who may require additional academic attention
* Analyze relationships between attendance, study hours, LMS usage, internal marks, and final grades
* Filter students based on multiple criteria
* View individual student performance
* Explore performance patterns using interactive visualizations
* Access administrative features through role-based authorization

The application is deployed using **Streamlit Cloud** and includes application-level authentication and security controls.

---

## 🎯 Problem Statement

Academic performance depends on multiple factors such as attendance, study time, LMS engagement, and internal assessment marks.

Without an analytical dashboard, it can be difficult to:

* Identify students who may be at academic risk
* Understand performance patterns across students
* Compare different academic indicators
* Explore relationships between engagement and final grades
* Monitor individual student performance
* Convert raw academic records into understandable visual insights

This project addresses these challenges through an interactive dashboard.

---

## 🎯 Objectives

The main objectives of this project are:

* Analyze student academic performance using Python
* Explore relationships between academic variables
* Identify potentially at-risk students
* Provide interactive data visualizations
* Allow users to filter and explore student records
* Provide individual student drill-down analysis
* Display correlation between important academic factors
* Present key analytical observations
* Implement authentication and role-based authorization
* Deploy the application as a publicly accessible web application

---

## 📊 Dataset

The dashboard uses a student academic performance dataset containing academic and engagement-related information.

| Feature                 | Description                                     |
| ----------------------- | ----------------------------------------------- |
| `Student_ID`            | Unique identifier for each student              |
| `Gender`                | Student gender                                  |
| `Attendance_Percentage` | Percentage of classes attended                  |
| `Study_Hours_per_Week`  | Weekly study hours                              |
| `LMS_Hours`             | Time spent using the Learning Management System |
| `Internal_Marks`        | Internal assessment marks                       |
| `Final_Grade`           | Final academic grade                            |

---

## 🚦 Risk Classification

The application classifies students into three risk categories using **final grade and attendance**.

### 🔴 High Risk

A student is classified as **High Risk** when:

* Final Grade is below `50`, **or**
* Attendance is below `60%`

### 🟡 Medium Risk

A student is classified as **Medium Risk** when:

* Final Grade is below `65`, **or**
* Attendance is below `75%`

### 🟢 Low Risk

Students who do not meet the High Risk or Medium Risk conditions are classified as **Low Risk**.

This classification provides a simple early-warning mechanism for identifying students who may need additional attention.

---

# 📊 Dashboard Features

The application provides multiple analytical views.

## 🏠 1. Overview

The Overview page provides a high-level summary of the selected student population.

### Displays:

* Total number of students
* Number of high-risk students
* Average final grade
* Grade distribution by risk level

The page also provides interactive filtering so that users can analyze specific groups of students.

---

## 🚨 2. At-Risk Analysis

The At-Risk Analysis page focuses on students classified as:

* 🔴 High Risk
* 🟡 Medium Risk

The dashboard displays relevant information such as:

* Student ID
* Gender
* Attendance
* Study hours
* Final grade
* Risk level

This allows users to quickly identify students who may require additional academic attention.

---

## 🔍 3. Student Drill-Down

The Student Drill-Down page allows users to select an individual student and examine their performance.

For each selected student, the dashboard displays:

* Attendance percentage
* Study hours per week
* Final grade
* Risk level

This provides a simple individual-level view in addition to the overall analysis.

---

## 📈 4. Visual Analysis

The Visual Analysis page contains interactive Plotly visualizations.

### Attendance vs Final Grade

Shows the relationship between student attendance and final grade.

### Study Hours vs Final Grade

Shows the relationship between weekly study hours and final grade.

### Average Grade by Risk Level

Compares the average final grade across the different risk categories.

### Grade Distribution by Risk Level

Box plots are used to visualize the distribution and spread of grades within each risk category.

---

## 🔥 5. Performance Correlation Heatmap

The Performance Heatmap displays correlations between important numerical academic variables:

* Attendance
* Study Hours
* LMS Hours
* Internal Marks
* Final Grade

This helps users explore how different academic factors are related to one another.

---

## 🧠 6. Insights

The Insights page summarizes important observations from the dashboard.

Examples include:

* Attendance should not be considered as the only indicator of academic success
* Study time and LMS engagement provide additional context
* Medium-risk students can be important intervention targets
* Multiple academic indicators provide a broader understanding of student performance

The page also highlights early-warning indicators such as:

* Attendance below `75%`
* Final grades below `65`
* Low LMS engagement

---

# 🔎 Interactive Filtering

The dashboard provides multiple filters through the sidebar.

Users can filter the dataset by:

* Gender
* Risk Level
* Attendance range
* Final Grade range

All applicable dashboard views update based on the selected filters.

This allows users to interactively explore different segments of the student population.

---

# 🔐 Authentication & Security

The application includes application-level authentication and authorization.

### Security Features

* Username/password authentication
* Password hashing using **bcrypt**
* JWT-based authentication
* JWT token expiration
* Role-Based Access Control (RBAC)
* Server-side authorization checks
* Generic authentication error messages
* Externalized secrets using Streamlit Secrets
* Sensitive configuration excluded from version control

### Authentication Flow

```text
User
  │
  ▼
Login
  │
  ▼
Credential Verification
  │
  ▼
bcrypt Password Verification
  │
  ▼
JWT Access Token
  │
  ▼
Token Validation
  │
  ▼
Authenticated Dashboard
```

---

# 👥 User Roles

The application currently supports two roles.

| Role          | Dashboard     | Student Analytics | Admin Panel  |
| ------------- | ------------- | ----------------- | ------------ |
| Administrator | ✅ Full Access | ✅ Allowed         | ✅ Allowed    |
| Analyst       | ✅ Full Access | ✅ Allowed         | ❌ Restricted |

The Administration page performs a server-side role check and is accessible only to users with the `admin` role.

---

# 🖥️ Admin Panel

Administrators have access to an additional Administration page.

The Admin Panel displays:

* Authenticated username
* Current role
* Session status
* Authentication status
* Password hashing status
* JWT authentication status
* Role-based authorization status
* JWT session configuration
* Secret management status
* Application health
* Access-control information
* Session information
* Logout functionality

The Admin Panel is intended to demonstrate administrative access control within the application.

---

# 🛠️ Technology Stack

## Programming

* **Python**

## Data Processing

* **Pandas**

## Data Visualization

* **Plotly**

## Dashboard

* **Streamlit**

## Authentication & Security

* **bcrypt**
* **PyJWT**
* JWT authentication
* Role-Based Access Control (RBAC)
* Streamlit Secrets

## Development Tools

* **Git**
* **GitHub**
* **VS Code**

## Deployment

* **Streamlit Cloud**

---



### Important

Local Streamlit secrets should be stored separately:

```text
.streamlit/
└── secrets.toml
```

The `secrets.toml` file should **never be committed to GitHub**.

---

# 🚀 Running the Project Locally

## 1. Clone the repository

```bash
git clone https://github.com/kav-26/Student-Performance-Dashboard.git
```

## 2. Navigate to the project

```bash
cd Student-Performance-Dashboard
```

## 3. Create a virtual environment

```bash
python -m venv venv
```

## 4. Activate the virtual environment

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

## 5. Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Configure Streamlit Secrets

Create:

```text
.streamlit/secrets.toml
```

and add the required JWT and user authentication configuration.

Example structure:

```toml
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

[users.admin]
password_hash = "your-admin-bcrypt-hash"
role = "admin"

[users.analyst]
password_hash = "your-analyst-bcrypt-hash"
role = "analyst"
```

**Never commit `secrets.toml` to GitHub.**

## 7. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

---

# 🌐 Deployment

The application is deployed using **Streamlit Cloud**.

### Live Application

🔗 https://kav-26-student-performance-dashboard-app-ghfwnu.streamlit.app/

The deployment uses Streamlit Secrets for sensitive configuration such as:

* JWT secret key
* User password hashes
* Authentication configuration

Sensitive credentials are therefore kept outside the public GitHub repository.

---

# 🔒 Security Considerations

This project demonstrates application-level security practices and is intended as an educational and portfolio project rather than a production-grade authentication system.

Implemented controls include:

* Password hashing rather than plaintext password storage
* JWT signature verification
* JWT expiration
* Role-based authorization
* Externalized secrets
* Generic authentication error messages
* Sensitive configuration excluded from version control

For a production application, additional security measures would be appropriate, including:

* HTTPS enforcement
* Secure session and cookie management
* Centralized identity management
* Rate limiting
* Audit logging
* CSRF protection where applicable
* Production-grade database and user management
* More comprehensive monitoring and security testing

---

# 💡 Key Insights

The dashboard is designed to help identify patterns such as:

* Students with lower attendance may require closer monitoring.
* Study time and LMS engagement can provide additional context when evaluating academic performance.
* Final grades can vary considerably within the same risk category.
* Medium-risk students can serve as an important early-intervention group.
* Combining multiple academic indicators provides a broader view of student performance.

These observations should be interpreted in the context of the available dataset rather than treated as universal conclusions.

---


# 🔮 Future Enhancements

Possible future improvements include:

* Database integration instead of CSV-based storage
* Advanced student search
* Downloadable analytical reports
* Additional performance KPIs
* Historical performance tracking
* More advanced statistical analysis
* Predictive performance modeling
* Automated notifications for high-risk students
* More granular administrative controls
* Audit logging
* Improved session management
* Cloud database integration
* More comprehensive automated testing

---

# 📌 Skills Demonstrated

This project demonstrates practical experience with:

* Python
* Pandas
* Data analysis
* Data filtering and transformation
* Data visualization
* Interactive dashboards
* Plotly
* Streamlit
* Risk classification
* Correlation analysis
* Application authentication
* JWT
* bcrypt
* Role-Based Access Control
* Secrets management
* Git
* GitHub
* Cloud deployment

---

# 📄 Conclusion

The **Student Performance Analytics Dashboard** demonstrates how raw academic data can be transformed into an interactive application for exploring student performance and identifying potential academic risks.

The project combines **data processing, interactive visualization, risk classification, dashboard development, authentication, authorization, and cloud deployment** into a single application.

By deploying the dashboard through Streamlit Cloud, the project is accessible as a live web application while sensitive authentication configuration remains separated from the public source code.

---

## 👩‍💻 Author

**Anjani Kavya**

GitHub: https://github.com/kav-26


