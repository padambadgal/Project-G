# doctor/doctor.py
from database.database import Database
from utils.helper import generate_id
from utils.validation import Validator

class Doctor:
    def __init__(self):
        self.db = Database()
        self.db.connect()
    
    def add_doctor(self, full_name, specialization, contact, email, years_experience):
        """Add a new doctor"""
        # Validate inputs
        if not full_name:
            return False, "Full name is required"
        
        if email and not Validator.validate_email(email):
            return False, "Invalid email address"
        
        if contact and not Validator.validate_phone(contact):
            return False, "Invalid contact number"
        
        try:
            years_experience = int(years_experience)
            if years_experience < 0:
                return False, "Invalid years of experience"
        except:
            return False, "Years of experience must be a number"
        
        # Generate unique doctor ID
        doctor_id = generate_id("D")
        
        query = """INSERT INTO doctors 
                   (doctor_id, full_name, specialization, contact, email, years_experience) 
                   VALUES (?, ?, ?, ?, ?, ?)"""
        
        try:
            self.db.execute_query(query, (doctor_id, full_name, specialization, contact, email, years_experience))
            return True, doctor_id
        except Exception as e:
            return False, str(e)
    
    def get_all_doctors(self):
        """Get all doctors"""
        query = "SELECT * FROM doctors ORDER BY created_at DESC"
        return self.db.fetch_all(query)
    
    def get_doctor_by_id(self, doctor_id):
        """Get doctor by ID"""
        query = "SELECT * FROM doctors WHERE doctor_id = ?"
        return self.db.fetch_one(query, (doctor_id,))
    
    def search_doctors(self, search_term):
        """Search doctors by name, ID, or specialization"""
        query = """SELECT * FROM doctors 
                   WHERE full_name LIKE ? OR doctor_id LIKE ? OR specialization LIKE ?
                   ORDER BY created_at DESC"""
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))
    
    def update_doctor(self, doctor_id, full_name=None, specialization=None, 
                     contact=None, email=None, years_experience=None):
        """Update doctor details"""
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = ?")
            params.append(full_name)
        if specialization:
            updates.append("specialization = ?")
            params.append(specialization)
        if contact:
            if not Validator.validate_phone(contact):
                return False, "Invalid contact number"
            updates.append("contact = ?")
            params.append(contact)
        if email:
            if not Validator.validate_email(email):
                return False, "Invalid email address"
            updates.append("email = ?")
            params.append(email)
        if years_experience is not None:
            try:
                years_experience = int(years_experience)
                if years_experience < 0:
                    return False, "Invalid years of experience"
                updates.append("years_experience = ?")
                params.append(years_experience)
            except:
                return False, "Years of experience must be a number"
        
        if not updates:
            return False, "No updates provided"
        
        params.append(doctor_id)
        query = f"UPDATE doctors SET {', '.join(updates)} WHERE doctor_id = ?"
        
        try:
            self.db.execute_query(query, params)
            return True, "Doctor updated successfully"
        except Exception as e:
            return False, str(e)
    
    def delete_doctor(self, doctor_id):
        """Delete a doctor"""
        query = "DELETE FROM doctors WHERE doctor_id = ?"
        try:
            self.db.execute_query(query, (doctor_id,))
            return True, "Doctor deleted successfully"
        except Exception as e:
            return False, str(e)
    
    def get_doctor_count(self):
        """Get total number of doctors"""
        query = "SELECT COUNT(*) FROM doctors"
        result = self.db.fetch_one(query)
        return result[0] if result else 0
    
    def close(self):
        self.db.close()