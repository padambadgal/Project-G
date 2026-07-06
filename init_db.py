# init_db.py
import sqlite3
import os
import hashlib

def init_database():
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)

    conn = sqlite3.connect('database/hospital.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist (for clean setup)
    cursor.execute('DROP TABLE IF EXISTS predictions')
    cursor.execute('DROP TABLE IF EXISTS medical_records')
    cursor.execute('DROP TABLE IF EXISTS doctors')
    cursor.execute('DROP TABLE IF EXISTS users')

    # Users table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient')),
        email TEXT,
        phone TEXT,
        gender TEXT,
        age INTEGER,
        address TEXT,
        medical_history TEXT,
        emergency_contact TEXT,
        blood_group TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Doctors table
    cursor.execute('''
    CREATE TABLE doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        specialization TEXT NOT NULL,
        years_experience INTEGER DEFAULT 0,
        qualification TEXT,
        hospital_name TEXT,
        consultation_fee REAL DEFAULT 0,
        bio TEXT,
        available_days TEXT,
        available_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # Medical records table - with all required columns
    cursor.execute('''
    CREATE TABLE medical_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        symptoms TEXT NOT NULL,
        disease TEXT NOT NULL,
        diagnosis TEXT NOT NULL,
        prescription TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id),
        FOREIGN KEY (doctor_id) REFERENCES users(id)
    )
    ''')

    # Predictions table
    cursor.execute('''
    CREATE TABLE predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER,
        symptoms TEXT NOT NULL,
        disease TEXT NOT NULL,
        confidence REAL NOT NULL,
        risk TEXT NOT NULL,
        recommendation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES users(id),
        FOREIGN KEY (doctor_id) REFERENCES users(id)
    )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_medical_records_patient ON medical_records(patient_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_medical_records_doctor ON medical_records(doctor_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_patient ON predictions(patient_id)')

    # Create a default admin user
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, full_name, role, email)
    VALUES (?, ?, ?, ?, ?)
    ''', ('admin', admin_password, 'System Admin', 'admin', 'admin@hospital.com'))

    # Create a default doctor user (for testing)
    doctor_password = hashlib.sha256('doctor123'.encode()).hexdigest()
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, full_name, role, email)
    VALUES (?, ?, ?, ?, ?)
    ''', ('doctor', doctor_password, 'Dr. John Smith', 'doctor', 'doctor@hospital.com'))

    # Get the doctor user_id
    cursor.execute('SELECT id FROM users WHERE username = ?', ('doctor',))
    doctor_user = cursor.fetchone()
    if doctor_user:
        cursor.execute('''
        INSERT OR IGNORE INTO doctors (user_id, specialization, years_experience, qualification,
                        hospital_name, consultation_fee, bio, available_days, available_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (doctor_user[0], 'Cardiologist', 10, 'MD, PhD', 'City Hospital', 100.00,
              'Experienced cardiologist with 10 years of practice', 'Mon-Fri', '9:00 AM - 5:00 PM'))

    # Create a default patient user (for testing)
    patient_password = hashlib.sha256('patient123'.encode()).hexdigest()
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, full_name, role, email)
    VALUES (?, ?, ?, ?, ?)
    ''', ('patient', patient_password, 'John Doe', 'patient', 'patient@email.com'))

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")
    print("✅ Default admin created: username='admin', password='admin123'")
    print("✅ Default doctor created: username='doctor', password='doctor123'")
    print("✅ Default patient created: username='patient', password='patient123'")

if __name__ == "__main__":
    init_database()