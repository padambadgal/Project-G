# authentication/login.py
import hashlib
from database.database import Database


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

# authentication/login.py - Add debug prints

    # authentication/login.py - Replace register_user method

   # authentication/login.py - Replace register_user method

    def register_user(self, username, password, role, full_name, **kwargs):
        """Register a new user with role-specific fields"""
        
        print(f"🔍 DEBUG: Starting registration for {username}")
        
        # Clean inputs
        username = username.strip()
        full_name = full_name.strip()

        if not username:
            return False, "Username is required"
        if not password:
            return False, "Password is required"
        if not full_name:
            return False, "Full name is required"
        if role not in ['admin', 'doctor', 'patient']:
            return False, "Invalid role"

        print(f"🔍 DEBUG: Validated inputs")

        # Check if username exists
        if self.get_user_by_username(username):
            return False, "Username already exists"

        print(f"🔍 DEBUG: Username is unique")

        email = kwargs.get('email')
        if email:
            email = email.strip()
            existing = self.db.fetch_one(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )
            if existing:
                return False, "Email already exists"

        print(f"🔍 DEBUG: Email validated")

        phone = kwargs.get('phone')
        gender = kwargs.get('gender')
        age = kwargs.get('age')
        address = kwargs.get('address')

        hashed_password = self.hash_password(password)
        
        print(f"🔍 DEBUG: Password hashed")

        # Build query based on role
        try:
            if role == 'doctor':
                specialization = kwargs.get('specialization')
                years_experience = kwargs.get('years_experience')
                
                query = """
                INSERT INTO users
                (username, password, role, full_name, email, phone, 
                gender, age, address, specialization, years_experience)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    username, hashed_password, role, full_name, email, phone,
                    gender, age, address, specialization, years_experience
                )
                
            elif role == 'patient':
                medical_history = kwargs.get('medical_history')
                emergency_contact = kwargs.get('emergency_contact')
                blood_group = kwargs.get('blood_group')
                
                query = """
                INSERT INTO users
                (username, password, role, full_name, email, phone, 
                gender, age, address, medical_history, emergency_contact, blood_group)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    username, hashed_password, role, full_name, email, phone,
                    gender, age, address, medical_history, emergency_contact, blood_group
                )
                
            else:  # admin
                query = """
                INSERT INTO users
                (username, password, role, full_name, email, phone, gender, age, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    username, hashed_password, role, full_name, email, phone,
                    gender, age, address
                )

            print(f"🔍 DEBUG: Executing query")
            print(f"🔍 DEBUG: Query: {query[:100]}...")
            print(f"🔍 DEBUG: Params count: {len(params)}")

            # Execute the query
            result = self.db.execute_query(query, params)
            
            print(f"🔍 DEBUG: Result from execute_query: {result}")
            
            if result and result > 0:
                print(f"✅ User registered: {username} ({role}) with ID: {result}")
                return True, f"Registration successful! User ID: {result}"
            else:
                # Check if user was actually inserted
                user = self.get_user_by_username(username)
                if user:
                    print(f"✅ User found in database despite result: {user['id']}")
                    return True, f"Registration successful! User ID: {user['id']}"
                else:
                    print(f"❌ Registration failed - no ID returned and user not found")
                    return False, "Registration failed - unable to create user"

        except Exception as e:
            print(f"❌ Registration error: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Database Error: {str(e)}"

    def close(self):
        self.db.close()