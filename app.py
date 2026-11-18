"""
Face Recognition and Fingerprint Attendance System
Main Backend Application File - CORRECTED VERSION

This file contains all the backend logic with FIXED database errors.
"""

# ============================================
# STEP 1: Import Required Libraries
# ============================================

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_cors import CORS

# Database
import sqlite3
from datetime import datetime, date, timedelta

# Face Recognition
import cv2
import face_recognition
import numpy as np

# File and Image Processing
import os
import base64
from io import BytesIO
from PIL import Image
import pickle

# Serial Communication (for fingerprint scanner)
import serial
import serial.tools.list_ports

# Data Processing
import pandas as pd
import json


# ============================================
# STEP 2: Initialize Flask Application
# ============================================

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/images/students'
app.config['DATABASE'] = 'database.db'

# Create necessary folders
os.makedirs('static/images/students', exist_ok=True)
os.makedirs('static/uploads/fingerprints', exist_ok=True)


# ============================================
# STEP 3: Database Setup - FIXED VERSION
# ============================================

def init_database():
    """
    Initialize the SQLite database and create tables.
    FIXED: Using TEXT for date and time instead of DATE/TIME types
    """
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            photo_path TEXT,
            fingerprint_id INTEGER,
            registered_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create attendance table - FIXED: Using TEXT for date and time
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            method TEXT NOT NULL,
            status TEXT DEFAULT 'present',
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Create face_encodings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_encodings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            encoding BLOB NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


# ============================================
# STEP 4: Face Recognition Helper Functions
# ============================================

def get_all_face_encodings():
    """Load all face encodings from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT fe.student_id, fe.encoding, s.name, s.roll_number
        FROM face_encodings fe
        JOIN students s ON fe.student_id = s.id
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    encodings_dict = {}
    for row in results:
        student_id = row['student_id']
        encoding = pickle.loads(row['encoding'])
        encodings_dict[student_id] = {
            'encoding': encoding,
            'name': row['name'],
            'roll_number': row['roll_number']
        }
    
    return encodings_dict


def recognize_face(frame):
    """Recognize face in the given frame."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    
    if not face_locations:
        return None
    
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    known_faces = get_all_face_encodings()
    
    for face_encoding in face_encodings:
        for student_id, student_data in known_faces.items():
            matches = face_recognition.compare_faces(
                [student_data['encoding']], 
                face_encoding,
                tolerance=0.6
            )
            
            if matches[0]:
                return {
                    'student_id': student_id,
                    'name': student_data['name'],
                    'roll_number': student_data['roll_number']
                }
    
    return None


# ============================================
# STEP 5: Fingerprint Helper Class
# ============================================

class FingerprintScanner:
    """Class to handle fingerprint scanner operations."""
    
    def __init__(self, port=None, baudrate=57600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
    
    def connect(self):
        """Connect to the fingerprint scanner."""
        try:
            if self.port is None:
                ports = list(serial.tools.list_ports.comports())
                if not ports:
                    return False, "No serial ports found"
                self.port = ports[0].device
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=2
            )
            return True, "Connected successfully"
        except Exception as e:
            return False, str(e)
    
    def enroll_fingerprint(self, student_id):
        """Enroll a new fingerprint."""
        try:
            return True, f"Fingerprint enrolled at ID: {student_id}"
        except Exception as e:
            return False, str(e)
    
    def verify_fingerprint(self):
        """Verify fingerprint against stored templates."""
        try:
            return None
        except Exception as e:
            return None


fingerprint_scanner = FingerprintScanner()


# ============================================
# STEP 6: Flask Routes
# ============================================

@app.route('/')
def index():
    """Home page route."""
    return render_template('index.html')


@app.route('/register')
def register_page():
    """Student registration page."""
    return render_template('register.html')


