# app.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from authentication.login import Authentication
from functools import wraps
import os
import sqlite3
from datetime import datetime
import hashlib
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

auth = Authentication()

# Database connection
def get_db():
    db = sqlite3.connect('database/hospital.db')
    db.row_factory = sqlite3.Row
    return db

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') != role:
                flash('Access denied', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =========================
# HOME
# =========================
@app.route("/")
def home():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif session.get('role') == 'patient':
            return redirect(url_for('patient_dashboard'))
    return render_template("index.html")

# =========================
# LOGIN PAGE
# =========================
@app.route("/login")
def login_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template("login.html")

# =========================
# LOGIN API
# =========================
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    
    user = auth.login(
        data.get("username"),
        data.get("password")
    )
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        
        return jsonify({
            "success": True,
            "role": user["role"],
            "user": user
        })
    
    return jsonify({
        "success": False,
        "message": "Invalid Username or Password"
    })

# =========================
# REGISTER PAGE
# =========================
@app.route("/register")
def register_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template("register.html")

# =========================
# REGISTER API
# =========================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'password', 'role', 'full_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "success": False,
                "message": f"Missing required field: {field}"
            })
    
    success, message = auth.register_user(
        username=data.get("username"),
        password=data.get("password"),
        role=data.get("role"),
        full_name=data.get("full_name"),
        
        # Common Fields
        email=data.get("email"),
        phone=data.get("phone"),
        gender=data.get("gender"),
        age=data.get("age"),
        
        # Patient Profile
        address=data.get("address"),
        medical_history=data.get("medical_history"),
        emergency_contact=data.get("emergency_contact"),
        blood_group=data.get("blood_group"),
        
        # Doctor Profile
        specialization=data.get("specialization"),
        years_experience=data.get("years_experience"),
        qualification=data.get("qualification"),
        hospital_name=data.get("hospital_name"),
        consultation_fee=data.get("consultation_fee"),
        bio=data.get("bio"),
        available_days=data.get("available_days"),
        available_time=data.get("available_time")
    )
    
    return jsonify({
        "success": success,
        "message": message
    })

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin/dashboard")
@login_required
@role_required('admin')
def admin_dashboard():
    db = get_db()
    
    # Get statistics
    total_users = db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_doctors = db.execute('SELECT COUNT(*) as count FROM doctors').fetchone()['count']
    total_patients = db.execute('SELECT COUNT(*) as count FROM users WHERE role = "patient"').fetchone()['count']
    total_predictions = db.execute('SELECT COUNT(*) as count FROM predictions').fetchone()['count']
    
    # Recent predictions
    recent_predictions = db.execute(
        '''SELECT p.*, u.full_name as patient_name 
           FROM predictions p 
           JOIN users u ON p.patient_id = u.id 
           ORDER BY p.created_at DESC LIMIT 5'''
    ).fetchall()
    
    db.close()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_predictions=total_predictions,
                         recent_predictions=recent_predictions)

@app.route("/admin/users")
@login_required
@role_required('admin')
def admin_users():
    db = get_db()
    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin/users.html', users=users)

@app.route("/admin/doctors")
@login_required
@role_required('admin')
def admin_doctors():
    db = get_db()
    doctors = db.execute(
        '''SELECT d.*, u.full_name, u.email, u.phone 
           FROM doctors d 
           JOIN users u ON d.user_id = u.id'''
    ).fetchall()
    db.close()
    return render_template('admin/doctors.html', doctors=doctors)

@app.route("/admin/patients")
@login_required
@role_required('admin')
def admin_patients():
    db = get_db()
    patients = db.execute(
        'SELECT * FROM users WHERE role = "patient" ORDER BY created_at DESC'
    ).fetchall()
    db.close()
    return render_template('admin/patients.html', patients=patients)

@app.route("/admin/predictions")
@login_required
@role_required('admin')
def admin_predictions():
    db = get_db()
    predictions = db.execute(
        '''SELECT p.*, u.full_name as patient_name, d.full_name as doctor_name 
           FROM predictions p 
           JOIN users u ON p.patient_id = u.id 
           LEFT JOIN users d ON p.doctor_id = d.id 
           ORDER BY p.created_at DESC'''
    ).fetchall()
    db.close()
    return render_template('admin/predictions.html', predictions=predictions)

@app.route("/admin/records")
@login_required
@role_required('admin')
def admin_records():
    db = get_db()
    records = db.execute(
        '''SELECT r.*, u.full_name as patient_name, d.full_name as doctor_name 
           FROM medical_records r 
           JOIN users u ON r.patient_id = u.id 
           LEFT JOIN users d ON r.doctor_id = d.id 
           ORDER BY r.created_at DESC'''
    ).fetchall()
    db.close()
    return render_template('admin/records.html', records=records)

