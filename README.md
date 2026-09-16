ExamGuard – Smart Examination Monitoring Platform

Project Overview
ExamGuard is a Python-based online examination monitoring platform designed to assist invigilators in monitoring important examination activities and analyzing examination integrity.
The platform brings monitoring, event capture, analysis, evidence management, and reporting together in a single system. It records relevant examination activities, calculates an integrity score based on recorded violations, analyzes activity patterns, manages examination incidents, and generates AI-based integrity reports.

Objectives
* Monitor student presence during online examinations.
* Record browser-related examination activities.
* Identify and record integrity-related events.
* Calculate an integrity score based on recorded violations.
* Manage and review examination incidents and supporting evidence.
* Analyze examination activity patterns using Data Science techniques.
* Generate natural-language integrity reports using an AI-based reporting module.
* Provide dashboards and visual analytics for easier examination review.

Key Features
1. Face Presence Monitoring
The system uses the webcam and OpenCV-based face detection to monitor whether the student's face is present during the examination.
It records relevant face-presence events and identifies periods when the student's face is not detected.

2. Browser Activity Monitoring
ExamGuard records selected browser-related activities during an examination, including:
* Tab switching
* Right-click activity
* Copy/Paste activity
* Developer Tools activity
* View Source activity
These events are recorded and used as part of the examination integrity analysis.

3. Integrity Score
The system calculates an integrity score based on recorded browser-related violations and their assigned penalty values.
The score provides a summarized view of the recorded examination activity and helps invigilators identify sessions that require further review.

4. Evidence & Incident Management
ExamGuard includes an incident management module for recording and reviewing integrity-related incidents during an examination session.
Incidents can be tracked using different statuses:
* Pending
* Reviewed
* Dismissed
Relevant evidence can be associated with incidents and stored for later review. This allows invigilators to organize examination events and review supporting evidence along with the session's integrity analysis.
The incident management system is designed to support human review rather than automatically make disciplinary decisions.

5. Data Science Analytics
ExamGuard analyzes examination session data using K-Means clustering to identify different patterns of examination activity.
The analytics module considers features such as:
* Integrity score
* Browser activity counts
* Face-related activity
* Face presence ratio
* Total recorded events
The resulting clusters are used to categorize different activity patterns for easier examination review.

6. AI-Based Integrity Reports
ExamGuard includes an AI-based reporting module that converts analyzed examination data into a natural-language integrity report.
The AI reporting component summarizes important examination events and analytical results to help invigilators understand the recorded activity without manually reviewing every individual event.

7. Dashboard and Reporting
The platform provides analytical views for reviewing examination sessions.
The dashboard can present information such as:
* Integrity score
* Recorded violations
* Activity timeline
* Risk categories
* Examination activity patterns
* K-Means cluster results
* AI-generated integrity summaries
The system also supports exporting relevant examination analysis and reporting data for further review.

Technology Stack
* Programming Language: Python
* Web Framework: Flask
* Database: SQLite
* Computer Vision: OpenCV
* Data Analysis: Pandas
* Machine Learning: Scikit-learn
* Clustering: K-Means
* AI Reporting: LangChain
* Dashboard & Visualization: Streamlit
* Frontend: HTML, CSS, JavaScript

System Workflow
Student starts examination
          ↓
Face presence monitoring
          ↓
Browser activity monitoring
          ↓
Event recording
          ↓
Incident & evidence management
          ↓
Integrity score calculation
          ↓
Data Science analysis
          ↓
K-Means activity clustering
          ↓
AI-based report generation
          ↓
Dashboard & examination review


Project Scope
ExamGuard is designed as an assistive examination monitoring system. It provides recorded examination events, supporting evidence, integrity scores, analytical information, and AI-generated summaries to assist invigilators during examination review. The system is intended to support human decision-making rather than automatically make disciplinary decisions.

Future Improvements
* Improved face verification and recognition.
* Advanced suspicious activity detection.
* Real-time notification mechanisms.
* More detailed examination analytics.
* Improved AI-generated reporting.
* Cloud-based deployment.
* Enhanced scalability for multiple simultaneous examinations.
* Advanced evidence visualization and management.



