# doctor/doctor.py
from database.database import Database
from utils.validation import Validator
from utils.ai_engine import AIEngine

class Doctor:
    def __init__(self):
        self.db = Database()
        self.db.connect()

    def get_doctor_by_id(self, user_id):
        query = """
        SELECT * FROM users 
        WHERE id = ? AND role = 'doctor'
        """
        return self.db.fetch_one(query, (user_id,))

    def get_doctor_by_username(self, username):
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

            d.specialization,
            d.years_experience,
            d.qualification,
            d.hospital_name,
            d.consultation_fee,
            d.bio,
            d.available_days,
            d.available_time

        FROM users u
        LEFT JOIN doctor_profile d ON u.id = d.user_id
        WHERE u.username = ? AND u.role = 'doctor'
        """
        return self.db.fetch_one(query, (username,))

    def get_all_doctors(self):
        query = """
        SELECT * FROM users 
        WHERE role = 'doctor' 
        ORDER BY created_at DESC
        """
        return self.db.fetch_all(query)

    def search_doctors(self, keyword):
        keyword = f"%{keyword}%"
        query = """
        SELECT * FROM users 
        WHERE role = 'doctor'
        AND (username LIKE ? OR full_name LIKE ? OR specialization LIKE ? OR phone LIKE ?)
        ORDER BY created_at DESC
        """
        return self.db.fetch_all(query, (keyword, keyword, keyword, keyword))

    def update_doctor(self, user_id, **kwargs):
        doctor = self.get_doctor_by_id(user_id)
        if not doctor:
            return False, "Doctor not found"

        updates = []
        params = []

        field_map = {
            'full_name': 'full_name',
            'specialization': 'specialization',
            'phone': 'phone',
            'email': 'email',
            'years_experience': 'years_experience',
            'gender': 'gender',
            'age': 'age',
            'address': 'address'
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
        WHERE id = ? AND role = 'doctor'
        """

        try:
            self.db.execute_query(query, params)
            return True, "Doctor updated successfully"
        except Exception as e:
            return False, str(e)

    def delete_doctor(self, user_id):
        doctor = self.get_doctor_by_id(user_id)
        if not doctor:
            return False, "Doctor not found"

        try:
            self.db.execute_query(
                "DELETE FROM users WHERE id = ? AND role = 'doctor'",
                (user_id,)
            )
            return True, "Doctor deleted successfully"
        except Exception as e:
            return False, str(e)

    def get_doctor_count(self):
        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM users WHERE role = 'doctor'"
        )
        return result[0] if result else 0

    def add_medical_record(self, patient_id, doctor_id, symptoms, disease, diagnosis, prescription, notes):
        query = """
        INSERT INTO medical_records
        (
            patient_id,
            doctor_id,
            symptoms,
            disease,
            diagnosis,
            prescription,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        try:
            self.db.execute_query(
                query,
                (
                    patient_id,
                    doctor_id,
                    symptoms,
                    disease,
                    diagnosis,
                    prescription,
                    notes
                )
            )
            return True, "Medical record added successfully"

        except Exception as e:
            return False, str(e)
    
    def predict_disease(self, patient_id, doctor_id, symptoms):

        ai = AIEngine()

        result = ai.analyze(symptoms)

        disease = result["disease"]
        risk = result["risk"]
        confidence = result["confidence"]

        recommendation = f"Consult specialist for {disease}"

        query = """
        INSERT INTO predictions
        (
            patient_id,
            doctor_id,
            symptoms,
            predicted_disease,
            confidence,
            risk_level,
            recommendation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.db.execute_query(
            query,
            (
                patient_id,
                doctor_id,
                symptoms,
                disease,
                confidence,
                risk,
                recommendation
            )
        )

        return result
    
    def close(self):
        self.db.close()