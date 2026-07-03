# admin/admin.py
from database.database import Database
from authentication.login import Authentication
from doctor.doctor import Doctor
from patient.patient import Patient
from utils.helper import generate_id

class Admin:
    def __init__(self):
        self.db = Database()
        self.db.connect()
        self.auth = Authentication()
    
    def get_all_users(self):
        """Get all users"""
        query = "SELECT * FROM users ORDER BY created_at DESC"
        return self.db.fetch_all(query)
    
    def create_user(self, username, password, role, full_name, email=None, phone=None):
        """Create a new user"""
        return self.auth.register_user(username, password, role, full_name, email, phone)
    
    def delete_user(self, username):
        """Delete a user"""
        query = "DELETE FROM users WHERE username = ?"
        try:
            self.db.execute_query(query, (username,))
            return True, "User deleted successfully"
        except Exception as e:
            return False, str(e)
    
    def get_system_statistics(self):
        """Get system statistics"""
        # Get user counts
        user_query = "SELECT role, COUNT(*) FROM users GROUP BY role"
        user_stats = self.db.fetch_all(user_query)
        
        # Get patient and doctor counts
        patient_count = "SELECT COUNT(*) FROM patients"
        doctor_count = "SELECT COUNT(*) FROM doctors"
        prediction_count = "SELECT COUNT(*) FROM predictions"
        
        total_patients = self.db.fetch_one(patient_count)[0]
        total_doctors = self.db.fetch_one(doctor_count)[0]
        total_predictions = self.db.fetch_one(prediction_count)[0]
        
        return {
            'user_stats': user_stats,
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_predictions': total_predictions
        }
    
    def close(self):
        self.db.close()
        self.auth.close()