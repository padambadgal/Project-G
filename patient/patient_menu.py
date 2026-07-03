# patient/patient_menu.py
import os
from patient.patient import Patient
from reports.reports import Reports

class PatientMenu:
    def __init__(self, user_info):
        self.user_info = user_info
        self.patient = Patient()
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_patient_menu(self):
        """Display the patient main menu"""
        # Get patient info
        patient_info = self.patient.get_patient_by_username(self.user_info['username'])
        
        while True:
            self.clear_screen()
            print("=" * 60)
            print("            PATIENT DASHBOARD")
            print("=" * 60)
            print(f"Welcome, {self.user_info['full_name']} ({self.user_info['username']})")
            print("=" * 60)
            print("\n1. View My Profile")
            print("2. Update My Profile")
            print("3. View My Prediction History")
            print("4. Logout")
            print("-" * 60)
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                self.view_profile()
            elif choice == '2':
                self.update_profile()
            elif choice == '3':
                self.view_prediction_history()
            elif choice == '4':
                print("\nLogging out...")
                break
            else:
                input("\nInvalid choice. Press Enter to continue...")
    
    def view_profile(self):
        """View patient profile"""
        self.clear_screen()
        print("\n--- My Profile ---\n")
        
        patient_info = self.patient.get_patient_by_username(self.user_info['username'])
        
        if patient_info:
            print(f"Patient ID: {patient_info[1]}")
            print(f"Full Name: {patient_info[2]}")
            print(f"Age: {patient_info[3]}")
            print(f"Gender: {patient_info[4]}")
            print(f"Contact: {patient_info[5]}")
            print(f"Address: {patient_info[6]}")
            print(f"Medical History: {patient_info[7] if patient_info[7] else 'None'}")
            print(f"Registered: {patient_info[8]}")
        else:
            print("Profile not found.")
        
        input("\nPress Enter to continue...")
    
    def update_profile(self):
        """Update patient profile"""
        self.clear_screen()
        print("\n--- Update My Profile ---\n")
        
        patient_info = self.patient.get_patient_by_username(self.user_info['username'])
        
        if not patient_info:
            print("Profile not found.")
            input("\nPress Enter to continue...")
            return
        
        patient_id = patient_info[1]
        
        print(f"Current Details:")
        print(f"Name: {patient_info[2]}")
        print(f"Age: {patient_info[3]}")
        print(f"Gender: {patient_info[4]}")
        print(f"Contact: {patient_info[5]}")
        print(f"Address: {patient_info[6]}")
        print(f"Medical History: {patient_info[7] if patient_info[7] else 'None'}")
        
        print("\nEnter new values (leave blank to keep current):")
        full_name = input(f"Full Name [{patient_info[2]}]: ").strip()
        age = input(f"Age [{patient_info[3]}]: ").strip()
        gender = input(f"Gender [{patient_info[4]}]: ").strip()
        contact = input(f"Contact [{patient_info[5]}]: ").strip()
        address = input(f"Address [{patient_info[6]}]: ").strip()
        medical_history = input(f"Medical History [{patient_info[7]}]: ").strip()
        
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
            print(f"\n✓ Profile updated successfully!")
        else:
            print(f"\n✗ Error: {message}")
        
        input("\nPress Enter to continue...")
    
    def view_prediction_history(self):
        """View patient's prediction history"""
        self.clear_screen()
        print("\n--- My Prediction History ---\n")
        
        patient_info = self.patient.get_patient_by_username(self.user_info['username'])
        
        if not patient_info:
            print("Profile not found.")
            input("\nPress Enter to continue...")
            return
        
        reports = Reports()
        predictions = reports.get_patient_predictions(patient_info[1])
        
        if predictions:
            print(f"{'Date':<20} {'Disease':<20} {'Doctor':<20} {'Confidence':<12} {'Risk':<10}")
            print("-" * 90)
            for pred in predictions:
                doctor_name = pred[7] if pred[7] else 'N/A'
                print(f"{pred[9][:19]:<20} {pred[5]:<20} {doctor_name[:20]:<20} {pred[6]:.2%}   {pred[7]:<10}")
        else:
            print("No prediction history found.")
        
        reports.close()
        input("\nPress Enter to continue...")