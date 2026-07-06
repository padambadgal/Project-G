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
        SELECT 
            u.id,
            u.username,
            u.full_name,
            u.email,
            u.phone,
            u.gender,
            u.age,
            u.created_at,

            p.address,
            p.medical_history,
            p.emergency_contact,
            p.blood_group

        FROM users u
        LEFT JOIN patient_profile p ON u.id = p.user_id
        WHERE u.username = ? AND u.role = 'patient'
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

    def get_medical_records(self, patient_id):
        query = """
        SELECT 
            mr.id,
            mr.symptoms,
            mr.disease,
            mr.diagnosis,
            mr.prescription,
            mr.notes,
            mr.visit_date,

            u.full_name AS doctor_name

        FROM medical_records mr
        LEFT JOIN users u ON mr.doctor_id = u.id
        WHERE mr.patient_id = ?
        ORDER BY mr.visit_date DESC
        """

        return self.db.fetch_all(query, (patient_id,))
        
    def get_predictions(self, patient_id):
        query = """
        SELECT 
            p.*,
            u.full_name AS doctor_name
        FROM predictions p
        LEFT JOIN users u ON p.doctor_id = u.id
        WHERE p.patient_id = ?
        ORDER BY p.predicted_at DESC
        """

        return self.db.fetch_all(query, (patient_id,))

    def close(self):
        self.db.close()