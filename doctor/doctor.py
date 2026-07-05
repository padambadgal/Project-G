# doctor/doctor.py
from database.database import Database
from utils.validation import Validator


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
        SELECT * FROM users 
        WHERE username = ? AND role = 'doctor'
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

    def close(self):
        self.db.close()