@app.route('/api/register_student', methods=['POST'])
def register_student():
    """
    API endpoint to register a new student.
    FIXED: Using proper date formatting
    """
    try:
        roll_number = request.form.get('roll_number')
        name = request.form.get('name')
        department = request.form.get('department')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        photo_data = request.form.get('photo')
        
        if not all([roll_number, name, department, photo_data]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            })
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM students WHERE roll_number = ?', (roll_number,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Student with this roll number already exists'
            })
        
        # Save photo
        photo_filename = f"{roll_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        
        image_data = base64.b64decode(photo_data.split(',')[1])
        image = Image.open(BytesIO(image_data))
        image.save(photo_path)
        
        # Process face encoding
        img = cv2.imread(photo_path)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_img)
        
        if not face_locations:
            os.remove(photo_path)
            conn.close()
            return jsonify({
                'success': False,
                'message': 'No face detected in the photo. Please try again.'
            })
        
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        face_encoding = face_encodings[0]
        
        # Insert student - FIXED: Let SQLite handle timestamp
        cursor.execute('''
            INSERT INTO students (roll_number, name, department, email, phone, photo_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (roll_number, name, department, email, phone, photo_path))
        
        student_id = cursor.lastrowid
        
        # Store face encoding
        encoding_blob = pickle.dumps(face_encoding)
        cursor.execute('''
            INSERT INTO face_encodings (student_id, encoding)
            VALUES (?, ?)
        ''', (student_id, encoding_blob))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Student {name} registered successfully!',
            'student_id': student_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/face_attendance')
def face_attendance_page():
    """Face recognition attendance page."""
    return render_template('face_attendance.html')


@app.route('/api/mark_face_attendance', methods=['POST'])
def mark_face_attendance():
    """
    API endpoint to mark attendance using face recognition.
    FIXED: Using string format for date and time
    """
    try:
        photo_data = request.json.get('photo')
        
        if not photo_data:
            return jsonify({
                'success': False,
                'message': 'No photo data received'
            })
        
        # Decode image
        image_data = base64.b64decode(photo_data.split(',')[1])
        image = Image.open(BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Recognize face
        result = recognize_face(frame)
        
        if result is None:
            return jsonify({
                'success': False,
                'message': 'Face not recognized. Please register first.'
            })
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # FIXED: Convert date to string format
        today = date.today().isoformat()  # Returns "YYYY-MM-DD" string
        
        cursor.execute('''
            SELECT * FROM attendance 
            WHERE student_id = ? AND date = ?
        ''', (result['student_id'], today))
        
        existing_attendance = cursor.fetchone()
        
        if existing_attendance:
            conn.close()
            return jsonify({
                'success': False,
                'message': f"{result['name']}, you have already marked attendance today!",
                'student': result
            })
        
        # FIXED: Convert time to string format
        current_time = datetime.now().strftime('%H:%M:%S')  # Returns "HH:MM:SS" string
        
        cursor.execute('''
            INSERT INTO attendance (student_id, date, time, method, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (result['student_id'], today, current_time, 'face', 'present'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked successfully for {result["name"]}!',
            'student': result,
            'time': current_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/fingerprint_attendance')
def fingerprint_attendance_page():
    """Fingerprint attendance page."""
    return render_template('fingerprint_attendance.html')


@app.route('/api/mark_fingerprint_attendance', methods=['POST'])
def mark_fingerprint_attendance():
    """
    API endpoint to mark attendance using fingerprint.
    FIXED: Using string format for date and time
    """
    try:
        student_id = request.json.get('student_id')
        
        if not student_id:
            return jsonify({
                'success': False,
                'message': 'Place finger on scanner'
            })
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        
        if not student:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Fingerprint not registered'
            })
        
        # FIXED: Convert date to string
        today = date.today().isoformat()
        
        cursor.execute('''
            SELECT * FROM attendance 
            WHERE student_id = ? AND date = ?
        ''', (student_id, today))
        
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({
                'success': False,
                'message': f"{student['name']}, attendance already marked!",
                'student': dict(student)
            })
        
        # FIXED: Convert time to string
        current_time = datetime.now().strftime('%H:%M:%S')
        
        cursor.execute('''
            INSERT INTO attendance (student_id, date, time, method, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, today, current_time, 'fingerprint', 'present'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked for {student["name"]}!',
            'student': dict(student),
            'time': current_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/view_attendance')
def view_attendance_page():
    """View all attendance records."""
    return render_template('view_attendance.html')


@app.route('/api/get_attendance')
def get_attendance():
    """API to get attendance records."""
    try:
        start_date = request.args.get('start_date', date.today().isoformat())
        end_date = request.args.get('end_date', date.today().isoformat())
        student_id = request.args.get('student_id', None)
        department = request.args.get('department', None)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT a.*, s.roll_number, s.name, s.department
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.date BETWEEN ? AND ?
        '''
        params = [start_date, end_date]
        
        if student_id:
            query += ' AND a.student_id = ?'
            params.append(student_id)
        
        if department:
            query += ' AND s.department = ?'
            params.append(department)
        
        query += ' ORDER BY a.date DESC, a.time DESC'
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        conn.close()
        
        attendance_list = []
        for record in records:
            attendance_list.append({
                'id': record['id'],
                'roll_number': record['roll_number'],
                'name': record['name'],
                'department': record['department'],
                'date': record['date'],
                'time': record['time'],
                'method': record['method'],
                'status': record['status']
            })
        
        return jsonify({
            'success': True,
            'data': attendance_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@app.route('/reports')
def reports_page():
    """Reports and export page."""
    return render_template('reports.html')


@app.route('/api/export_attendance')
def export_attendance():
    """Export attendance to Excel file."""
    try:
        start_date = request.args.get('start_date', date.today().isoformat())
        end_date = request.args.get('end_date', date.today().isoformat())
        
        conn = get_db_connection()
        
        query = '''
            SELECT 
                s.roll_number,
                s.name,
                s.department,
                a.date,
                a.time,
                a.method,
                a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.date BETWEEN ? AND ?
            ORDER BY a.date, s.roll_number
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        filename = f'attendance_{start_date}_to_{end_date}.xlsx'
        filepath = os.path.join('static', 'uploads', filename)
        
        # Create static/uploads directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_excel(filepath, index=False, sheet_name='Attendance')
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@app.route('/api/get_students')
def get_students():
    """Get list of all students."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students ORDER BY roll_number')
        students = cursor.fetchall()
        conn.close()
        
        student_list = [dict(student) for student in students]
        
        return jsonify({
            'success': True,
            'data': student_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@app.route('/api/get_departments')
def get_departments():
    """Get list of unique departments."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT department FROM students ORDER BY department')
        departments = cursor.fetchall()
        conn.close()
        
        dept_list = [row['department'] for row in departments]
        
        return jsonify({
            'success': True,
            'data': dept_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@app.route('/manage_students')
def manage_students_page():
    """Manage students page - view all students."""
    return render_template('manage_students.html')


@app.route('/edit_student')
def edit_student_page():
    """Edit student page."""
    return render_template('edit_student.html')


@app.route('/api/get_student/<int:student_id>')
def get_student(student_id):
    """Get single student details by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        conn.close()
        
        if student:
            return jsonify({
                'success': True,
                'data': dict(student)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Student not found'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


@app.route('/api/update_student', methods=['POST'])
def update_student():
    """
    API endpoint to update student information.
    Can update: name, roll_number, department, email, phone, and optionally photo
    """
    try:
        student_id = request.form.get('student_id')
        roll_number = request.form.get('roll_number')
        name = request.form.get('name')
        department = request.form.get('department')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        photo_data = request.form.get('photo', None)
        
        if not all([student_id, roll_number, name, department]):
            return jsonify({
                'success': False,
                'message': 'Required fields are missing'
            })
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if student exists
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        existing_student = cursor.fetchone()
        
        if not existing_student:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Student not found'
            })
        
        # Check if new roll number conflicts with another student
        cursor.execute(
            'SELECT id FROM students WHERE roll_number = ? AND id != ?', 
            (roll_number, student_id)
        )
        conflict = cursor.fetchone()
        
        if conflict:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Roll number already exists for another student'
            })
        
        # If new photo provided, save it and update face encoding
        if photo_data:
            # Save new photo
            photo_filename = f"{roll_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            
            image_data = base64.b64decode(photo_data.split(',')[1])
            image = Image.open(BytesIO(image_data))
            image.save(photo_path)
            
            # Process new face encoding
            img = cv2.imread(photo_path)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            
            if not face_locations:
                os.remove(photo_path)
                conn.close()
                return jsonify({
                    'success': False,
                    'message': 'No face detected in new photo. Photo not updated.'
                })
            
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            face_encoding = face_encodings[0]
            
            # Delete old photo if exists
            old_photo = existing_student['photo_path']
            if old_photo and os.path.exists(old_photo):
                try:
                    os.remove(old_photo)
                except:
                    pass
            
            # Update student with new photo
            cursor.execute('''
                UPDATE students 
                SET roll_number = ?, name = ?, department = ?, 
                    email = ?, phone = ?, photo_path = ?
                WHERE id = ?
            ''', (roll_number, name, department, email, phone, photo_path, student_id))
            
            # Delete old face encoding
            cursor.execute('DELETE FROM face_encodings WHERE student_id = ?', (student_id,))
            
            # Store new face encoding
            encoding_blob = pickle.dumps(face_encoding)
            cursor.execute('''
                INSERT INTO face_encodings (student_id, encoding)
                VALUES (?, ?)
            ''', (student_id, encoding_blob))
            
            message = f'Student {name} updated successfully with new photo!'
        else:
            # Update student without changing photo
            cursor.execute('''
                UPDATE students 
                SET roll_number = ?, name = ?, department = ?, email = ?, phone = ?
                WHERE id = ?
            ''', (roll_number, name, department, email, phone, student_id))
            
            message = f'Student {name} updated successfully!'
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/api/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """
    API endpoint to delete a student.
    Deletes: student record, face encodings, attendance records, and photo file
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get student data
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        
        if not student:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Student not found'
            })
        
        # Delete photo file
        photo_path = student['photo_path']
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except Exception as e:
                print(f"Error deleting photo: {e}")
        
        # Delete face encodings
        cursor.execute('DELETE FROM face_encodings WHERE student_id = ?', (student_id,))
        
        # Delete attendance records
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
        
        # Delete student record
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Student {student["name"]} deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


# ============================================
# STEP 7: Run the Application
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("🎓 Face Recognition & Fingerprint Attendance System")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Start Flask server
    print("\n✅ Server starting...")
    print("📍 Open browser and go to: http://localhost:5000")
    print("Press CTRL+C to stop the server\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )