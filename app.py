import os
import json
from flask import Flask, request, jsonify, send_from_directory, render_template_string, redirect, url_for, session, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this lesson.'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, student_name, student_id, class_name, is_active=True):
        self.id = id
        self.email = email
        self.student_name = student_name
        self.student_id = student_id
        self.class_name = class_name
        self.is_active = is_active

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM students WHERE id = %s AND is_active = TRUE", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            return User(user_data['id'], user_data['email'], user_data['student_name'], 
                       user_data['student_id'], user_data['class_name'], user_data['is_active'])
    finally:
        cur.close()
        conn.close()
    return None

# Forms
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    student_name = StringField('Full Name', validators=[DataRequired()])
    student_id = StringField('Student ID (optional)')
    class_name = StringField('Class/Grade (optional)')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('PGHOST'),
        database=os.getenv('PGDATABASE'), 
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        port=os.getenv('PGPORT')
    )

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Check if email already exists
            cur.execute("SELECT id FROM students WHERE email = %s", (form.email.data,))
            if cur.fetchone():
                flash('Email already registered. Please log in instead.', 'error')
                return redirect(url_for('login'))
            
            # Create new user
            password_hash = generate_password_hash(form.password.data)
            cur.execute("""
                INSERT INTO students (email, student_name, student_id, class_name, password_hash)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (form.email.data, form.student_name.data, form.student_id.data or '', 
                  form.class_name.data or '', password_hash))
            
            user_id = cur.fetchone()[0]
            conn.commit()
            
            # Log the user in
            user = User(user_id, form.email.data, form.student_name.data, 
                       form.student_id.data or '', form.class_name.data or '')
            login_user(user)
            
            flash('Registration successful! Welcome to the Programming Fundamentals course.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            conn.rollback()
            flash('Registration failed. Please try again.', 'error')
        finally:
            cur.close()
            conn.close()
    
    return render_template_string(REGISTER_TEMPLATE, form=form)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("SELECT * FROM students WHERE email = %s AND is_active = TRUE", 
                       (form.email.data,))
            user_data = cur.fetchone()
            
            if user_data and check_password_hash(user_data['password_hash'], form.password.data):
                # Update last login
                cur.execute("UPDATE students SET last_login = CURRENT_TIMESTAMP WHERE id = %s", 
                           (user_data['id'],))
                conn.commit()
                
                user = User(user_data['id'], user_data['email'], user_data['student_name'],
                           user_data['student_id'], user_data['class_name'])
                login_user(user)
                
                flash(f'Welcome back, {user.student_name}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            flash('Login failed. Please try again.', 'error')
        finally:
            cur.close()
            conn.close()
    
    return render_template_string(LOGIN_TEMPLATE, form=form)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Serve specific HTML files - now with authentication
@app.route('/')
def index():
    if current_user.is_authenticated:
        return send_from_directory('.', 'index.html')
    else:
        return redirect(url_for('login'))

@app.route('/index.html')
@login_required
def index_html():
    return send_from_directory('.', 'index.html')

@app.route('/Coding.html')
@login_required
def coding_html():
    return send_from_directory('.', 'Coding.html')

@app.route('/Coding_al.html')
@login_required
def coding_al_html():
    return send_from_directory('.', 'Coding_al.html')

@app.route('/teacher.html')
def teacher_html():
    return send_from_directory('.', 'teacher.html')

# API Health Check endpoint
@app.route('/api', methods=['GET', 'HEAD'])
def api_health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Programming Fundamentals Educational Platform'
    })

# Get current user info for JavaScript
@app.route('/api/user/current', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'student_name': current_user.student_name,
        'student_id': current_user.student_id,
        'class_name': current_user.class_name
    })

# Save student response (now using authenticated user)
@app.route('/api/response/save', methods=['POST'])
@login_required
def save_response():
    data = request.json
    lesson_slug = data.get('lesson_slug')
    question_type = data.get('question_type')
    question_id = data.get('question_id')
    student_answer = data.get('student_answer')
    is_correct = data.get('is_correct')
    
    if not all([lesson_slug, question_type, question_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get lesson ID
        cur.execute("SELECT id FROM lessons WHERE lesson_slug = %s", (lesson_slug,))
        lesson = cur.fetchone()
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        lesson_id = lesson[0]
        
        # Use UPSERT with authenticated user
        cur.execute("""
            INSERT INTO student_responses (student_id, lesson_id, question_type, question_id, student_answer, is_correct)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_id, lesson_id, question_type, question_id)
            DO UPDATE SET 
                student_answer = EXCLUDED.student_answer,
                is_correct = EXCLUDED.is_correct,
                updated_at = CURRENT_TIMESTAMP
        """, (current_user.id, lesson_id, question_type, question_id,
              json.dumps(student_answer) if isinstance(student_answer, (dict, list)) else student_answer,
              is_correct))
        
        conn.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Get student progress for a lesson (now using authenticated user)
@app.route('/api/student/lesson/<lesson_slug>/progress', methods=['GET'])
@login_required
def get_student_progress(lesson_slug):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT sr.* FROM student_responses sr
            JOIN lessons l ON sr.lesson_id = l.id
            WHERE sr.student_id = %s AND l.lesson_slug = %s
            ORDER BY sr.updated_at DESC
        """, (current_user.id, lesson_slug))
        
        responses = cur.fetchall()
        return jsonify({'responses': [dict(r) for r in responses]})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Simple teacher authentication (in production, use proper session-based auth)
