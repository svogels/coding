# Programming Fundamentals Educational Website

## Overview
This is an interactive educational website designed to teach programming fundamentals. It features two main lesson modules:
- **Coding.html**: Comprehensive programming fundamentals with quizzes, matching activities, and a timeline exercise
- **Coding_al.html**: Adapted lesson version with simplified language and teacher notes

## Project Architecture
- **Type**: Static HTML website with interactive JavaScript features
- **Structure**: Simple flat file structure with HTML, CSS, and JavaScript
- **Dependencies**: 
  - External: jsPDF library from CloudFlare CDN for PDF generation
  - No backend dependencies - fully client-side
- **Server**: Python 3.11 HTTP server for development and deployment

## Features
- Interactive definition matching activities
- Multiple choice quizzes with immediate feedback
- Timeline creation for programming history
- PDF export functionality for student responses
- Teacher notes and adapted content for different learning levels
- Responsive design with clean, professional styling

## Current Setup
- **Development Server**: Python HTTP server on port 5000
- **Deployment**: Configured for Replit Autoscale deployment
- **Host Configuration**: Properly configured to bind to 0.0.0.0 for Replit environment

## Recent Changes (September 18, 2025)
- Imported from GitHub repository
- Set up Python 3.11 development environment
- Configured web server workflow for Replit environment
- Tested all pages and interactive functionality
- Configured deployment settings for production
- Verified external CDN dependencies are accessible

## User Preferences
- Static HTML approach maintained from original project
- Educational focus preserved with interactive elements
- Clean, accessible design patterns followed

## File Structure
```
/
├── index.html          # Main navigation page
├── Coding.html         # Primary lesson content
├── Coding_al.html      # Adapted lesson content
├── LICENSE             # Project license
├── .replit             # Replit configuration
└── replit.md           # This documentation file
```

## Deployment Notes
- Uses Python HTTP server for both development and production
- External dependencies served via CDN (jsPDF)
- No build process required - direct HTML serving
- Static content suitable for autoscale deployment