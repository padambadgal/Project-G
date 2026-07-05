# patient/patient.py
from database.database import Database
from utils.validation import Validator


class Patient:
    def __init__(self):
        self.db = Database()
        self.db.connect()

    def get_patient_by_id(self, user_id):
        query = """
        SELECT * FROM users 
        WHERE id = ? AND role = 'patient'
        """
        return self.db.fetch_one(query, (user_id,))

    def get_patient_by_username(self, username):
        query = """
        SELECT * FROM users 
        WHERE username = ? AND role = 'patient'
        """
        return self.db.fetch_one(query, (username,))

    def get_all_patients(self):
        query = """
        SELECT * FROM users 
        WHERE role = 'patient' 
        ORDER BY created_at DESC
        """
        return self.db.fetch_all(query)

    def search_patients(self, keyword):
        keyword = f"%{keyword}%"
        query = """
        SELECT * FROM users 
        WHERE role = 'patient'
        AND (username LIKE ? OR full_name LIKE ? OR phone LIKE ?)
        ORDER BY created_at DESC
        """
        return self.db.fetch_all(query, (keyword, keyword, keyword))

    def update_patient(self, user_id, **kwargs):
        patient = self.get_patient_by_id(user_id)
        if not patient:
            return False, "Patient not found"

        updates = []
        params = []

        field_map = {
            'full_name': 'full_name',
            'age': 'age',
            'gender': 'gender',
            'phone': 'phone',
            'address': 'address',
            'medical_history': 'medical_history',
            'emergency_contact': 'emergency_contact',
            'blood_group': 'blood_group'
        }

        for key, db_field in field_map.items():
            if key in kwargs and kwargs[key] is not None:
                updates.append(f"{db_field}=?")
                params.append(kwargs[key])

        if not updates:
            return False, "Nothing to update"

        params.append(user_id)
        query = f"""
        UPDATE users
        SET {", ".join(updates)}
        WHERE id = ? AND role = 'patient'
        """

        try:
            self.db.execute_query(query, params)
            return True, "Patient updated successfully"
        except Exception as e:
            return False, str(e)

    def delete_patient(self, user_id):
        patient = self.get_patient_by_id(user_id)
        if not patient:
            return False, "Patient not found"

        try:
            self.db.execute_query(
                "DELETE FROM users WHERE id = ? AND role = 'patient'",
                (user_id,)
            )
            return True, "Patient deleted successfully"
        except Exception as e:
            return False, str(e)

    def get_patient_count(self):
        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM users WHERE role = 'patient'"
        )
        return result[0] if result else 0

    def close(self):
        self.db.close()