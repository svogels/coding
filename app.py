import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('PGHOST'),
        database=os.getenv('PGDATABASE'), 
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        port=os.getenv('PGPORT')
    )

# Serve specific HTML files only - security hardening
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/index.html')
def index_html():
    return send_from_directory('.', 'index.html')

@app.route('/Coding.html')
def coding_html():
    return send_from_directory('.', 'Coding.html')

@app.route('/Coding_al.html')
def coding_al_html():
    return send_from_directory('.', 'Coding_al.html')

@app.route('/teacher.html')
def teacher_html():
    return send_from_directory('.', 'teacher.html')

# Student authentication/identification
@app.route('/api/student/login', methods=['POST'])
def student_login():
    data = request.json
    student_name = data.get('student_name')
    student_id = data.get('student_id', '')
    class_name = data.get('class_name', '')
    
    if not student_name:
        return jsonify({'error': 'Student name is required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check if student exists
        cur.execute("SELECT * FROM students WHERE student_name = %s AND student_id = %s", 
                   (student_name, student_id))
        student = cur.fetchone()
        
        if not student:
            # Create new student
            cur.execute("""
                INSERT INTO students (student_name, student_id, class_name) 
                VALUES (%s, %s, %s) RETURNING *
            """, (student_name, student_id, class_name))
            student = cur.fetchone()
            conn.commit()
        
        return jsonify({'student': dict(student)})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Save student response
@app.route('/api/response/save', methods=['POST'])
def save_response():
    data = request.json
    student_db_id = data.get('student_db_id')
    lesson_slug = data.get('lesson_slug')
    question_type = data.get('question_type')
    question_id = data.get('question_id')
    student_answer = data.get('student_answer')
    is_correct = data.get('is_correct')
    
    if not all([student_db_id, lesson_slug, question_type, question_id]):
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
        
        # Check if response already exists
        cur.execute("""
            SELECT id FROM student_responses 
            WHERE student_id = %s AND lesson_id = %s AND question_type = %s AND question_id = %s
        """, (student_db_id, lesson_id, question_type, question_id))
        
        existing = cur.fetchone()
        
        # Use UPSERT with unique constraint to handle concurrent requests
        cur.execute("""
            INSERT INTO student_responses (student_id, lesson_id, question_type, question_id, student_answer, is_correct)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_id, lesson_id, question_type, question_id)
            DO UPDATE SET 
                student_answer = EXCLUDED.student_answer,
                is_correct = EXCLUDED.is_correct,
                updated_at = CURRENT_TIMESTAMP
        """, (student_db_id, lesson_id, question_type, question_id,
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

# Get student progress for a lesson
@app.route('/api/student/<int:student_id>/lesson/<lesson_slug>/progress', methods=['GET'])
def get_student_progress(student_id, lesson_slug):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT sr.* FROM student_responses sr
            JOIN lessons l ON sr.lesson_id = l.id
            WHERE sr.student_id = %s AND l.lesson_slug = %s
            ORDER BY sr.updated_at DESC
        """, (student_id, lesson_slug))
        
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
            SELECT s.*, 
                   COUNT(DISTINCT sr.lesson_id) as lessons_started,
                   COUNT(sr.id) as total_responses
            FROM students s
            LEFT JOIN student_responses sr ON s.id = sr.student_id
            GROUP BY s.id
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)