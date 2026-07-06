# admin/admin.py
from database.database import Database
from authentication.login import Authentication


class Admin:
    def __init__(self):
        self.db = Database()
        self.db.connect()
        self.auth = Authentication()

    # ==========================================================
    # USER MANAGEMENT
    # ==========================================================

    def get_all_users(self):
        query = """
        SELECT * FROM users
        ORDER BY created_at DESC
        """
        return self.db.fetch_all(query)

    def get_users_by_role(self, role):
        query = "SELECT * FROM users WHERE role = ? ORDER BY created_at DESC"
        return self.db.fetch_all(query, (role,))

    def get_all_doctors(self):
        query = """
        SELECT u.*, d.specialization, d.years_experience
        FROM users u
        LEFT JOIN doctor_profile d ON u.id = d.user_id
        WHERE u.role = 'doctor'
        """
        return self.db.fetch_all(query)

    def get_all_patients(self):
        query = """
        SELECT u.*, p.blood_group, p.medical_history
        FROM users u
        LEFT JOIN patient_profile p ON u.id = p.user_id
        WHERE u.role = 'patient'
        """
        return self.db.fetch_all(query)

    def create_user(self, username, password, role, full_name, **kwargs):
        return self.auth.register_user(
            username=username,
            password=password,
            role=role,
            full_name=full_name,
            **kwargs
        )

    def delete_user(self, user_id):
        try:
            self.db.execute_query(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            return True, "User deleted successfully"
        except Exception as e:
            return False, str(e)

    def update_user_role(self, username, new_role):
        if username == "admin":
            return False, "Cannot change admin role"
        if new_role not in ['admin', 'doctor', 'patient']:
            return False, "Invalid role"

        try:
            self.db.execute_query(
                "UPDATE users SET role = ? WHERE username = ?",
                (new_role, username)
            )
            return True, f"User role updated to {new_role}"
        except Exception as e:
            return False, str(e)

    # ==========================================================
    # PATIENT STATISTICS
    # ==========================================================

    def get_patient_statistics(self):
        total = self.db.fetch_one(
            "SELECT COUNT(*) FROM users WHERE role = 'patient'"
        )[0]

        gender_stats = self.db.fetch_all("""
            SELECT gender, COUNT(*) as count 
            FROM users 
            WHERE role = 'patient' AND gender IS NOT NULL
            GROUP BY gender
        """)

        age_stats = self.db.fetch_all("""
            SELECT 
                CASE 
                    WHEN age < 18 THEN 'Minor (<18)'
                    WHEN age BETWEEN 18 AND 60 THEN 'Adult (18-60)'
                    WHEN age > 60 THEN 'Senior (>60)'
                    ELSE 'Unknown'
                END as age_group,
                COUNT(*) as count
            FROM users
            WHERE role = 'patient'
            GROUP BY age_group
        """)

        return {
            'total': total,
            'gender_distribution': gender_stats,
            'age_distribution': age_stats
        }

    # ==========================================================
    # SYSTEM STATISTICS
    # ==========================================================

    def get_system_statistics(self):
        user_stats = self.db.fetch_all(
            "SELECT role, COUNT(*) as count FROM users GROUP BY role"
        )

        patient_count = self.db.fetch_one(
            "SELECT COUNT(*) FROM users WHERE role = 'patient'"
        )[0]
        doctor_count = self.db.fetch_one(
            "SELECT COUNT(*) FROM users WHERE role = 'doctor'"
        )[0]
        prediction_count = self.db.fetch_one(
            "SELECT COUNT(*) FROM predictions"
        )[0]

        return {
            "user_stats": [dict(row) for row in user_stats],
            "total_patients": patient_count,
            "total_doctors": doctor_count,
            "total_predictions": prediction_count,
        }

    def close(self):
        self.auth.close()
        self.db.close()