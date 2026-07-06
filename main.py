# main.py
import os
import sys
from authentication.login import Authentication
from admin.admin_menu import AdminMenu
from doctor.doctor_menu import DoctorMenu
from patient.patient_menu import PatientMenu
from ai.train_model import ModelTrainer
from config.settings import APP_NAME, VERSION

class HospitalSystem:
    def __init__(self):
        self.auth = Authentication()
        self.current_user = None
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display application header"""
        print("=" * 60)
        print(f"{APP_NAME}")
        print(f"Version: {VERSION}")
        print("=" * 60)
    
    def display_main_menu(self):
        """Display the main menu"""
        self.clear_screen()
        self.display_header()
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")
        print("-" * 60)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        return choice
    
    def login(self):
        """Handle user login"""
        self.clear_screen()
        self.display_header()
        print("\n--- Login ---\n")
        
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        user = self.auth.login(username, password)
        
        if user:
            self.current_user = user
            print(f"\n✓ Login successful! Welcome, {user['full_name']}.")
            input("\nPress Enter to continue...")
            return True
        else:
            print("\n✗ Invalid username or password.")
            input("\nPress Enter to continue...")
            return False
    
    def register(self):
        print("\n--- Register New User ---\n")

        username = input("Username: ").strip()
        password = input("Password: ").strip()
        confirm_password = input("Confirm Password: ").strip()

        if password != confirm_password:
            print("\n✗ Passwords do not match.")
            input("\nPress Enter to continue...")
            return False

        full_name = input("Full Name: ").strip()
        role = input("Role (admin/doctor/patient): ").strip().lower()

        if role not in ['admin', 'doctor', 'patient']:
            print("\n✗ Invalid role.")
            input("\nPress Enter to continue...")
            return False

        email = input("Email (optional): ").strip()
        phone = input("Phone (optional): ").strip()

        # =========================
        # DOCTOR EXTRA FIELDS
        # =========================
        doctor_data = {}

        if role == "doctor":
            print("\n--- Doctor Details ---")

            specialization = input("Specialization: ").strip()
            if not specialization:
                print("✗ Specialization is required for doctor")
                input("Press Enter...")
                return False

            years_experience = input("Years of Experience: ").strip()
            years_experience = int(years_experience) if years_experience else 0

            qualification = input("Qualification: ").strip()
            hospital_name = input("Hospital Name: ").strip()

            consultation_fee = input("Consultation Fee: ").strip()
            consultation_fee = float(consultation_fee) if consultation_fee else 0.0

            bio = input("Bio: ").strip()
            available_days = input("Available Days: ").strip()
            available_time = input("Available Time: ").strip()

            doctor_data = {
                "specialization": specialization,
                "years_experience": years_experience,
                "qualification": qualification,
                "hospital_name": hospital_name,
                "consultation_fee": consultation_fee,
                "bio": bio,
                "available_days": available_days,
                "available_time": available_time
            }

        # =========================
        # PATIENT FIELDS (optional future)
        # =========================
        patient_data = {}

        # =========================
        # REGISTER CALL
        # =========================
        success, message = self.auth.register_user(
            username=username,
            password=password,
            role=role,
            full_name=full_name,
            email=email if email else None,
            phone=phone if phone else None,
            **doctor_data,
            **patient_data
        )

        if success:
            print(f"\n✓ {message}")
        else:
            print(f"\n✗ Registration failed: {message}")

        input("\nPress Enter to continue...")
        return success
        
    def run(self):
        """Main application loop"""
        while True:
            choice = self.display_main_menu()
            
            if choice == '1':
                if self.login():
                    self.handle_user_session()
            elif choice == '2':
                self.register()
            elif choice == '3':
                print("\nThank you for using the AI Hospital Disease Prediction System!")
                print("Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("\nPress Enter to continue...")
    
    def handle_user_session(self):
        """Handle user session after login"""
        role = self.current_user['role']
        
        if role == 'admin':
            admin_menu = AdminMenu(self.current_user)
            admin_menu.display_admin_menu()
        elif role == 'doctor':
            doctor_menu = DoctorMenu(self.current_user)
            doctor_menu.display_doctor_menu()
        elif role == 'patient':
            patient_menu = PatientMenu(self.current_user)
            patient_menu.display_patient_menu()
        else:
            print(f"Unknown role: {role}")
            input("\nPress Enter to continue...")
        
        self.current_user = None

    def initialize_system():
        """Initialize the system - create necessary directories and files"""
        print("Initializing system...")
        
        # Create necessary directories
        directories = ['models', 'datasets', 'database']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        
        # Initialize database
        from database.database import Database
        db = Database()
        db.connect()
        print("✓ Database initialized")
        db.close()
        
        # Check if model exists
        from config.settings import MODEL_PATH
        if not os.path.exists(MODEL_PATH):
            print("\nNo AI model found. Do you want to train the model now?")
            choice = input("Train model? (y/n): ").strip().lower()
            if choice == 'y':
                print("\nTraining AI model...")
                trainer = ModelTrainer()
                trainer.load_and_prepare_data()
                trainer.train_model()
                trainer.save_model()
                trainer.evaluate_model()
                print("✓ Model training complete!")
        
        print("\n✓ System initialization complete!")
        input("\nPress Enter to continue...")

    def add_record(self):
        print("\n--- Add Medical Record ---\n")

        patient_id = input("Patient ID: ")
        symptoms = input("Symptoms: ")
        disease = input("Disease: ")
        diagnosis = input("Diagnosis: ")
        prescription = input("Prescription: ")
        notes = input("Notes: ")

        success, message = self.doctor.add_medical_record(
            patient_id,
            self.user_info['id'],
            symptoms,
            disease,
            diagnosis,
            prescription,
            notes
        )

        print("\n", message)
        input("\nPress Enter to continue...")

    def predict_patient(self):
        print("\n--- Disease Prediction ---\n")

        patient_id = input("Patient ID: ")
        symptoms = input("Enter Symptoms: ")

        result = self.doctor.predict_disease(
            patient_id,
            self.user_info['id'],
            symptoms
        )

        print("\n--- Prediction Result ---")
        print(f"Disease: {result['disease']}")
        print(f"Confidence: {result['confidence'] * 100}%")
        print(f"Risk Level: {result['risk']}")
        print(f"Recommendation: {result['recommendation']}")

        input("\nPress Enter to continue...")
        
if __name__ == "__main__":
    # Initialize system on first run
    if not os.path.exists('database/hospital.db'):
        initialize_system()
    
    # Run the application
    system = HospitalSystem()
    system.run()