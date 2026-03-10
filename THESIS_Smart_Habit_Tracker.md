# SMART HABIT TRACKER WITH BEHAVIORAL ANALYTICS AND ML PREDICTIONS

## A Project Report

Submitted in partial fulfillment of the requirements for the award of the degree of  
`<Degree Name>`  
in  
`<Department Name>`

By  
`<Student Name>`  
`<Roll Number>`

Under the Supervision of  
`<Guide Name>`  
`<Designation>`

`<Department Name>`  
`<Institution Name>`  
`<City, State, Country>`  
`<Academic Year>`

---

## DECLARATION

I hereby declare that the project report entitled **"Smart Habit Tracker with Behavioral Analytics and ML Predictions"** is my original work carried out under the guidance of `<Guide Name>`. This report is submitted in partial fulfillment of the requirements for the award of `<Degree Name>`.

The work presented in this report has not been submitted, either in part or full, to any other university or institution for the award of any degree or diploma.

**Signature of Student:** ____________________  
**Name:** `<Student Name>`  
**Roll Number:** `<Roll Number>`  
**Date:** `<DD-MM-YYYY>`

---

## CERTIFICATE

This is to certify that the project report entitled **"Smart Habit Tracker with Behavioral Analytics and ML Predictions"** submitted by `<Student Name>` (`<Roll Number>`) is a bonafide record of work carried out under my supervision and guidance, in partial fulfillment of the requirements for the award of `<Degree Name>`.

**Guide Signature:** ____________________  
**Guide Name:** `<Guide Name>`  
**Designation:** `<Designation>`  
**Department:** `<Department Name>`

**Head of Department Signature:** ____________________  
**HOD Name:** `<HOD Name>`

---

## ACKNOWLEDGEMENT

I express my sincere gratitude to my project guide, `<Guide Name>`, for valuable guidance, continuous support, and constructive suggestions throughout this project.

I also thank the Head of the Department, faculty members, and my institution for providing the required infrastructure and encouragement. I extend my gratitude to my peers, friends, and family for their support during the completion of this project.

---

## ABSTRACT

The **Smart Habit Tracker with Behavioral Analytics and ML Predictions** is a web-based system designed to help users build consistency in daily routines through structured tracking, predictive insights, and engagement features. The application supports user authentication, habit creation, daily logging, streak analytics, reminders, social leaderboard, and progress reporting.

The system combines rule-based logic with machine learning models to estimate habit completion probability and provide actionable recommendations. It also includes a scheduler-driven notification module for time-sensitive reminders and a gamification layer using XP and achievements to improve motivation.

The project is implemented using **Flask**, **SQLAlchemy**, **Flask-Login**, **Flask-Mail**, **APScheduler**, and **scikit-learn** components integrated through model artifacts. The result is a practical and extensible productivity platform suitable for students, professionals, and personal wellness use-cases.

**Keywords:** Habit Tracking, Behavioral Analytics, Machine Learning, Flask, Predictive Modeling, Gamification

---

## TABLE OF CONTENTS

1. Introduction  
2. Problem Statement  
3. Requirement Analysis  
4. Software Design  
5. Implementation  
6. Testing  
7. Algorithms  
8. Code Structure  
9. Test Cases  
10. Input and Output Screens  
11. Conclusion  
12. Literature Review  
13. References

---

# CHAPTER 1: INTRODUCTION

## 1.1 Project Scope

The project provides a complete habit lifecycle system:
- User registration and authentication
- Habit creation and management
- Daily completion/miss tracking
- Streak and consistency analytics
- ML-based completion/failure risk estimation
- Rule-based suggestions and next-action recommendations
- Email reminders for time-window habits
- Gamification through XP, achievements, and leaderboard
- Exportable PDF-style reports (daily/weekly/monthly)

## 1.2 Existing System

Traditional habit trackers generally focus on simple checklist logging with limited personalization. Many systems lack:
- Predictive insights
- Intelligent suggestions
- Time-window reminders
- Engagement mechanisms such as social competition and rewards

## 1.3 Proposed System

The proposed system integrates analytics and machine learning into routine tracking. It not only stores completion logs but also interprets behavioral patterns to support decision-making through:
- completion probability prediction
- risk heuristics fallback
- smart next-action recommendation
- session mode with reflection

## 1.4 Feasibility Study

### 1.4.1 Technical Feasibility
- Built on Python Flask stack with modular blueprints.
- Uses relational DB (SQLite/MySQL compatible via SQLAlchemy).
- ML model training and prediction are implemented with scalable artifacts (`.pkl`).

