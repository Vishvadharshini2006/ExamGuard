# ExamGuard – Smart Examination Monitoring Platform

## Overview

ExamGuard is a Python-based online examination monitoring platform designed to assist invigilators in monitoring and reviewing student examination sessions.

During an online examination, it can be difficult for an invigilator to continuously monitor every student and identify all relevant activities manually. ExamGuard addresses this by bringing monitoring, event capture, analysis, evidence management, and reporting together in a single platform.

The system monitors face presence through the webcam, records selected browser activities, calculates an integrity score based on recorded violations, analyzes examination activity patterns, manages incidents and evidence, and generates AI-based examination reports.

**Note:** ExamGuard is an assistive monitoring system. The recorded information and analytical results are intended to support human review and do not automatically determine disciplinary action.

## Objectives

* Monitor student face presence during online examinations.
* Capture selected browser-related activities.
* Record integrity-related examination events.
* Calculate an integrity score based on recorded violations.
* Manage incidents and supporting evidence.
* Analyze examination activity patterns using Data Science techniques.
* Generate AI-based integrity reports.
* Provide dashboards and visual analytics for examination review.
* Export relevant examination analysis and reporting data.

## Features

### 1. Face Presence Monitoring

ExamGuard uses the student's webcam and OpenCV-based face detection to monitor face presence during an examination.

The system records relevant face-presence events and identifies periods when the student's face is not detected.

### 2. Browser Activity Monitoring

ExamGuard records selected browser-related activities that occur during an examination.

The monitored activities include:

* Tab switching
* Right-click activity
* Copy/Paste activity
* Developer Tools activity
* View Source activity

These events are recorded and used during the examination integrity analysis.

### 3. Integrity Score

ExamGuard calculates an integrity score based on recorded browser-related violations and their corresponding penalty values.

The score provides a summarized representation of the recorded examination activity and can help invigilators identify sessions that require further review.

### 4. Evidence and Incident Management

The platform includes an Evidence and Incident Management module for organizing integrity-related incidents.

Incidents can be tracked using different statuses:

* Pending
* Reviewed
* Dismissed

Supporting evidence can be associated with incidents and stored for later review.

This allows an invigilator to review the recorded event, its supporting evidence, and the examination session information together.

### 5. Data Science Analytics

ExamGuard uses K-Means clustering to analyze examination session data and identify different patterns of examination activity.

The analysis considers features such as:

* Integrity score
* Browser activity counts
* Face-related activity
* Face presence ratio
* Total recorded events

The resulting clusters help organize different examination activity patterns for analysis.

### 6. AI-Based Integrity Reports

ExamGuard includes an AI-based reporting module that converts examination and analytical information into a natural-language integrity report.

The generated report summarizes important examination events and analysis results, making the information easier for an invigilator to review.

### 7. Dashboard and Reporting

A Streamlit-based dashboard provides analytical views of examination sessions.

The dashboard can display:

* Integrity scores
* Recorded violations
* Activity patterns
* Risk categories
* K-Means cluster results
* AI-generated summaries

The system also supports exporting relevant examination data and analysis results.

## Technology Stack

| Technology            | Purpose                                  |
| --------------------- | ---------------------------------------- |
| Python                | Core programming language                |
| Flask                 | Web application and examination platform |
| SQLite                | Database                                 |
| OpenCV                | Face detection and monitoring            |
| Pandas                | Data processing and analysis             |
| Scikit-learn          | Machine learning and clustering          |
| K-Means               | Examination activity pattern analysis    |
| LangChain             | AI-based reporting workflow              |
| Streamlit             | Analytics dashboard                      |
| HTML, CSS, JavaScript | Web interface                            |

## Project Structure

```text
ExamGuard/
│
├── app.py
├── config.py
├── database.py
├── check_db.py
├── test_export.py
├── streamlit_app.py
├── requirements.txt
├── LICENSE
├── README.md
│
├── modules/
│   ├── face_monitor.py
│   ├── analytics.py
│   ├── ai_report.py
│   └── incident_manager.py
│
├── haarcascade/
│
├── static/
│
├── templates/
│
├── exports/
│
└── docs/
    ├── Project-Documentation.md
    └── Agile-Documentation.md
```

## Important Files

* `app.py` – Main Flask application.
* `config.py` – Application configuration.
* `database.py` – SQLite database operations.
* `streamlit_app.py` – Streamlit analytics dashboard.
* `modules/face_monitor.py` – Face monitoring functionality.
* `modules/analytics.py` – Examination analytics and K-Means clustering.
* `modules/ai_report.py` – AI-based integrity report generation.
* `modules/incident_manager.py` – Incident and evidence management.
* `requirements.txt` – Python dependencies.

