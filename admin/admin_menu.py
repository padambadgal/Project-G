# admin/admin_menu.py
import os
import sys
from admin.admin import Admin
from doctor.doctor import Doctor
from patient.patient import Patient

class AdminMenu:
    def __init__(self, user_info):
        self.user_info = user_info
        self.admin = Admin()
        self.doctor = Doctor()
        self.patient = Patient()
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_admin_menu(self):
        """Display the admin main menu"""
        while True:
            self.clear_screen()
            print("=" * 60)
            print("              ADMIN DASHBOARD")
            print("=" * 60)
            print(f"Welcome, {self.user_info['full_name']} ({self.user_info['username']})")
            print("=" * 60)
            print("\n1. Manage Patients")
            print("2. Manage Doctors")
            print("3. Manage Users")
            print("4. View System Statistics")
            print("5. Train AI Model")
            print("6. View All Predictions")
            print("7. Logout")
            print("-" * 60)
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.manage_patients()
            elif choice == '2':
                self.manage_doctors()
            elif choice == '3':
                self.manage_users()
            elif choice == '4':
                self.view_statistics()
            elif choice == '5':
                self.train_model()
            elif choice == '6':
                self.view_predictions()
            elif choice == '7':
                print("\nLogging out...")
                break
            else:
                input("\nInvalid choice. Press Enter to continue...")
    
    def manage_patients(self):
        """Patient management menu for admin"""
        while True:
            self.clear_screen()
            print("=" * 50)
            print("         PATIENT MANAGEMENT")
            print("=" * 50)
            print("\n1. Add Patient")
            print("2. View All Patients")
            print("3. Search Patient")
            print("4. Update Patient")
            print("5. Delete Patient")
            print("6. Back to Main Menu")
            print("-" * 50)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.add_patient()
            elif choice == '2':
                self.view_all_patients()
            elif choice == '3':
                self.search_patient()
            elif choice == '4':
                self.update_patient()
            elif choice == '5':
                self.delete_patient()
            elif choice == '6':
                break
            else:
                input("\nInvalid choice. Press Enter to continue...")
    
    def add_patient(self):
        self.clear_screen()
        print("\n--- Add New Patient ---\n")
        
        full_name = input("Full Name: ").strip()
        age = input("Age: ").strip()
        gender = input("Gender: ").strip()
        contact = input("Contact Number: ").strip()
        address = input("Address: ").strip()
        medical_history = input("Medical History (optional): ").strip()
        
        success, result = self.patient.add_patient(
            full_name, age, gender, contact, address, medical_history
        )
        
        if success:
            print(f"\n✓ Patient added successfully! Patient ID: {result}")
        else:
            print(f"\n✗ Error: {result}")
        
        input("\nPress Enter to continue...")
    
    def view_all_patients(self):
        self.clear_screen()
        print("\n--- All Patients ---\n")
        
        patients = self.patient.get_all_patients()
        if patients:
            print(f"{'ID':<15} {'Name':<30} {'Age':<5} {'Gender':<10} {'Contact':<15}")
            print("-" * 80)
            for patient in patients:
                print(f"{patient[1]:<15} {patient[2]:<30} {patient[3]:<5} {patient[4]:<10} {patient[5]:<15}")
        else:
            print("No patients found.")
        
        input("\nPress Enter to continue...")
    
    def search_patient(self):
        self.clear_screen()
        print("\n--- Search Patient ---\n")
        
        search_term = input("Enter patient name, ID, or contact: ").strip()
        results = self.patient.search_patients(search_term)
        
        if results:
            print(f"\n{'ID':<15} {'Name':<30} {'Age':<5} {'Gender':<10} {'Contact':<15}")
            print("-" * 80)
            for patient in results:
                print(f"{patient[1]:<15} {patient[2]:<30} {patient[3]:<5} {patient[4]:<10} {patient[5]:<15}")
        else:
            print("\nNo patients found matching the search term.")
        
        input("\nPress Enter to continue...")
    
    def update_patient(self):
        self.clear_screen()
        print("\n--- Update Patient ---\n")
        
        patient_id = input("Enter Patient ID to update: ").strip()
        patient = self.patient.get_patient_by_id(patient_id)
        
        if not patient:
            print(f"\n✗ Patient with ID {patient_id} not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nCurrent Details:")
        print(f"Name: {patient[2]}")
        print(f"Age: {patient[3]}")
        print(f"Gender: {patient[4]}")
        print(f"Contact: {patient[5]}")
        print(f"Address: {patient[6]}")
        print(f"Medical History: {patient[7]}")
        
        print("\nEnter new values (leave blank to keep current):")
        full_name = input(f"Full Name [{patient[2]}]: ").strip()
        age = input(f"Age [{patient[3]}]: ").strip()
        gender = input(f"Gender [{patient[4]}]: ").strip()
        contact = input(f"Contact [{patient[5]}]: ").strip()
        address = input(f"Address [{patient[6]}]: ").strip()
        medical_history = input(f"Medical History [{patient[7]}]: ").strip()
        
        success, message = self.patient.update_patient(
            patient_id,
            full_name=full_name if full_name else None,
            age=age if age else None,
            gender=gender if gender else None,
            contact=contact if contact else None,
            address=address if address else None,
            medical_history=medical_history if medical_history else None
        )
        
        if success:
            print(f"\n✓ Patient updated successfully!")
        else:
            print(f"\n✗ Error: {message}")
        
        input("\nPress Enter to continue...")
    
    def delete_patient(self):
        self.clear_screen()
        print("\n--- Delete Patient ---\n")
        
        patient_id = input("Enter Patient ID to delete: ").strip()
        confirm = input(f"Are you sure you want to delete patient {patient_id}? (y/n): ").strip().lower()
        
        if confirm == 'y':
            success, message = self.patient.delete_patient(patient_id)
            if success:
                print(f"\n✓ Patient deleted successfully!")
            else:
                print(f"\n✗ Error: {message}")
        else:
            print("\nDeletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def manage_doctors(self):
        """Doctor management menu"""
        while True:
            self.clear_screen()
            print("=" * 50)
            print("         DOCTOR MANAGEMENT")
            print("=" * 50)
            print("\n1. Add Doctor")
            print("2. View All Doctors")
            print("3. Search Doctor")
            print("4. Update Doctor")
            print("5. Delete Doctor")
            print("6. Back to Main Menu")
            print("-" * 50)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.add_doctor()
            elif choice == '2':
                self.view_all_doctors()
            elif choice == '3':
                self.search_doctor()
            elif choice == '4':
                self.update_doctor()
            elif choice == '5':
                self.delete_doctor()
            elif choice == '6':
                break
            else:
                input("\nInvalid choice. Press Enter to continue...")
    
    def add_doctor(self):
        self.clear_screen()
        print("\n--- Add New Doctor ---\n")
        
        full_name = input("Full Name: ").strip()
        specialization = input("Specialization: ").strip()
        contact = input("Contact Number: ").strip()
        email = input("Email: ").strip()
        years_experience = input("Years of Experience: ").strip()
        
        success, result = self.doctor.add_doctor(
            full_name, specialization, contact, email, years_experience
        )
        
        if success:
            print(f"\n✓ Doctor added successfully! Doctor ID: {result}")
        else:
            print(f"\n✗ Error: {result}")
        
        input("\nPress Enter to continue...")
    
    def view_all_doctors(self):
        self.clear_screen()
        print("\n--- All Doctors ---\n")
        
        doctors = self.doctor.get_all_doctors()
        if doctors:
            print(f"{'ID':<15} {'Name':<30} {'Specialization':<25} {'Experience':<10} {'Contact':<15}")
            print("-" * 100)
            for doctor in doctors:
                print(f"{doctor[1]:<15} {doctor[2]:<30} {doctor[3]:<25} {doctor[6]:<10} {doctor[4]:<15}")
        else:
            print("No doctors found.")
        
        input("\nPress Enter to continue...")
    
    def search_doctor(self):
        self.clear_screen()
        print("\n--- Search Doctor ---\n")
        
        search_term = input("Enter doctor name, ID, or specialization: ").strip()
        results = self.doctor.search_doctors(search_term)
        
        if results:
            print(f"\n{'ID':<15} {'Name':<30} {'Specialization':<25} {'Experience':<10}")
            print("-" * 85)
            for doctor in results:
                print(f"{doctor[1]:<15} {doctor[2]:<30} {doctor[3]:<25} {doctor[6]:<10}")
        else:
            print("\nNo doctors found matching the search term.")
        
        input("\nPress Enter to continue...")
    
    def update_doctor(self):
        self.clear_screen()
        print("\n--- Update Doctor ---\n")
        
        doctor_id = input("Enter Doctor ID to update: ").strip()
        doctor = self.doctor.get_doctor_by_id(doctor_id)
        
        if not doctor:
            print(f"\n✗ Doctor with ID {doctor_id} not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nCurrent Details:")
        print(f"Name: {doctor[2]}")
        print(f"Specialization: {doctor[3]}")
        print(f"Contact: {doctor[4]}")
        print(f"Email: {doctor[5]}")
        print(f"Years of Experience: {doctor[6]}")
        
        print("\nEnter new values (leave blank to keep current):")
        full_name = input(f"Full Name [{doctor[2]}]: ").strip()
        specialization = input(f"Specialization [{doctor[3]}]: ").strip()
        contact = input(f"Contact [{doctor[4]}]: ").strip()
        email = input(f"Email [{doctor[5]}]: ").strip()
        years_experience = input(f"Years of Experience [{doctor[6]}]: ").strip()
        
        success, message = self.doctor.update_doctor(
            doctor_id,
            full_name=full_name if full_name else None,
            specialization=specialization if specialization else None,
            contact=contact if contact else None,
            email=email if email else None,
            years_experience=years_experience if years_experience else None
        )
        
        if success:
            print(f"\n✓ Doctor updated successfully!")
        else:
            print(f"\n✗ Error: {message}")
        
        input("\nPress Enter to continue...")
    
    def delete_doctor(self):
        self.clear_screen()
        print("\n--- Delete Doctor ---\n")
        
        doctor_id = input("Enter Doctor ID to delete: ").strip()
        confirm = input(f"Are you sure you want to delete doctor {doctor_id}? (y/n): ").strip().lower()
        
        if confirm == 'y':
            success, message = self.doctor.delete_doctor(doctor_id)
            if success:
                print(f"\n✓ Doctor deleted successfully!")
            else:
                print(f"\n✗ Error: {message}")
        else:
            print("\nDeletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def manage_users(self):
        """User management menu"""
        while True:
            self.clear_screen()
            print("=" * 50)
            print("          USER MANAGEMENT")
            print("=" * 50)
            print("\n1. View All Users")
            print("2. Add New User")
            print("3. Delete User")
            print("4. Back to Main Menu")
            print("-" * 50)
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                self.view_all_users()
            elif choice == '2':
                self.add_new_user()
            elif choice == '3':
                self.delete_user()
            elif choice == '4':
                break
            else:
                input("\nInvalid choice. Press Enter to continue...")
    
    def view_all_users(self):
        self.clear_screen()
        print("\n--- All Users ---\n")
        
        users = self.admin.get_all_users()
        if users:
            print(f"{'Username':<15} {'Full Name':<30} {'Role':<15} {'Email':<25}")
            print("-" * 90)
            for user in users:
                print(f"{user[1]:<15} {user[4]:<30} {user[3]:<15} {user[5] if user[5] else 'N/A':<25}")
        else:
            print("No users found.")
        
        input("\nPress Enter to continue...")
    
    def add_new_user(self):
        self.clear_screen()
        print("\n--- Add New User ---\n")
        
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        full_name = input("Full Name: ").strip()
        role = input("Role (admin/doctor/patient): ").strip().lower()
        email = input("Email (optional): ").strip()
        phone = input("Phone (optional): ").strip()
        
        if role not in ['admin', 'doctor', 'patient']:
            print("\n✗ Invalid role. Must be admin, doctor, or patient.")
            input("\nPress Enter to continue...")
            return
        
        success, result = self.admin.create_user(username, password, role, full_name, email, phone)
        
        if success:
            print(f"\n✓ User added successfully!")
        else:
            print(f"\n✗ Error: {result}")
        
        input("\nPress Enter to continue...")
    
    def delete_user(self):
        self.clear_screen()
        print("\n--- Delete User ---\n")
        
        username = input("Enter username to delete: ").strip()
        
        if username == 'admin':
            print("\n✗ Cannot delete the default admin user.")
            input("\nPress Enter to continue...")
            return
        
        confirm = input(f"Are you sure you want to delete user {username}? (y/n): ").strip().lower()
        
        if confirm == 'y':
            success, message = self.admin.delete_user(username)
            if success:
                print(f"\n✓ User deleted successfully!")
            else:
                print(f"\n✗ Error: {message}")
        else:
            print("\nDeletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def view_statistics(self):
        """View system statistics"""
        self.clear_screen()
        print("\n--- System Statistics ---\n")
        
        stats = self.admin.get_system_statistics()
        
        print("User Statistics:")
        for role, count in stats['user_stats']:
            print(f"  {role.capitalize()}s: {count}")
        
        print(f"\nTotal Patients: {stats['total_patients']}")
        print(f"Total Doctors: {stats['total_doctors']}")
        print(f"Total Predictions: {stats['total_predictions']}")
        
        input("\nPress Enter to continue...")
    
    def train_model(self):
        """Train the AI model"""
        self.clear_screen()
        print("\n--- Train AI Model ---\n")
        
        from ai.train_model import ModelTrainer
        
        print("Training model... This may take a moment...")
        trainer = ModelTrainer()
        trainer.load_and_prepare_data()
        trainer.train_model()
        trainer.save_model()
        accuracy = trainer.evaluate_model()
        
        print(f"\n✓ Model trained successfully!")
        print(f"Model Accuracy: {accuracy:.2%}")
        
        input("\nPress Enter to continue...")
    
    def view_predictions(self):
        """View all predictions"""
        self.clear_screen()
        print("\n--- All Predictions ---\n")
        
        from reports.reports import Reports
        reports = Reports()
        predictions = reports.get_prediction_history(365)  # Last year
        
        if predictions:
            print(f"{'Patient':<20} {'Doctor':<20} {'Disease':<20} {'Confidence':<12} {'Risk':<10} {'Date':<20}")
            print("-" * 110)
            for pred in predictions:
                patient_name = pred[7] if pred[7] else 'N/A'
                doctor_name = pred[8] if pred[8] else 'N/A'
                print(f"{patient_name[:20]:<20} {doctor_name[:20]:<20} {pred[5]:<20} {pred[6]:.2%}   {pred[7]:<10} {pred[9][:19]:<20}")
        else:
            print("No predictions found.")
        
        reports.close()
        input("\nPress Enter to continue...")