### 1.4.2 Economic Feasibility
- Uses open-source technologies.
- Minimal infrastructure cost for deployment.
- Suitable for institutional/student projects with low budget.

### 1.4.3 Operational Feasibility
- Simple web UI for non-technical users.
- Supports practical daily use with reminders and progress visibility.
- Easy maintenance due to modular backend architecture.

## 1.5 Software Requirement Specification (Summary)

The SRS covers:
- functional requirements (FR1–FR21)
- non-functional requirements (performance, security, usability, reliability)
- external interfaces (UI, DB, email SMTP)
- system models and module-level requirements

## 1.6 System Features

### Functional Features
- Secure signup/login and session management
- Habit CRUD and logging
- Dashboard analytics (streak, completion trends)
- Prediction engine (logistic regression + heuristic fallback)
- Suggestion and decision modules
- Notification scheduling for habit windows
- Gamification and leaderboard

### Non-Functional Features
- Secure password hashing
- Responsive UI
- Modular and maintainable codebase
- Graceful handling of missing data

## 1.7 External Interface Requirements

### User Interface
- HTML/CSS + templates under `templates/`
- Dashboard, profile, admin, social and session pages

### Hardware Interface
- Any standard desktop/mobile browser environment

### Software Interface
- SQL database (SQLite/MySQL)
- ML model files in `models/`
- SMTP integration for reminders

## 1.8 Future Scope

- Mobile-first app packaging
- Personalized coaching with reinforcement learning
- Improved anomaly detection for habit breaks
- Calendar integrations
- NLP-based contextual suggestion engine

---

# CHAPTER 2: PROBLEM STATEMENT

People struggle to maintain long-term habits due to inconsistent motivation, lack of timely prompts, and absence of data-driven feedback. Basic trackers record outcomes but do not proactively guide users.

This project addresses that gap by building a system that:
- predicts completion likelihood
- identifies risky habit patterns
- suggests practical next actions
- improves engagement with social and gamified elements

Goal: **Increase user consistency and sustained habit adherence using analytics and intelligent intervention.**

---

# CHAPTER 3: REQUIREMENT ANALYSIS

## 3.1 Functional Requirements (Condensed)

- FR1-FR5: Registration, login, session management
- FR6-FR9: Habit creation and daily logs
- FR10-FR12: Dashboard analytics and streak metrics
- FR13-FR14: ML prediction and risk categories
- FR15-FR16: Rule-based suggestions
- FR17-FR19: Time-based reminders and missed notifications
- FR20-FR21: Leaderboard and XP rewards

## 3.2 Non-Functional Requirements

- Performance: near-real-time dashboard and prediction retrieval
- Security: hashed passwords, controlled route access
- Usability: intuitive web interface
- Reliability: handles incomplete logs and sparse data with heuristic fallback

## 3.3 Hardware and Software Requirements

### Hardware
- Processor: i3/Ryzen equivalent or above
- RAM: 4 GB minimum (8 GB recommended)
- Storage: 1 GB free project runtime space

### Software
- Python 3.x
- Flask ecosystem (`flask`, `flask-sqlalchemy`, `flask-login`, `Flask-Mail`)
- `APScheduler`
- ML/data stack (`scikit-learn`, `pandas`, `numpy`, `joblib`)

---

# CHAPTER 4: SOFTWARE DESIGN

## 4.1 Architecture

The system follows a layered architecture:
- Presentation Layer: Jinja templates + static assets
- Application Layer: Flask blueprints (`auth`, `dashboard`, `habits`, `api`, `profile`, `social`, `admin`)
- Business Logic Layer: prediction, decision engine, smart coach, gamification
- Data Layer: SQLAlchemy models (`User`, `Habit`, `HabitLog`, etc.)
- Scheduler Layer: APScheduler jobs for reminder workflows

## 4.2 Use Case Overview

Primary actors:
- End User
- Admin

Primary use cases:
- Register/Login
- Add/Edit Habit
- Mark Completion
- View Dashboard Analytics
- Start Session Mode
- Receive Reminder Notifications
- View Leaderboard and Achievements

## 4.3 Class Design (Key Entities)

- `User`: identity, credentials, XP, streak metadata
- `Habit`: habit definition, frequency, time-window, style attributes
- `HabitLog`: daily completion status + completion type + XP
- `Achievement` / `UserAchievement`: milestone rewards
- `Suggestion`: adaptive advisory messages
- `Friendship`: social connections and status
- `WeeklyReport`: summary analytics and insights
- `Session`: focused execution block with reflection outcome

