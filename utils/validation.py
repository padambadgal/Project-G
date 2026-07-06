import re


class Validator:

    # =========================
    # USERNAME VALIDATION
    # =========================
    @staticmethod
    def validate_username(username):
        if not username:
            return False, "Username cannot be empty"

        if len(username) < 3:
            return False, "Username must be at least 3 characters"

        if not re.match("^[a-zA-Z0-9_]+$", username):
            return False, "Username can only contain letters, numbers, underscore"

        return True, "Valid username"

    # =========================
    # PASSWORD VALIDATION
    # =========================
    @staticmethod
    def validate_password(password):
        if not password:
            return False, "Password cannot be empty"

        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        if len(password) > 30:
            return False, "Password too long"

        return True, "Valid password"

    # =========================
    # EMAIL VALIDATION
    # =========================
    @staticmethod
    def validate_email(email):
        if not email:
            return True, "Optional field"

        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(pattern, email):
            return False, "Invalid email format"

        return True, "Valid email"

    # =========================
    # PHONE VALIDATION
    # =========================
    @staticmethod
    def validate_phone(phone):
        if not phone:
            return True, "Optional field"

        if not phone.isdigit():
            return False, "Phone must contain only numbers"

        if len(phone) != 10:
            return False, "Phone must be 10 digits"

        return True, "Valid phone"

    # =========================
    # AGE VALIDATION
    # =========================
    @staticmethod
    def validate_age(age):
        if not age:
            return True, "Optional field"

        try:
            age = int(age)
        except:
            return False, "Age must be a number"

        if age < 0 or age > 150:
            return False, "Invalid age range"

        return True, "Valid age"

    # =========================
    # ROLE VALIDATION
    # =========================
    @staticmethod
    def validate_role(role):
        valid_roles = ["admin", "doctor", "patient"]

        if role not in valid_roles:
            return False, "Invalid role"

        return True, "Valid role"

    # =========================
    # SYMPTOMS VALIDATION
    # =========================
    @staticmethod
    def validate_symptoms(symptoms):
        if not symptoms:
            return False, "Symptoms cannot be empty"

        if len(symptoms) < 3:
            return False, "Please enter proper symptoms"

        return True, "Valid symptoms"