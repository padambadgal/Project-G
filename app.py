# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
import json
from datetime import datetime

# Import modules
from authentication.login import Authentication
from admin.admin import Admin
from doctor.doctor import Doctor
from patient.patient import Patient
from ai.predict import DiseasePredictor
from ai.train_model import ModelTrainer
from reports.reports import Reports
from database.database import Database
from config.settings import APP_NAME, VERSION
from utils.helper import calculate_risk_level, generate_recommendation

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Initialize components
auth = Authentication()
admin = Admin()
doctor = Doctor()
patient = Patient()
predictor = DiseasePredictor()
reports = Reports()

# ============================================
# DECORATORS
# ============================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                flash('Please login first.', 'warning')
                return redirect(url_for('login'))
            if session['role'] not in allowed_roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================
# PUBLIC ROUTES
# ============================================

@app.route('/')
def index():
    return render_template('index.html', app_name=APP_NAME, version=VERSION)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = auth.login(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            session['email'] = user.get('email')
            session['phone'] = user.get('phone')
            
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif user['role'] == 'patient':
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', app_name=APP_NAME)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', '').strip().lower()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender', '').strip()
        age = request.form.get('age', '').strip()
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', app_name=APP_NAME)
        
        # Build kwargs based on role
        kwargs = {
            'email': email if email else None,
            'phone': phone if phone else None,
            'gender': gender if gender else None,
            'age': age if age else None
        }
        
        # Add role-specific fields
        if role == 'doctor':
            kwargs['specialization'] = request.form.get('specialization', '').strip()
            kwargs['years_experience'] = request.form.get('years_experience', '').strip()
        elif role == 'patient':
            kwargs['medical_history'] = request.form.get('medical_history', '').strip()
            kwargs['emergency_contact'] = request.form.get('emergency_contact', '').strip()
            kwargs['blood_group'] = request.form.get('blood_group', '').strip()
        
        success, message = auth.register_user(
            username=username,
            password=password,
            role=role,
            full_name=full_name,
            **kwargs
        )
        
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')
    
    return render_template('register.html', app_name=APP_NAME)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    elif role == 'patient':
        return redirect(url_for('patient_dashboard'))
    return redirect(url_for('logout'))

# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/admin/dashboard')
@login_required
@role_required(['admin'])
def admin_dashboard():
    stats = admin.get_system_statistics()
    return render_template('admin/dashboard.html', 
                         app_name=APP_NAME, user=session, stats=stats)

@app.route('/admin/users')
@login_required
@role_required(['admin'])
def admin_users():
    users_data = admin.get_all_users()
    users_list = [dict(row) for row in users_data] if users_data else []
    return render_template('admin/users.html', 
                         app_name=APP_NAME, user=session, users=users_list)