## 4.4 Sequence Summary

`Login -> Dashboard -> Habit Log -> Analytics Update -> Prediction -> Suggestion/Next Action -> Notification Cycle`

## 4.5 Activity Summary

Create habit -> daily check-in -> streak changes -> XP updates -> model retraining/usage -> decision guidance -> weekly reporting.

## 4.6 Deployment Model

- Flask app server
- SQL database file/server
- Mail service (SMTP)
- model artifact storage (`models/*.pkl`)

## 4.7 Component Overview

- Auth component
- Habit management component
- Analytics component
- ML component
- Scheduler/notification component
- Reporting component
- Social/gamification component

## 4.8 ER Mapping Summary

1. `User` 1:N `Habit`  
2. `Habit` 1:N `HabitLog`  
3. `User` N:N `Achievement` via `UserAchievement`  
4. `User` 1:N `Suggestion`  
5. `User` social links via `Friendship`  
6. `User` 1:N `WeeklyReport`  
7. `User` 1:N `Session`, `Habit` 1:N `Session`

---

# CHAPTER 5: IMPLEMENTATION

## 5.1 Technology Stack

- Backend: Python Flask
- ORM: SQLAlchemy
- Authentication: Flask-Login + Werkzeug hashing
- Scheduler: APScheduler
- Notification: Flask-Mail
- ML: scikit-learn Logistic Regression + StandardScaler
- Frontend: HTML/CSS/JS (template-based)

## 5.2 Module-wise Implementation

### Authentication Module
- Implements register/login/logout
- Passwords stored as hashes using secure Werkzeug methods

### Habit Module
- CRUD operations for habits
- Support for daily/weekly frequency and optional time windows

### Logging and Analytics
- Daily completion logs with completion type (`completed`, `late`, `recovered`, `partial`)
- Streak calculations and consistency metrics

### ML Prediction Module
- User-specific model training using historical habit logs
- Features include cyclical hour encoding, weekday flags, streak length, previous-day completion, and habit difficulty
- Fallback heuristic when model data is insufficient

### Decision Engine
- Identifies active habits in current time window
- Computes priority using predicted probability + streak factor
- Returns actionable recommendation (`Start Session` or fallback action)

### Notification and Scheduler Module
- Starts scheduler at application bootstrap
- Sends reminder/missed notifications based on habit windows

### Gamification and Social Module
- XP and streak-based leaderboard
- Friendship system and achievement tracking

## 5.3 Project Structure

`app.py` initializes application, config, plugins, blueprints, and scheduler.  
`models.py` defines data schema and helper methods.  
`ml_logic.py` contains model training and prediction logic.  
`decision_engine.py` computes next best action.  
`blueprints/` separates route responsibilities.  
`templates/` and `static/` provide UI.

---

# CHAPTER 6: TESTING

## 6.1 Testing Objectives

- Validate correctness of each module
- Ensure secure authentication and protected actions
- Verify prediction and fallback behavior
- Validate reminder flow and data persistence

## 6.2 Testing Levels

- Unit-level validation for logic methods
- Integration testing for route-DB interactions
- System testing for end-to-end workflows
- Manual UI testing across primary screens

## 6.3 Sample Testing Results

- User registration/login flow: Passed
- Habit create/update/delete: Passed
- Daily log uniqueness per habit/date: Passed (constraint enforced)
- Prediction without model file: Passed (heuristic fallback)
- Active-window next action: Passed
- Leaderboard update after XP changes: Passed

---

# CHAPTER 7: ALGORITHMS

## 7.1 Streak Calculation Algorithm

1. Fetch successful logs ordered by date descending.  
2. If last log is older than yesterday, streak = 0.  
3. Traverse backward date-by-date while logs are contiguous and successful.  
4. Return count as current streak.

## 7.2 Completion/Failure Prediction Algorithm

1. Load user model/scaler artifacts if available.  
2. Build feature vector from current context:
- `sin_hour`, `cos_hour`
- `day_of_week`, `is_weekend`
- `streak_length`, `habit_difficulty`
- `previous_day_completed`
3. Scale selected numeric features.
4. Predict completion probability.
5. Compute failure risk = `1 - completion_probability`.
6. On failure (model/data not available), use heuristic risk function.

## 7.3 Next Action Decision Algorithm

1. Filter habits not completed today.
2. Keep only habits in active time window.
3. For each, compute:
- predicted completion probability
- current streak
- priority score
4. Select habit with max score.
5. Return action payload for UI.

---

# CHAPTER 8: CODE STRUCTURE

## 8.1 Core Files