## Documentation

Detailed project documentation is available in the `docs` directory.

* [Project Documentation](docs/Project-Documentation.md)
* [Agile Documentation](docs/Agile-Documentation.md)

## Installation

Follow the steps below to run ExamGuard locally.

### Prerequisites

Before installing ExamGuard, make sure the following are installed:

* Python 3.x
* Git
* A modern web browser
* Webcam access for face monitoring

### 1. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/Vishvadharshini2006/ExamGuard.git
```

Move into the project directory:

```bash
cd ExamGuard
```

### 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

#### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
venv\Scripts\activate
```

After activation, the terminal should display:

```text
(venv)
```

### 4. Install Dependencies

Install all required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Configuration

If the AI reporting functionality requires an API key, configure the required environment variables according to the application's configuration.

Create a `.env` file in the project root if required by the application.

Example:

```text
YOUR_API_KEY=your_api_key_here
```

Do not commit API keys or other secrets to GitHub.

The `.env` file should remain local and should be excluded through `.gitignore`.

## Running the Application

### Start the Flask Application

Make sure the virtual environment is activated.

Run:

```bash
python app.py
```

The Flask application will start locally.

Open the URL displayed in the terminal.

Typically:

```text
http://127.0.0.1:5000
```

### Start the Streamlit Dashboard

Open a second terminal in the project directory.

Activate the virtual environment and run:

```bash
streamlit run streamlit_app.py
```

Streamlit will provide a local URL.

Typically:

```text
http://localhost:8501
```

Open this URL in a browser to access the analytics dashboard.

## How ExamGuard Works

1. A student starts an online examination.
2. The system monitors face presence through the webcam.
3. Selected browser activities are captured during the examination.
4. Recorded events are stored in the database.
5. Integrity-related incidents and supporting evidence can be managed and reviewed.
6. Browser-related violations contribute to the integrity score.
7. Examination data is analyzed using Data Science techniques.
8. K-Means clustering identifies examination activity patterns.
9. The AI reporting module generates a natural-language examination report.
10. The dashboard presents the analysis and reports for invigilator review.

## Integrity Score

ExamGuard uses penalty values for selected browser-related activities.

The current penalty values are:

| Activity        | Penalty |
| --------------- | ------: |
| Tab Switching   |       5 |
| Right Click     |       2 |
| Copy/Paste      |       3 |
| F12             |       5 |
| Developer Tools |      10 |
| View Source     |       5 |

The recorded penalties are used to calculate the examination integrity score.

## Data Science Analysis

ExamGuard uses K-Means clustering to group examination sessions based on recorded activity patterns.

The clustering process considers features such as:

* Integrity score
* Total recorded events
* Browser activity counts
* Face-related activity
* Face presence ratio

The analysis helps organize examination sessions into different activity patterns for further review.

## Evidence and Incident Management

ExamGuard provides an incident management workflow for recorded examination events.

Each incident can be assigned one of the following statuses:

* Pending
* Reviewed
* Dismissed

Supporting evidence can be associated with an incident and stored for later examination.

This provides a structured way to review examination events and their supporting information.

## Data and Privacy

ExamGuard processes examination-related information such as:

* Face monitoring events
* Browser activity events
* Integrity scores
* Incident information
* Supporting evidence
* Examination analytics
* Generated reports

Sensitive configuration information such as API keys should not be stored in the GitHub repository.

ExamGuard is designed as an assistive monitoring platform. Final examination decisions should remain under appropriate human review.

## Project Scope

ExamGuard focuses on providing an integrated platform for online examination monitoring, event recording, analysis, incident management, and reporting.

The current implementation demonstrates:

* Online examination functionality
* Face presence monitoring
* Browser activity monitoring
* Integrity score calculation
* Incident and evidence management
* Data Science-based activity analysis
* K-Means clustering
* AI-based reporting
* Streamlit analytics dashboard
* Examination data export

## Future Improvements

Potential future improvements include:

* Advanced face recognition and identity verification
* Improved browser activity monitoring
* Real-time notification mechanisms
* More advanced anomaly detection
* Additional machine learning models
* Improved dashboard visualizations
* Cloud-based deployment
* Scalable multi-user examination management
* Enhanced evidence storage and management

## Project Status

ExamGuard is an academic project developed as a Smart Examination Monitoring Platform with Integrity Analysis and Reporting capabilities.

The current implementation integrates examination monitoring, event capture, integrity analysis, incident management, Data Science analytics, AI-based reporting, and dashboard visualization into a single platform.

## Authors

* Vishva Dharshini R.
* B.Tech Artificial Intelligence and Data Science
* Panimalar Engineering College

## License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
