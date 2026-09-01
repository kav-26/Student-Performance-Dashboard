# 🎓 Student Performance Analytics Dashboard

An interactive **Data Analytics and Predictive Modeling dashboard** built with Python and Streamlit to analyze student academic performance, identify risk patterns, visualize relationships between academic factors, and support data-driven decision-making.

---

## 📌 Project Overview

Educational institutions generate large amounts of student academic and engagement data. However, raw data alone does not provide an easy way to identify performance patterns, detect students who may require intervention, or understand the factors associated with academic outcomes.

This project transforms student performance data into meaningful insights using:

* Exploratory Data Analysis (EDA)
* Descriptive and statistical analysis
* Correlation analysis
* Data preprocessing
* Data visualization
* Predictive modeling using Linear Regression
* Interactive Streamlit dashboard
* Risk classification
* Role-based authentication and authorization

The dashboard enables users to explore student performance interactively and identify important relationships between attendance, study time, LMS engagement, internal marks, and final grades.

---

## 🎯 Problem Statement

Educational institutions often have large datasets containing attendance, study hours, LMS engagement, internal marks, and final grades.

Without effective analytical tools, it can be difficult to:

* Identify students at academic risk
* Understand factors affecting final grades
* Detect relationships between engagement and performance
* Compare performance across different student groups
* Convert raw academic data into actionable insights

This project addresses these challenges through an interactive analytics and visualization platform.

---

## 🎯 Objectives

* Analyze student academic performance using Python
* Perform Exploratory Data Analysis (EDA)
* Identify relationships between academic and engagement variables
* Analyze correlations between student engagement and final grades
* Detect potential at-risk students
* Visualize performance patterns using interactive charts
* Apply statistical techniques to understand the dataset
* Build a predictive model using Linear Regression
* Create an interactive Streamlit dashboard
* Implement secure authentication and role-based authorization

---

## 📊 Dataset

The dataset contains student academic and engagement-related attributes, including:

| Feature               | Description                                     |
| --------------------- | ----------------------------------------------- |
| Student_ID            | Unique identifier for each student              |
| Gender                | Student gender                                  |
| Attendance_Percentage | Percentage of classes attended                  |
| Study_Hours_per_Week  | Weekly study hours                              |
| LMS_Hours             | Time spent using the Learning Management System |
| Internal_Marks        | Internal assessment marks                       |
| Final_Grade           | Final academic grade                            |

---

## 🔍 Exploratory Data Analysis

Exploratory Data Analysis was performed to understand the structure, distribution, and relationships within the dataset.

### EDA includes:

* Dataset structure and data types
* Missing-value analysis
* Duplicate detection
* Descriptive statistics
* Distribution analysis
* Outlier detection
* Univariate analysis
* Bivariate analysis
* Correlation analysis
* Feature relationships
* Performance comparison across risk levels

### Statistical Analysis

Key statistical techniques include:

* Mean
* Median
* Standard deviation
* Minimum and maximum values
* Quartiles
* Interquartile Range (IQR)
* Correlation analysis

These techniques help identify trends, variation, and relationships within the student performance data.

---

## 🧹 Data Preprocessing

The following preprocessing techniques were used as part of the analysis:

* Detection and removal of duplicate records
* Handling missing values
* Outlier detection using the IQR method
* Feature transformation and normalization where required
* Feature engineering
* Creation of an Engagement Score
* Preparation of numerical variables for modeling

---

## 📈 Data Visualization

Multiple visualization techniques were used to communicate analytical findings effectively.

### Visualization libraries

* **Matplotlib**
* **Seaborn**
* **Plotly**

### Visualizations include:

* Histograms
* Scatter plots
* Box plots
* Bar charts
* Correlation heatmaps
* Performance distributions
* Risk-level comparisons

These visualizations help identify patterns that may not be immediately visible from raw numerical data.

---

## 🤖 Predictive Modeling

### Linear Regression

Linear Regression was used as a predictive modeling technique to analyze the relationship between academic/engagement factors and student final grades.

The modeling workflow includes:

1. Data preparation
2. Feature selection
3. Train-test split
4. Model training
5. Prediction
6. Model evaluation
7. Interpretation of relationships between variables

The model helps demonstrate how academic and engagement-related factors can be used to estimate student performance.

---

## 🚦 Student Risk Classification

Students are categorized into three risk levels based on academic performance and attendance:

### 🔴 High Risk

Students with:

* Final Grade below 50, **or**
* Attendance below 60%

### 🟡 Medium Risk

Students with:

* Final Grade below 65, **or**
* Attendance below 75%

### 🟢 Low Risk

Students who do not fall into the High or Medium Risk categories.

This classification helps highlight students who may require additional academic attention.

---

## 📊 Dashboard Features

The Streamlit dashboard provides several interactive analytical views.

### 🏠 Overview

Provides a high-level summary of:

* Total students
* High-risk students
* Average grade
* Grade distribution by risk level

### 🚨 At-Risk Analysis

Displays students identified as:

* High Risk
* Medium Risk

along with relevant academic and engagement indicators.