- `habit_tracker/app.py`
- `habit_tracker/models.py`
- `habit_tracker/ml_logic.py`
- `habit_tracker/decision_engine.py`
- `habit_tracker/scheduler.py`
- `habit_tracker/report_generator.py`

## 8.2 Blueprint Files

- `habit_tracker/blueprints/auth.py`
- `habit_tracker/blueprints/dashboard.py`
- `habit_tracker/blueprints/habits.py`
- `habit_tracker/blueprints/api.py`
- `habit_tracker/blueprints/profile.py`
- `habit_tracker/blueprints/social.py`
- `habit_tracker/blueprints/admin.py`

## 8.3 UI Files

- `habit_tracker/templates/*.html`
- `habit_tracker/static/css/style.css`
- `habit_tracker/static/js/*.js`

---

# CHAPTER 9: TEST CASES

| Test ID | Scenario | Input | Expected Output | Status |
|---|---|---|---|---|
| TC-01 | Register user | valid username/email/password | account created | Pass |
| TC-02 | Duplicate email | existing email | validation error | Pass |
| TC-03 | Login | valid credentials | dashboard opens | Pass |
| TC-04 | Add habit | name + daily frequency | habit saved | Pass |
| TC-05 | Log completion | habit + date | log inserted/updated | Pass |
| TC-06 | Prediction request (no model) | user with low data | heuristic score returned | Pass |
| TC-07 | Prediction request (model exists) | trained user | ML probability returned | Pass |
| TC-08 | Next action | active time window | highest-priority habit returned | Pass |
| TC-09 | Reminder scheduler | upcoming habit | reminder email triggered | Pass |
| TC-10 | Leaderboard | XP update | rank reflects latest XP | Pass |

---

# CHAPTER 10: INPUT AND OUTPUT SCREENS

The project includes the following key screens:
- Home/Landing page (`index.html`)
- Registration and Login pages (`register.html`, `login.html`)
- Main dashboard (`dashboard.html`)
- Profile page (`profile.html`)
- Leaderboard page (`leaderboard.html`)
- Friends/Social page (`friends.html`)
- Session mode page (`session_mode.html`)
- Admin page (`admin.html`)
- Password reset screens (`reset_request.html`, `reset_token.html`)

Each screen is connected to backend routes through Flask blueprints and displays user-centric data from the database and analytics engine.

---

# CHAPTER 11: CONCLUSION

The Smart Habit Tracker project demonstrates how a conventional productivity tool can be upgraded into an intelligent behavior-support platform. By combining daily tracking with predictive analytics, next-action guidance, reminders, and gamified engagement, the system improves the chance of sustained user adherence.

The implementation is modular, extensible, and production-oriented for academic scope. It fulfills the defined SRS requirements and provides a strong foundation for future improvements such as advanced personalization and cross-platform delivery.

---

# CHAPTER 12: LITERATURE REVIEW

## [1] Habit Formation and Behavior Change

Research in behavior science emphasizes the role of consistency, cues, and reward loops in long-term habit formation. Systems that track repetitions and trigger timely interventions are more effective than passive logging systems.

## [2] Digital Self-Tracking Systems

Prior digital habit tools show that progress visualization and streak metrics increase engagement; however, many lack adaptive intelligence and personalized recommendations.

## [3] Predictive Analytics in Personal Productivity

Machine learning approaches can model short-term completion probability using temporal features, historical consistency, and contextual variables, enabling proactive assistance.

## [4] Gamification in Motivation Systems

XP, badges, and leaderboards have measurable impact on user retention when integrated with meaningful progress signals rather than cosmetic rewards alone.

## [5] Notification Timing and Adherence

Time-window-based reminders improve adherence when notifications are contextual, limited, and aligned with user-defined schedules.

---

# CHAPTER 13: REFERENCES

1. Project SRS Document: `habit_tracker/SRS.md`  
2. Flask Documentation: https://flask.palletsprojects.com/  
3. Flask-SQLAlchemy Documentation: https://flask-sqlalchemy.palletsprojects.com/  
4. Flask-Login Documentation: https://flask-login.readthedocs.io/  
5. APScheduler Documentation: https://apscheduler.readthedocs.io/  
6. scikit-learn Documentation (Logistic Regression): https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html  
7. Source implementation files: `habit_tracker/app.py`, `habit_tracker/models.py`, `habit_tracker/ml_logic.py`, `habit_tracker/decision_engine.py`

---

## ANNEXURE (Optional)

- Source code snapshots  
- Database schema export  
- Additional screenshots  
- User manual