def require_teacher_auth():
    auth = request.authorization
    if not auth or not (auth.username == 'teacher' and auth.password == 'education123'):
        return False
    return True

# Teacher dashboard - get all students (with authentication)
@app.route('/api/teacher/students', methods=['GET'])
def get_all_students():
    if not require_teacher_auth():
        return jsonify({'error': 'Authentication required'}), 401
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT s.id, s.email, s.student_name, s.student_id, s.class_name, s.created_at, s.last_login,
                   COUNT(DISTINCT sr.lesson_id) as lessons_started,
                   COUNT(sr.id) as total_responses
            FROM students s
            LEFT JOIN student_responses sr ON s.id = sr.student_id
            GROUP BY s.id, s.email, s.student_name, s.student_id, s.class_name, s.created_at, s.last_login
            ORDER BY s.created_at DESC
        """)
        
        students = cur.fetchall()
        return jsonify({'students': [dict(s) for s in students]})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Teacher dashboard - get student details (with authentication)
@app.route('/api/teacher/student/<int:student_id>/details', methods=['GET'])
def get_student_details(student_id):
    if not require_teacher_auth():
        return jsonify({'error': 'Authentication required'}), 401
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get student info
        cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cur.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get all responses with lesson info and last activity
        cur.execute("""
            SELECT sr.*, l.lesson_title, l.lesson_slug,
                   (SELECT MAX(updated_at) FROM student_responses WHERE student_id = %s) as last_activity
            FROM student_responses sr
            JOIN lessons l ON sr.lesson_id = l.id
            WHERE sr.student_id = %s
            ORDER BY l.lesson_title, sr.question_type, sr.question_id
        """, (student_id, student_id))
        
        responses = cur.fetchall()
        
        return jsonify({
            'student': dict(student),
            'responses': [dict(r) for r in responses]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Login - Programming Fundamentals</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .auth-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #005A9C;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="email"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background-color: #005A9C;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #004080;
        }
        .auth-link {
            text-align: center;
            margin-top: 20px;
        }
        .auth-link a {
            color: #005A9C;
            text-decoration: none;
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .flash-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .flash-error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .flash-info {
            background-color: #cce7ff;
            color: #004085;
            border: 1px solid #b3d7ff;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <h1>Student Login</h1>
        
        <div class="flash-messages">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>
        
        <form method="POST">
            {{ form.hidden_tag() }}
            
            <div class="form-group">
                {{ form.email.label(class="form-label") }}
                {{ form.email(class="form-control") }}
            </div>
            
            <div class="form-group">
                {{ form.password.label(class="form-label") }}
                {{ form.password(class="form-control") }}
            </div>
            
            {{ form.submit(class="btn") }}
        </form>
        
        <div class="auth-link">
            <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
        </div>
    </div>
</body>
</html>
'''

REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Registration - Programming Fundamentals</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .auth-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #005A9C;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="email"], input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background-color: #005A9C;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #004080;
        }
        .auth-link {
            text-align: center;
            margin-top: 20px;
        }
        .auth-link a {
            color: #005A9C;
            text-decoration: none;
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .flash-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .flash-error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .optional {
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <h1>Student Registration</h1>
        
        <div class="flash-messages">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>
        
        <form method="POST">
            {{ form.hidden_tag() }}
            
            <div class="form-group">
                {{ form.email.label(class="form-label") }}
                {{ form.email(class="form-control") }}
            </div>
            
            <div class="form-group">
                {{ form.student_name.label(class="form-label") }}
                {{ form.student_name(class="form-control") }}
            </div>
            
            <div class="form-group">
                {{ form.student_id.label(class="form-label") }}
                <span class="optional">(optional)</span>
                {{ form.student_id(class="form-control") }}
            </div>
            
            <div class="form-group">
                {{ form.class_name.label(class="form-label") }}
                <span class="optional">(optional)</span>
                {{ form.class_name(class="form-control") }}
            </div>
            
            <div class="form-group">
                {{ form.password.label(class="form-label") }}
                {{ form.password(class="form-control") }}
            </div>
            
            <div class="form-group">
                {{ form.confirm_password.label(class="form-label") }}
                {{ form.confirm_password(class="form-control") }}
            </div>
            
            {{ form.submit(class="btn") }}
        </form>
        
        <div class="auth-link">
            <p>Already have an account? <a href="{{ url_for('login') }}">Log in here</a></p>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)