### 🔍 Student Drill-Down

Allows users to select an individual student and view:

* Attendance
* Study hours
* Final grade
* Risk level

### 📈 Visual Analysis

Provides interactive visualizations including:

* Attendance vs Final Grade
* Study Hours vs Final Grade
* Average Grade by Risk Level
* Grade distribution using Box Plots

### 🔥 Performance Heatmap

Displays correlations between:

* Attendance
* Study Hours
* LMS Hours
* Internal Marks
* Final Grade

### 🧠 Insights

Summarizes important findings and early-warning indicators from the analysis.

---

## 🔐 Authentication & Security

The dashboard also implements basic application-level security controls.

### Security Features

* Username/password authentication
* Password hashing using **bcrypt**
* JWT-based authentication
* JWT token expiration
* Role-based access control (RBAC)
* Server-side authorization checks
* Generic authentication error messages
* Externalized security secrets using Streamlit Secrets
* Sensitive configuration excluded from version control

### User Roles

| Role          | Dashboard     | Student Analytics | Admin Panel |
| ------------- | ------------- | ----------------- | ----------- |
| Administrator | ✅ Full Access | ✅                 | ✅           |
| Analyst       | ✅ Full Access | ✅                 | ❌           |

The Administration page is protected using server-side role validation, so only users with the `admin` role can access it.

### Security Configuration

JWT tokens are configured with a limited lifetime to reduce the risk associated with long-lived sessions.

Sensitive credentials and JWT secrets are stored outside the source code using Streamlit Secrets and are not committed to the public repository.

---

## 🖥️ Admin Panel

The administrator panel provides system and access information, including:

* Current authenticated user
* User role
* Session status
* Authentication status
* bcrypt password hashing status
* JWT authentication status
* Role-based authorization status
* JWT expiration configuration
* Secret management status
* Application health
* Access-control overview
* Session information
* Logout functionality

---

## 🛠️ Technologies Used

### Programming & Data Analysis

* **Python**
* **Pandas**
* **NumPy**

### Data Visualization

* **Matplotlib**
* **Seaborn**
* **Plotly**

### Statistical & Machine Learning

* **Scikit-learn**
* Linear Regression
* MinMaxScaler
* Statistical analysis
* Correlation analysis
* IQR-based outlier detection

### Dashboard

* **Streamlit**

### Security

* **bcrypt**
* **PyJWT**
* JWT authentication
* Role-Based Access Control (RBAC)
* Streamlit Secrets

### Development Tools

* Git
* GitHub
* VS Code



## 💡 Key Insights

The analysis highlights several patterns in student performance:

* Attendance is an important indicator of academic performance, but it should not be considered in isolation.
* Study time and LMS engagement can provide additional context when evaluating student performance.
* Correlation analysis helps identify relationships between engagement factors and final grades.
* Students in the medium-risk category can represent important intervention targets.
* Combining multiple academic indicators provides a better understanding of student performance than relying on a single metric.

---

## 🚀 Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/kav-26/Student-Performance-Dashboard.git
```

### 2. Navigate to the project directory

```bash
cd Student-Performance-Dashboard
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install streamlit pandas numpy plotly matplotlib seaborn scikit-learn bcrypt PyJWT
```

### 6. Configure Streamlit Secrets

Create:

```text
.streamlit/secrets.toml
```

and configure the required JWT and user authentication settings.

**Do not commit this file to GitHub.**

### 7. Run the dashboard

```bash
python -m streamlit run app.py
```

The dashboard will then be available locally through Streamlit.

---

## 🔒 Security Considerations

This project implements application-level security controls, but it is intended as an educational and portfolio project rather than a production-grade authentication system.

Security measures include:

* Password hashing instead of plaintext password storage
* JWT signature verification
* JWT expiration
* Role-based authorization
* Externalized secrets
* Generic login error messages
* Sensitive configuration excluded from Git

For production deployment, additional controls such as HTTPS, secure cookie/session management, centralized identity management, rate limiting, audit logging, CSRF protection where applicable, and a production database would be appropriate.

---

## 🎯 Skills Demonstrated

This project demonstrates practical experience in:

* Python programming
* Data cleaning
* Data preprocessing
* Exploratory Data Analysis (EDA)
* Descriptive statistics
* Statistical analysis
* Outlier detection
* Feature engineering
* Correlation analysis
* Data visualization
* Matplotlib
* Seaborn
* Plotly
* NumPy
* Pandas
* Linear Regression
* Machine Learning fundamentals
* Interactive dashboard development
* Streamlit
* Authentication
* JWT
* bcrypt
* Role-Based Access Control
* Git and GitHub

---

## 📌 Conclusion

The Student Performance Analytics Dashboard demonstrates how Python-based data analytics and visualization can transform raw academic data into actionable insights.

By combining **EDA, statistical analysis, correlation analysis, predictive modeling, interactive visualization, and risk classification**, the project provides a comprehensive approach to understanding student performance.

The addition of **JWT authentication, bcrypt password hashing, and role-based authorization** also demonstrates an understanding of securing analytical applications beyond the data-analysis layer.

