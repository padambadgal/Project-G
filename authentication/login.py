# authentication/login.py
import hashlib
from database.database import Database

class Authentication:
    def __init__(self):
        self.db = Database()
        self.db.connect()
        self.initialize_admin()
    
    def initialize_admin(self):
        """Create default admin user if not exists"""
        hashed_password = self.hash_password("admin123")
        query = "INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)"
        self.db.execute_query(query, ("admin", hashed_password, "admin", "System Administrator"))
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        """Authenticate user"""
        hashed_password = self.hash_password(password)
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        result = self.db.fetch_one(query, (username, hashed_password))
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'role': result[3],
                'full_name': result[4],
                'email': result[5],
                'phone': result[6]
            }
        return None
    
def register_user(self, username, password, role, full_name, email=None, phone=None):
    """Register a new user - RETURNS TUPLE (success, message)"""
    try:
        # Check if username already exists
        existing = self.get_user_by_username(username)
        if existing:
            return False, "Username already exists"
        
        # Hash the password
        hashed_password = self.hash_password(password)
        
        # Insert new user
        query = """INSERT INTO users (username, password, role, full_name, email, phone) 
                   VALUES (?, ?, ?, ?, ?, ?)"""
        result = self.db.execute_query(query, (username, hashed_password, role, full_name, email, phone))
        
        if result:
            return True, "Registration successful"
        else:
            return False, "Registration failed"
            
    except Exception as e:
        return False, str(e)
    
    def get_user_by_username(self, username):
        """Get user details by username"""
        query = "SELECT * FROM users WHERE username = ?"
        return self.db.fetch_one(query, (username,))
    
    def close(self):
        self.db.close()