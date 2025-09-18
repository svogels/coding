# Programming Fundamentals Educational Website

## Overview
This is an interactive educational website designed to teach programming fundamentals with full student authentication and progress tracking. It features two main lesson modules:
- **Coding.html**: Comprehensive programming fundamentals with quizzes, matching activities, and a timeline exercise
- **Coding_al.html**: Adapted lesson version with simplified language and teacher notes

## Project Architecture
- **Type**: Full-stack web application with Flask backend and PostgreSQL database
- **Frontend**: HTML, CSS, and JavaScript with interactive educational activities
- **Backend**: Flask with Flask-Login authentication and Flask-WTF forms
- **Database**: PostgreSQL with user accounts, lesson tracking, and progress storage
- **Authentication**: Email-based registration and login system
- **Dependencies**: 
  - Backend: Flask, Flask-Login, Flask-WTF, psycopg2-binary
  - Frontend: jsPDF library from CloudFlare CDN for PDF generation
- **Server**: Flask development server on port 5000

## Features
- **Student Authentication**: Email-based registration and secure login system
- **Automatic Progress Tracking**: All student work automatically saved as they type/click
- **Interactive Learning Activities**:
  - Definition matching with immediate feedback
  - Multiple choice quizzes with progress tracking
  - Timeline creation for programming history
  - Research questions and brainstorm activities
- **PDF Progress Reports**: Students can download personalized PDF reports of their work
- **Teacher Dashboard**: Monitor all student progress and view detailed responses
- **Adaptive Content**: Two lesson versions (standard and simplified for accessibility)
- **Session Management**: Students can logout and return anytime with work preserved
- **Responsive Design**: Works on phones, tablets, and computers

## Current Setup
- **Development Server**: Flask application on port 5000
- **Database**: PostgreSQL with proper schema and relationships
- **Authentication**: Flask-Login with secure session management
- **Host Configuration**: Properly configured to bind to 0.0.0.0 for Replit environment

## Hosting & Student Access

### Deployment Instructions
1. **Use Autoscale Deployment** (recommended for educational sites)
   - Click the "Publish" button in your Replit workspace
   - Choose "Autoscale Deployment" for cost-effective hosting
   - Only pay when students are actively using the site
   - Automatically scales during peak usage (assignment deadlines, etc.)

2. **Cost Estimates** (with Replit Core $25/month credits)
   - Example: 30 students × 10 lessons × 50 requests each ≈ $3.50/month
   - Perfect for most classroom scenarios
   - Unused credits don't roll over monthly

### Student Access
- **No Replit accounts required** - Students access via direct URL
- **Professional URL provided** after deployment (e.g., `https://your-app-name.username.repl.co`)
- **Share URL through**: Email, LMS, school website, or QR code
- **Works on any device**: Phones, tablets, laptops without special software
- **24/7 availability**: Students can access from home, school, or library

### Student Workflow
1. **First time**: Student visits URL → Registers with email/password
2. **Return visits**: Student visits URL → Logs in with email
3. **During lessons**: All work automatically saves as they progress
4. **Anytime**: Students can download PDF reports of their completed work

### Classroom Management
- **Monitor usage** through Replit's analytics dashboard
- **Teacher dashboard** accessible at `/teacher.html` (username: `teacher`, password: `education123`)
- **View all students**: Registration dates, lesson progress, detailed responses
- **Professional reliability**: Hosted on Replit's cloud infrastructure

## Recent Changes (September 18, 2025)
- **Transformed to full authentication system**: Added email-based student registration and login
- **Implemented automatic progress tracking**: All student work saves in real-time to PostgreSQL database
- **Added teacher dashboard**: Teachers can monitor all student progress and responses
- **Enhanced PDF functionality**: Students get personalized progress reports with their names
- **Configured Flask backend**: Secure session management with Flask-Login
- **Database integration**: PostgreSQL with proper schema for users, lessons, and responses
- **Ready for deployment**: Configured for Replit Autoscale hosting with cost-effective scaling

## User Preferences
- **Educational focus**: Maintained interactive elements while adding professional authentication
- **Clean, accessible design**: Preserved original design patterns with enhanced functionality
- **Student-centered approach**: All features designed for ease of use by students and teachers

## File Structure
```
/
├── app.py                 # Flask backend with authentication and API endpoints
├── index.html             # Main navigation page (login-protected)
├── Coding.html            # Primary lesson content with progress tracking
├── Coding_al.html         # Adapted lesson with simplified language
├── teacher.html           # Teacher dashboard for monitoring students
├── LICENSE                # Project license
├── .replit                # Replit configuration
└── replit.md              # This documentation file
```

## Database Schema
- **students**: User accounts with email authentication and profile information
- **lessons**: Lesson metadata and configuration
- **student_responses**: All student work and progress with timestamps

## Deployment Notes
- **Production ready**: Flask application with proper session management
- **Database included**: PostgreSQL automatically configured in Replit environment
- **External dependencies**: jsPDF served via CDN for reliable PDF generation
- **Autoscale compatible**: Designed for variable educational traffic patterns
- **Security considerations**: Password hashing, session management, and CSRF protection