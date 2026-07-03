# utils/validation.py
import re

class Validator:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_age(age):
        """Validate age"""
        try:
            age = int(age)
            return 0 < age < 120
        except:
            return False
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate required fields are present"""
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"{field} is required"
        return True, ""