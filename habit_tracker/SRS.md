Title: Smart Habit Tracker with Behavioural Analytics 

1. Introduction 
1.1 Purpose 
This Software Requirements Specification (SRS) document describes the functional and non-functional requirements of the Smart Habit Tracker with Behavioral Analytics and ML Predictions. The document is intended for developers, testers, project guides, evaluators, and stakeholders to clearly understand the system requirements and scope. 

1.2 Scope 
The Smart Habit Tracker is a web-based application that allows users to register, log in, create and track daily habits, analyze habit consistency, view behavioral analytics, and receive machine learning–based predictions about future habit completion. The system also provides rule-based suggestions to help users improve habit regularity. 
The application focuses on habit tracking, analytics, predictions, visualization, and general nutrition-related habit suggestions. The system does not provide medical diagnosis, personalized diet plans, or clinical nutritional advice. All food-related suggestions are generic, rule-based, and intended only to support healthy habit formation. 

1.3 Definitions, Acronyms, and Abbreviations 
 UI – User Interface 
 API – Application Programming Interface 
 ML – Machine Learning 
 DB – Database 
 Admin – System administrator 

1.4 References 
 IEEE 830 – Software Requirements Specification Standard 
 
2. Overall Description 
2.1 Product Perspective 
The Smart Habit Tracker is a standalone web application developed using a client–server architecture. The frontend is implemented using HTML and CSS, while the backend is built using Python and the Flask framework. A relational SQL database is used for data storage, and machine learning models are integrated for prediction purposes. 

2.2 Product Features 
 - User registration and authentication 
 - Habit creation and management 
 - Daily habit logging 
 - Behavioral analytics (consistency, streaks, breaks) 
 - ML-based habit completion prediction 
 - Rule-based habit-support suggestions 
 - Dashboard with charts and reports 
 - Automated Email Reminders (Time-sensitive)
 - Gamification System (XP and Leaderboard)

2.3 User Classes and Characteristics 
End Users 
 - Can register and log in 
 - Can create and manage habits 
 - Can log daily habit completion 
 - Can view analytics, predictions, charts, and suggestions 
 - Can earn XP and view leaderboard position
Administrator (Optional) 
 - Can view overall system statistics 
 - Can monitor user activity 

2.4 Constraints 
 - The system must run on all major web browsers 
 - Database must be relational (MySQL or SQLite) 
 - ML models must be trained offline 
 - Internet connection is required for access 
 
3. System Features 
3.1 User Registration Module 
Description: Allows new users to create an account in the system. 
Functional Requirements: 
 FR1: User shall provide name, email, and password during registration. 
 FR2: System shall validate duplicate email addresses. 
 FR3: System shall securely store user credentials. 

3.2 Login Module 
Description: Authenticates users and provides access to the system. 
Functional Requirements: 
 FR4: User shall log in using valid email and password. 
 FR5: System shall maintain user session after successful login. 

3.3 Habit Management Module 
Description: Allows users to create and manage habits. 
Functional Requirements: 
 FR6: User shall be able to add new habits with habit name and type. 
 FR7: User shall be able to view and manage existing habits. 

3.4 Daily Habit Logging Module 
Description: Enables users to record daily habit completion. 
Functional Requirements: 
 FR8: User shall mark a habit as completed or missed for a selected date. 
 FR9: System shall store daily habit logs in the database. 

3.5 Analytics and Dashboard Module 
Description: Displays habit analytics and trends. 
Functional Requirements: 
 FR10: System shall calculate habit consistency percentage. 
 FR11: System shall calculate current streak and break patterns. 
 FR12: System shall display analytics on the user dashboard. 

3.6 ML Prediction Module 
Description: Predicts the probability of habit completion for the next day. 
Functional Requirements: 
 FR13: System shall use a trained ML model to predict next-day habit completion. 
 FR14: System shall classify prediction results into risk levels (Low, Medium, High). 

3.7 Suggestions Module 
Description: Provides general habit-support suggestions. 
Functional Requirements: 
 FR15: System shall generate rule-based suggestions based on habit type, consistency, and risk level. 
 FR16: Suggestions shall be non-medical and advisory in nature. 

3.8 Notification & Scheduling Module
Description: Manages time-sensitive habits and sends automated reminders.
Functional Requirements:
 FR17: User shall be able to set a specific time window (start/end time) for each habit.
 FR18: System shall send specific notifications/emails for upcoming habits (5 minutes before start).
 FR19: System shall notify users of missed habits after the time window expires.

3.9 Gamification Module
Description: Increases user engagement through rewards and competition.
Functional Requirements:
 FR20: System shall maintain a user leaderboard based on habit streaks/completion and XP.
 FR21: System shall award points (XP) for consistent habit completion.

4. External Interface Requirements 
4.1 User Interface 
 - Web-based UI using HTML and CSS 
 - Responsive dashboard layout 
4.2 Hardware Interfaces 
 - Standard desktop or mobile devices 
4.3 Software Interfaces 
 - SQL database interface 
 - Machine learning model file interface 
 - SMTP Server interface for emails

5. Non-Functional Requirements 
5.1 Performance 
 System shall generate analytics and predictions with minimal delay. 
5.2 Security 
 Passwords shall be securely stored using encryption techniques. 
 Unauthorized access shall be restricted. 
5.3 Usability 
 System shall provide a simple and intuitive user interface. 
5.4 Reliability 
 System shall handle missing or incomplete habit logs gracefully. 
 
6. System Models 
 Use Case Diagram 
 ER Diagram 
 Sequence Diagram 
 
7. Conclusion 
This SRS document defines the functional and non-functional requirements of the Smart Habit Tracker with Behavioral Analytics and ML Predictions. It serves as a reference for system design, development, testing, and evaluation, ensuring clarity and consistency throughout the project lifecycle. 
