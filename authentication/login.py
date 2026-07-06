# authentication/login.py
import hashlib
from database.database import Database
from utils.validation import Validator

class Authentication:
    def __init__(self):
        self.db = Database()
        self.db.connect()
        self.initialize_admin()

    def initialize_admin(self):
        """Create default admin if it doesn't exist"""
        admin = self.get_user_by_username("admin")
        if admin:
            return

        hashed_password = self.hash_password("admin123")

        query = """
        INSERT INTO users
        (username, password, role, full_name)
        VALUES (?, ?, ?, ?)
        """

        self.db.execute_query(
            query,
            (
                "admin",
                hashed_password,
                "admin",
                "System Administrator",
            ),
        )
        print("✅ Default admin user created (admin/admin123)")

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def login(self, username, password):
        """Authenticate user"""
        if not username or not password:
            return None

        hashed_password = self.hash_password(password)

        query = """
        SELECT *
        FROM users
        WHERE username = ?
        AND password = ?
        """

        result = self.db.fetch_one(query, (username, hashed_password))

        if result:
            print(f"✅ Login successful for: {username}")
            return dict(result)

        print(f"❌ Login failed for: {username}")
        return None

    def get_user_by_username(self, username):
        """Return user by username"""
        query = "SELECT * FROM users WHERE username = ?"
        return self.db.fetch_one(query, (username,))

    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        return self.db.fetch_one(query, (user_id,))


    from utils.validation import Validator

    def register_user(self, username, password, role, full_name, **kwargs):
        """Register a new user and create role profile"""

        # ==================================================
        # CLEAN INPUT
        # ==================================================
        username = username.strip()
        full_name = full_name.strip()

        # ==================================================
        # VALIDATION LAYER
        # ==================================================
        valid, msg = Validator.validate_username(username)
        if not valid:
            return False, msg

        valid, msg = Validator.validate_password(password)
        if not valid:
            return False, msg

        valid, msg = Validator.validate_role(role)
        if not valid:
            return False, msg

        if kwargs.get("email"):
            valid, msg = Validator.validate_email(kwargs.get("email"))
            if not valid:
                return False, msg

        if kwargs.get("phone"):
            valid, msg = Validator.validate_phone(kwargs.get("phone"))
            if not valid:
                return False, msg

        if kwargs.get("age"):
            valid, msg = Validator.validate_age(kwargs.get("age"))
            if not valid:
                return False, msg

        # ==================================================
        # BASIC CHECKS
        # ==================================================
        if not username:
            return False, "Username is required"

        if not password:
            return False, "Password is required"

        if not full_name:
            return False, "Full Name is required"

        if role not in ("admin", "doctor", "patient"):
            return False, "Invalid role"

        # Username exists check
        if self.get_user_by_username(username):
            return False, "Username already exists"

        hashed_password = self.hash_password(password)

        try:

            # ==================================================
            # INSERT USER
            # ==================================================
            user_query = """
            INSERT INTO users
            (
                username,
                password,
                role,
                full_name,
                email,
                phone,
                gender,
                age
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            self.db.cursor.execute(
                user_query,
                (
                    username,
                    hashed_password,
                    role,
                    full_name,
                    kwargs.get("email"),
                    kwargs.get("phone"),
                    kwargs.get("gender"),
                    kwargs.get("age"),
                ),
            )

            user_id = self.db.cursor.lastrowid

            # ==================================================
            # PATIENT PROFILE
            # ==================================================
            if role == "patient":

                patient_query = """
                INSERT INTO patient_profile
                (
                    user_id,
                    address,
                    medical_history,
                    emergency_contact,
                    blood_group
                )
                VALUES (?, ?, ?, ?, ?)
                """

                self.db.cursor.execute(
                    patient_query,
                    (
                        user_id,
                        kwargs.get("address"),
                        kwargs.get("medical_history"),
                        kwargs.get("emergency_contact"),
                        kwargs.get("blood_group"),
                    ),
                )

            # ==================================================
            # DOCTOR PROFILE
            # ==================================================
            elif role == "doctor":

                doctor_query = """
                INSERT INTO doctor_profile
                (
                    user_id,
                    specialization,
                    years_experience,
                    qualification,
                    hospital_name,
                    consultation_fee,
                    bio,
                    available_days,
                    available_time
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                self.db.cursor.execute(
                    doctor_query,
                    (
                        user_id,
                        kwargs.get("specialization"),
                        kwargs.get("years_experience", 0),
                        kwargs.get("qualification"),
                        kwargs.get("hospital_name"),
                        kwargs.get("consultation_fee", 0),
                        kwargs.get("bio"),
                        kwargs.get("available_days"),
                        kwargs.get("available_time"),
                    ),
                )

            self.db.connection.commit()

            return True, f"Registration Successful (User ID: {user_id})"

        except Exception as e:
            self.db.connection.rollback()
            print("❌ Registration Error:", e)
            return False, str(e)

    def close(self):
        self.db.close()