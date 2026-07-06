import sqlite3
import hashlib

class Authentication:
    def __init__(self):
        self.db_path = 'database/hospital.db'
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_db(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db
    
    def login(self, username, password):
        db = self.get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, self.hash_password(password))
        ).fetchone()
        db.close()
        
        if user:
            return dict(user)
        return None
    
    def register_user(self, username, password, role, full_name, **kwargs):
        db = self.get_db()
        
        try:
            # Check if username exists
            existing = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if existing:
                db.close()
                return False, "Username already exists"
            
            # For doctor role, validate specialization
            if role == 'doctor':
                if not kwargs.get('specialization'):
                    db.close()
                    return False, "Specialization is required for doctors"
            
            # Insert user
            cursor = db.execute(
                '''INSERT INTO users 
                   (username, password, full_name, role, email, phone, gender, age, 
                    address, medical_history, emergency_contact, blood_group) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (username, self.hash_password(password), full_name, role, 
                 kwargs.get('email'), kwargs.get('phone'),
                 kwargs.get('gender'), kwargs.get('age'),
                 kwargs.get('address'), kwargs.get('medical_history'),
                 kwargs.get('emergency_contact'), kwargs.get('blood_group'))
            )
            user_id = cursor.lastrowid
            
            # Insert doctor details if role is doctor
            if role == 'doctor':
                db.execute(
                    '''INSERT INTO doctors 
                       (user_id, specialization, years_experience, qualification, 
                        hospital_name, consultation_fee, bio, available_days, available_time) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, 
                     kwargs.get('specialization'),
                     int(kwargs.get('years_experience', 0) or 0),
                     kwargs.get('qualification', ''),
                     kwargs.get('hospital_name', ''),
                     float(kwargs.get('consultation_fee', 0) or 0),
                     kwargs.get('bio', ''),
                     kwargs.get('available_days', ''),
                     kwargs.get('available_time', ''))
                )
            
            db.commit()
            db.close()
            return True, "User registered successfully"
            
        except Exception as e:
            db.rollback()
            db.close()
            return False, f"Registration failed: {str(e)}"

    def close(self):
        self.db.close()