@app.route('/admin/users/delete/<username>')
@login_required
@role_required(['admin'])
def admin_delete_user(username):
    if username == 'admin':
        flash('Cannot delete default admin user.', 'danger')
    else:
        success, message = admin.delete_user(username)
        if success:
            flash('User deleted successfully.', 'success')
        else:
            flash(f'Error: {message}', 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/doctors')
@login_required
@role_required(['admin'])
def admin_doctors():
    doctors_data = admin.get_doctors()
    doctors_list = [dict(row) for row in doctors_data] if doctors_data else []
    return render_template('admin/doctors.html', 
                         app_name=APP_NAME, user=session, doctors=doctors_list)

@app.route('/admin/patients')
@login_required
@role_required(['admin'])
def admin_patients():
    patients_data = admin.get_patients()
    patients_list = [dict(row) for row in patients_data] if patients_data else []
    stats = admin.get_patient_statistics()
    return render_template('admin/patients.html', 
                         app_name=APP_NAME, user=session, patients=patients_list, stats=stats)

@app.route('/admin/predictions')
@login_required
@role_required(['admin'])
def admin_predictions():
    predictions_data = reports.get_prediction_history(365)
    predictions_list = [dict(row) for row in predictions_data] if predictions_data else []
    return render_template('admin/predictions.html', 
                         app_name=APP_NAME, user=session, predictions=predictions_list)

@app.route('/admin/train-model', methods=['POST'])
@login_required
@role_required(['admin'])
def admin_train_model():
    try:
        trainer = ModelTrainer()
        trainer.load_and_prepare_data()
        trainer.train_model()
        trainer.save_model()
        accuracy = trainer.evaluate_model()
        flash(f'Model trained successfully! Accuracy: {accuracy:.2%}', 'success')
    except Exception as e:
        flash(f'Error training model: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))

# ============================================
# DOCTOR ROUTES
# ============================================

@app.route('/doctor/dashboard')
@login_required
@role_required(['doctor'])
def doctor_dashboard():
    doctor_data = doctor.get_doctor_by_username(session['username'])
    doctor_id = doctor_data['id'] if doctor_data else None
    
    stats = {'total_predictions': 0, 'avg_confidence': 0, 'unique_patients': 0}
    if doctor_id:
        stats = reports.get_doctor_statistics(doctor_id)
    
    return render_template('doctor/dashboard.html', 
                         app_name=APP_NAME, user=session, stats=stats)

@app.route('/doctor/predict', methods=['GET', 'POST'])
@login_required
@role_required(['doctor'])
def doctor_predict():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', '').strip()
        patient_data = patient.get_patient_by_username(patient_id)
        
        if not patient_data:
            flash('Patient not found. Please enter a valid Patient Username.', 'danger')
            return render_template('doctor/predict.html', app_name=APP_NAME, user=session)
        
        symptoms = {}
        required_symptoms = predictor.get_symptoms_required()
        
        for symptom in required_symptoms:
            value = request.form.get(symptom, '0')
            symptoms[symptom] = int(value)
        
        result = predictor.predict_disease(symptoms)
        
        if result:
            risk_level = calculate_risk_level(result['confidence'])
            recommendation = generate_recommendation(result['disease'], risk_level)
            
            doctor_data = doctor.get_doctor_by_username(session['username'])
            doctor_id = doctor_data['id'] if doctor_data else None
            
            symptoms_str = ', '.join([f"{k.replace('_', ' ')}: {v}" for k, v in symptoms.items() if v == 1])
            if not symptoms_str:
                symptoms_str = "No symptoms reported"
            
            db = Database()
            db.connect()
            query = """INSERT INTO predictions 
                       (patient_id, doctor_id, symptoms, predicted_disease, confidence, risk_level, recommendation) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)"""
            db.execute_query(query, (
                patient_data['id'],
                doctor_id,
                symptoms_str,
                result['disease'],
                result['confidence'],
                risk_level,
                recommendation
            ))
            db.close()
            
            return render_template('doctor/predict_result.html',
                                 app_name=APP_NAME,
                                 user=session,
                                 patient=dict(patient_data),
                                 result=result,
                                 risk_level=risk_level,
                                 recommendation=recommendation)
        else:
            flash('Prediction failed. Please ensure the model is trained.', 'danger')
    
    patients_data = patient.get_all_patients()
    patients_list = [dict(row) for row in patients_data] if patients_data else []
    required_symptoms = predictor.get_symptoms_required()
    
    return render_template('doctor/predict.html',
                         app_name=APP_NAME,
                         user=session,
                         patients=patients_list,
                         symptoms=required_symptoms)

@app.route('/doctor/predictions')
@login_required
@role_required(['doctor'])
def doctor_predictions():
    doctor_data = doctor.get_doctor_by_username(session['username'])
    doctor_id = doctor_data['id'] if doctor_data else None
    
    predictions_list = []
    if doctor_id:
        predictions_data = reports.get_doctor_predictions(doctor_id)
        predictions_list = [dict(row) for row in predictions_data] if predictions_data else []
    
    return render_template('doctor/predictions.html',
                         app_name=APP_NAME,
                         user=session,
                         predictions=predictions_list)

@app.route('/doctor/patients')
@login_required
@role_required(['doctor'])
def doctor_patients():
    patients_data = patient.get_all_patients()
    patients_list = [dict(row) for row in patients_data] if patients_data else []
    return render_template('doctor/patients.html',
                         app_name=APP_NAME,
                         user=session,
                         patients=patients_list)

# ============================================
# PATIENT ROUTES
# ============================================

@app.route('/patient/dashboard')
@login_required
@role_required(['patient'])
def patient_dashboard():
    patient_data = patient.get_patient_by_username(session['username'])
    return render_template('patient/dashboard.html',
                         app_name=APP_NAME,
                         user=session,
                         patient=dict(patient_data) if patient_data else None)

@app.route('/patient/profile')
@login_required
@role_required(['patient'])
def patient_profile():
    patient_data = patient.get_patient_by_username(session['username'])
    return render_template('patient/profile.html',
                         app_name=APP_NAME,
                         user=session,
                         patient=dict(patient_data) if patient_data else None)

@app.route('/patient/profile/update', methods=['POST'])
@login_required
@role_required(['patient'])
def patient_update_profile():
    patient_data = patient.get_patient_by_username(session['username'])
    if not patient_data:
        flash('Profile not found.', 'danger')
        return redirect(url_for('patient_dashboard'))
    
    patient_id = patient_data['id']
    full_name = request.form.get('full_name', '').strip()
    age = request.form.get('age', '').strip()
    gender = request.form.get('gender', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    medical_history = request.form.get('medical_history', '').strip()
    
    success, message = patient.update_patient(
        patient_id,
        full_name=full_name if full_name else None,
        age=age if age else None,
        gender=gender if gender else None,
        phone=phone if phone else None,
        address=address if address else None,
        medical_history=medical_history if medical_history else None
    )
    
    if success:
        flash('Profile updated successfully!', 'success')
    else:
        flash(f'Error: {message}', 'danger')
    
    return redirect(url_for('patient_profile'))

@app.route('/patient/predictions')
@login_required
@role_required(['patient'])
def patient_predictions():
    patient_data = patient.get_patient_by_username(session['username'])
    predictions_list = []
    if patient_data:
        predictions_data = reports.get_patient_predictions(patient_data['id'])
        predictions_list = [dict(row) for row in predictions_data] if predictions_data else []
    
    return render_template('patient/predictions.html',
                         app_name=APP_NAME,
                         user=session,
                         predictions=predictions_list)

# ============================================
# API ROUTES
# ============================================

@app.route('/api/patient/<int:patient_id>')
@login_required
def api_get_patient(patient_id):
    patient_data = patient.get_patient_by_id(patient_id)
    if patient_data:
        return jsonify({'success': True, 'patient': dict(patient_data)})
    return jsonify({'success': False, 'message': 'Patient not found'})

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', app_name=APP_NAME), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', app_name=APP_NAME), 500

# ============================================
# RUN APP
# ============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)