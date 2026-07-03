# patient/patient.py
from database.database import Database
from utils.helper import generate_id
from utils.validation import Validator

class Patient:
    def __init__(self):
        self.db = Database()
        self.db.connect()
    
    def add_patient(self, full_name, age, gender, contact, address, medical_history=None):
        """Add a new patient"""
        # Validate inputs
        if not full_name:
            return False, "Full name is required"
        
        if not Validator.validate_age(age):
            return False, "Invalid age"
        
        if contact and not Validator.validate_phone(contact):
            return False, "Invalid contact number"
        
        # Generate unique patient ID
        patient_id = generate_id("P")
        
        query = """INSERT INTO patients 
                   (patient_id, full_name, age, gender, contact, address, medical_history) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""
        
        try:
            self.db.execute_query(query, (patient_id, full_name, age, gender, contact, address, medical_history))
            return True, patient_id
        except Exception as e:
            return False, str(e)
    
    def get_all_patients(self):
        """Get all patients"""
        query = "SELECT * FROM patients ORDER BY created_at DESC"
        return self.db.fetch_all(query)
    
    def get_patient_by_id(self, patient_id):
        """Get patient by ID"""
        query = "SELECT * FROM patients WHERE patient_id = ?"
        return self.db.fetch_one(query, (patient_id,))
    
    def search_patients(self, search_term):
        """Search patients by name or ID"""
        query = """SELECT * FROM patients 
                   WHERE full_name LIKE ? OR patient_id LIKE ? OR contact LIKE ?
                   ORDER BY created_at DESC"""
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))
    
    def update_patient(self, patient_id, full_name=None, age=None, gender=None, 
                      contact=None, address=None, medical_history=None):
        """Update patient details"""
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = ?")
            params.append(full_name)
        if age is not None:
            if not Validator.validate_age(age):
                return False, "Invalid age"
            updates.append("age = ?")
            params.append(age)
        if gender:
            updates.append("gender = ?")
            params.append(gender)
        if contact:
            if not Validator.validate_phone(contact):
                return False, "Invalid contact number"
            updates.append("contact = ?")
            params.append(contact)
        if address:
            updates.append("address = ?")
            params.append(address)
        if medical_history is not None:
            updates.append("medical_history = ?")
            params.append(medical_history)
        
        if not updates:
            return False, "No updates provided"
        
        params.append(patient_id)
        query = f"UPDATE patients SET {', '.join(updates)} WHERE patient_id = ?"
        
        try:
            self.db.execute_query(query, params)
            return True, "Patient updated successfully"
        except Exception as e:
            return False, str(e)
    
    def delete_patient(self, patient_id):
        """Delete a patient"""
        query = "DELETE FROM patients WHERE patient_id = ?"
        try:
            self.db.execute_query(query, (patient_id,))
            return True, "Patient deleted successfully"
        except Exception as e:
            return False, str(e)
    
    def get_patient_count(self):
        """Get total number of patients"""
        query = "SELECT COUNT(*) FROM patients"
        result = self.db.fetch_one(query)
        return result[0] if result else 0
    
    def close(self):
        self.db.close()