# =========================
# DOCTOR DASHBOARD
# =========================
@app.route("/doctor/dashboard")
@login_required
@role_required('doctor')
def doctor_dashboard():
    db = get_db()
    
    # Get doctor info
    doctor = db.execute(
        'SELECT * FROM doctors WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()
    
    # Get statistics
    total_patients = db.execute(
        'SELECT COUNT(DISTINCT patient_id) as count FROM medical_records WHERE doctor_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    total_records = db.execute(
        'SELECT COUNT(*) as count FROM medical_records WHERE doctor_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    total_predictions = db.execute(
        'SELECT COUNT(*) as count FROM predictions WHERE doctor_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    # Recent patients
    recent_patients = db.execute(
        '''SELECT DISTINCT u.* 
           FROM medical_records r 
           JOIN users u ON r.patient_id = u.id 
           WHERE r.doctor_id = ? 
           ORDER BY r.created_at DESC LIMIT 5''',
        (session['user_id'],)
    ).fetchall()
    
    db.close()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         total_patients=total_patients,
                         total_records=total_records,
                         total_predictions=total_predictions,
                         recent_patients=recent_patients)

@app.route("/doctor/profile")
@login_required
@role_required('doctor')
def doctor_profile():
    db = get_db()
    doctor = db.execute(
        '''SELECT d.*, u.full_name, u.email, u.phone, u.username 
           FROM doctors d 
           JOIN users u ON d.user_id = u.id 
           WHERE d.user_id = ?''',
        (session['user_id'],)
    ).fetchone()
    db.close()
    return render_template('doctor/profile.html', doctor=doctor)

@app.route("/doctor/patients")
@login_required
@role_required('doctor')
def doctor_patients():
    db = get_db()
    patients = db.execute(
        '''SELECT DISTINCT u.* 
           FROM medical_records r 
           JOIN users u ON r.patient_id = u.id 
           WHERE r.doctor_id = ? 
           ORDER BY u.full_name''',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('doctor/patients.html', patients=patients)

@app.route("/doctor/add_record", methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def doctor_add_record():
    db = get_db()
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        symptoms = request.form.get('symptoms')
        disease = request.form.get('disease')
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        
        db.execute(
            '''INSERT INTO medical_records 
               (patient_id, doctor_id, symptoms, disease, diagnosis, prescription, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (patient_id, session['user_id'], symptoms, disease, diagnosis, prescription, notes)
        )
        db.commit()
        db.close()
        
        flash('Medical record added successfully', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    patients = db.execute(
        'SELECT * FROM users WHERE role = "patient" ORDER BY full_name'
    ).fetchall()
    db.close()
    
    return render_template('doctor/add_record.html', patients=patients)

@app.route("/doctor/predictions")
@login_required
@role_required('doctor')
def doctor_predictions():
    db = get_db()
    predictions = db.execute(
        '''SELECT p.*, u.full_name as patient_name 
           FROM predictions p 
           JOIN users u ON p.patient_id = u.id 
           WHERE p.doctor_id = ? 
           ORDER BY p.created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('doctor/predictions.html', predictions=predictions)

@app.route("/doctor/history")
@login_required
@role_required('doctor')
def doctor_history():
    db = get_db()
    records = db.execute(
        '''SELECT r.*, u.full_name as patient_name 
           FROM medical_records r 
           JOIN users u ON r.patient_id = u.id 
           WHERE r.doctor_id = ? 
           ORDER BY r.created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('doctor/history.html', records=records)

# =========================
# PATIENT DASHBOARD
# =========================
@app.route("/patient/dashboard")
@login_required
@role_required('patient')
def patient_dashboard():
    db = get_db()
    
    # Get patient stats
    total_records = db.execute(
        'SELECT COUNT(*) as count FROM medical_records WHERE patient_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    total_predictions = db.execute(
        'SELECT COUNT(*) as count FROM predictions WHERE patient_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    # Recent records
    recent_records = db.execute(
        '''SELECT r.*, u.full_name as doctor_name 
           FROM medical_records r 
           JOIN users u ON r.doctor_id = u.id 
           WHERE r.patient_id = ? 
           ORDER BY r.created_at DESC LIMIT 5''',
        (session['user_id'],)
    ).fetchall()
    
    # Recent predictions
    recent_predictions = db.execute(
        '''SELECT p.*, u.full_name as doctor_name 
           FROM predictions p 
           LEFT JOIN users u ON p.doctor_id = u.id 
           WHERE p.patient_id = ? 
           ORDER BY p.created_at DESC LIMIT 5''',
        (session['user_id'],)
    ).fetchall()
    
    db.close()
    
    return render_template('patient/dashboard.html',
                         total_records=total_records,
                         total_predictions=total_predictions,
                         recent_records=recent_records,
                         recent_predictions=recent_predictions)

@app.route("/patient/profile")
@login_required
@role_required('patient')
def patient_profile():
    db = get_db()
    patient = db.execute(
        'SELECT * FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    
    # Get additional stats
    total_records = db.execute(
        'SELECT COUNT(*) as count FROM medical_records WHERE patient_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    total_predictions = db.execute(
        'SELECT COUNT(*) as count FROM predictions WHERE patient_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    db.close()
    
    return render_template('patient/profile.html', 
                         patient=patient,
                         total_records=total_records,
                         total_predictions=total_predictions)

@app.route("/patient/predict", methods=['GET', 'POST'])
@login_required
@role_required('patient')
def patient_predict():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        
        if not symptoms or len(symptoms) < 10:
            flash('Please provide detailed symptoms (at least 10 characters)', 'error')
            return render_template('patient/predict.html')
        
        # Here you would integrate with your AI model
        # For now, we'll simulate a prediction
        import random
        
        diseases = ['Cold', 'Flu', 'COVID-19', 'Pneumonia', 'Allergy', 'Bronchitis', 'Asthma']
        disease = random.choice(diseases)
        confidence = random.uniform(0.7, 0.95)
        risk_levels = ['Low', 'Medium', 'High']
        risk = random.choices(risk_levels, weights=[0.5, 0.3, 0.2])[0]
        
        recommendations = {
            'Low': 'Monitor symptoms at home. Get plenty of rest and stay hydrated.',
            'Medium': 'Schedule a doctor\'s appointment for proper evaluation.',
            'High': 'Seek immediate medical attention. Visit the nearest emergency room.'
        }
        
        db = get_db()
        db.execute(
            '''INSERT INTO predictions 
               (patient_id, doctor_id, symptoms, disease, confidence, risk, recommendation) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (session['user_id'], None, symptoms, disease, confidence, risk, recommendations[risk])
        )
        db.commit()
        db.close()
        
        flash(f'Prediction completed! Predicted disease: {disease}', 'success')
        return redirect(url_for('patient_dashboard'))
    
    return render_template('patient/predict.html')

@app.route("/patient/records")
@login_required
@role_required('patient')
def patient_records():
    db = get_db()
    records = db.execute(
        '''SELECT r.*, u.full_name as doctor_name 
           FROM medical_records r 
           JOIN users u ON r.doctor_id = u.id 
           WHERE r.patient_id = ? 
           ORDER BY r.created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('patient/records.html', records=records)

@app.route("/patient/history")
@login_required
@role_required('patient')
def patient_history():
    db = get_db()
    predictions = db.execute(
        '''SELECT p.*, u.full_name as doctor_name 
           FROM predictions p 
           LEFT JOIN users u ON p.doctor_id = u.id 
           WHERE p.patient_id = ? 
           ORDER BY p.created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('patient/history.html', predictions=predictions)

# =========================
# API ROUTES FOR CRUD OPERATIONS
# =========================
@app.route("/api/user/<int:user_id>", methods=['DELETE'])
@login_required
@role_required('admin')
def delete_user(user_id):
    db = get_db()
    try:
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
        return jsonify({"success": True, "message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        db.close()

@app.route("/api/record/<int:record_id>", methods=['DELETE'])
@login_required
def delete_record(record_id):
    db = get_db()
    try:
        # Check if user has permission
        record = db.execute('SELECT * FROM medical_records WHERE id = ?', (record_id,)).fetchone()
        if not record:
            return jsonify({"success": False, "message": "Record not found"})
        
        # Allow deletion by admin, doctor who created it, or patient who owns it
        if (session['role'] != 'admin' and 
            session['user_id'] != record['doctor_id'] and 
            session['user_id'] != record['patient_id']):
            return jsonify({"success": False, "message": "Permission denied"})
        
        db.execute('DELETE FROM medical_records WHERE id = ?', (record_id,))
        db.commit()
        return jsonify({"success": True, "message": "Record deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        db.close()

@app.route("/api/prediction/<int:prediction_id>", methods=['GET'])
@login_required
def get_prediction(prediction_id):
    db = get_db()
    try:
        prediction = db.execute(
            '''SELECT p.*, u.full_name as patient_name, d.full_name as doctor_name 
               FROM predictions p 
               JOIN users u ON p.patient_id = u.id 
               LEFT JOIN users d ON p.doctor_id = d.id 
               WHERE p.id = ?''',
            (prediction_id,)
        ).fetchone()
        
        if not prediction:
            return jsonify({"success": False, "message": "Prediction not found"})
        
        # Check permission
        if (session['role'] not in ['admin'] and 
            session['user_id'] != prediction['patient_id'] and 
            session['user_id'] != prediction['doctor_id']):
            return jsonify({"success": False, "message": "Permission denied"})
        
        return jsonify({"success": True, "prediction": dict(prediction)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        db.close()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)