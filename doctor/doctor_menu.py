# doctor/doctor_menu.py
import os
from models.doctor import Doctor
from models.patient import Patient
from ai.predict import DiseasePredictor
from reports.reports import Reports
from database.database import Database
from utils.helper import generate_recommendation, calculate_risk_level


class DoctorMenu:
    def __init__(self, user_info):
        self.user_info = user_info
        self.doctor = Doctor()
        self.patient = Patient()
        self.db = Database()
        self.db.connect()
        self.predictor = DiseasePredictor()
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_doctor_menu(self):
        """Display the doctor main menu"""
        # Load the model
        if not self.predictor.load_model():
            print("Model not found. Please ask the admin to train the model.")
        
        while True:
            self.clear_screen()
            print("=" * 60)
            print("             DOCTOR DASHBOARD")
            print("=" * 60)
            print(f"Welcome, Dr. {self.user_info['full_name']} ({self.user_info['username']})")
            print("=" * 60)
            print("\n1. Predict Disease for Patient")
            print("2. View My Predictions")
            print("3. View Patient Records")
            print("4. Search Patient")
            print("5. View Prediction Statistics")
            print("6. Logout")
            print("-" * 60)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.predict_disease()
            elif choice == '2':
                self.view_my_predictions()
            elif choice == '3':
                self.view_patient_records()
            elif choice == '4':
                self.search_patient()
            elif choice == '5':
                self.view_statistics()
            elif choice == '6':
                print("\nLogging out...")
                break
            else:
                input("\nInvalid choice. Press Enter to continue...")
    
    def predict_disease(self):
        """Predict disease for a patient"""
        self.clear_screen()
        print("\n--- Disease Prediction for Patient ---\n")
        
        # Get patient ID
        patient_id = input("Enter Patient ID: ").strip()
        patient = self.patient.get_patient_by_id(patient_id)
        
        if not patient:
            print(f"\n✗ Patient with ID {patient_id} not found.")
            input("\nPress Enter to continue...")
            return
        
        # Using dictionary access
        print(f"\nPatient: {patient['full_name']}")
        print(f"Age: {patient['age']}")
        print(f"Gender: {patient['gender']}")
        print("-" * 40)
        
        # Get symptoms
        print("\nPlease enter symptoms (0 = No, 1 = Yes):")
        symptoms = {}
        required_symptoms = self.predictor.get_symptoms_required()
        
        if not required_symptoms:
            print("No symptoms defined. Please train the model first.")
            input("\nPress Enter to continue...")
            return
        
        for symptom in required_symptoms:
            while True:
                try:
                    value = input(f"{symptom.replace('_', ' ').title()}: ").strip()
                    if value in ['0', '1']:
                        symptoms[symptom] = int(value)
                        break
                    else:
                        print("Please enter 0 or 1")
                except:
                    print("Please enter 0 or 1")
        
        # Predict disease
        print("\nAnalyzing symptoms...")
        result = self.predictor.predict_disease(symptoms)
        
        if result:
            risk_level = calculate_risk_level(result['confidence'])
            recommendation = generate_recommendation(result['disease'], risk_level)
            
            print("\n" + "=" * 50)
            print("PREDICTION RESULT")
            print("=" * 50)
            print(f"Predicted Disease: {result['disease']}")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"Risk Level: {risk_level}")
            print("\nRecommendation:")
            print(recommendation)
            print("=" * 50)
            
            # Save prediction to database
            symptoms_str = ', '.join([f"{k.replace('_', ' ')}: {v}" for k, v in symptoms.items() if v == 1])
            if not symptoms_str:
                symptoms_str = "No symptoms reported"
            
            # Get doctor ID using dictionary access
            doctor_info = self.doctor.get_all_doctors()
            doctor_id = None
            if doctor_info:
                # Use the first doctor or find by name
                for doc in doctor_info:
                    if self.user_info['full_name'] in doc['full_name']:
                        doctor_id = doc['doctor_id']
                        break
                if not doctor_id:
                    doctor_id = doctor_info[0]['doctor_id']  # Use first doctor
            
            query = """INSERT INTO predictions 
                       (patient_id, doctor_id, symptoms, predicted_disease, confidence, risk_level, recommendation) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)"""
            
            self.db.execute_query(query, (
                patient_id,
                doctor_id,
                symptoms_str,
                result['disease'],
                result['confidence'],
                risk_level,
                recommendation
            ))
            
            print("\n✓ Prediction saved successfully!")
        else:
            print("\n✗ Prediction failed. Please ensure the model is properly trained.")
        
        input("\nPress Enter to continue...")
    
    def view_my_predictions(self):
        """View predictions made by the doctor"""
        self.clear_screen()
        print("\n--- My Predictions ---\n")
        
        # Get doctor ID using dictionary access
        doctor_info = self.doctor.get_all_doctors()
        doctor_id = None
        if doctor_info:
            for doc in doctor_info:
                if self.user_info['full_name'] in doc['full_name']:
                    doctor_id = doc['doctor_id']
                    break
        
        if not doctor_id:
            print("Doctor record not found. Please add doctor profile first.")
            input("\nPress Enter to continue...")
            return
        
        reports = Reports()
        predictions = reports.get_doctor_predictions(doctor_id)
        
        if predictions:
            print(f"{'Patient':<20} {'Disease':<20} {'Confidence':<12} {'Risk':<10} {'Date':<20}")
            print("-" * 90)
            for pred in predictions:
                patient_name = pred['patient_name'] if pred['patient_name'] else 'N/A'
                confidence = pred['confidence'] if pred['confidence'] else 0
                risk_level = pred['risk_level'] if pred['risk_level'] else 'N/A'
                predicted_at = pred['predicted_at'] if pred['predicted_at'] else 'N/A'
                if predicted_at and predicted_at != 'N/A':
                    predicted_at = str(predicted_at)[:19]
                disease = pred['predicted_disease'] if pred['predicted_disease'] else 'N/A'
                print(f"{patient_name[:20]:<20} {disease[:20]:<20} {confidence:.2%}   {risk_level:<10} {predicted_at:<20}")
        else:
            print("No predictions found.")
        
        reports.close()
        input("\nPress Enter to continue...")
    
    def view_patient_records(self):
        """View patient records"""
        self.clear_screen()
        print("\n--- Patient Records ---\n")
        
        patients = self.patient.get_all_patients()
        if patients:
            print(f"{'ID':<15} {'Name':<30} {'Age':<5} {'Gender':<10} {'Contact':<15}")
            print("-" * 80)
            for patient in patients:
                # ✅ FIX: Properly handle age and contact
                age = patient['age'] if patient['age'] else 'N/A'
                contact = patient['contact'] if patient['contact'] else 'N/A'
                print(f"{patient['patient_id']:<15} {patient['full_name']:<30} {age:<5} {patient['gender']:<10} {contact:<15}")
        else:
            print("No patients found.")
        
        input("\nPress Enter to continue...")
    
    def search_patient(self):
        """Search for a patient"""
        self.clear_screen()
        print("\n--- Search Patient ---\n")
        
        search_term = input("Enter patient name, ID, or contact: ").strip()
        results = self.patient.search_patients(search_term)
        
        if results:
            print(f"\n{'ID':<15} {'Name':<30} {'Age':<5} {'Gender':<10} {'Contact':<15}")
            print("-" * 80)
            for patient in results:
                contact = patient['contact'] if patient['contact'] else 'N/A'
                print(f"{patient['patient_id']:<15} {patient['full_name']:<30} {patient['age']:<5} {patient['gender']:<10} {contact:<15}")
                
            # Option to view detailed patient info
            if len(results) == 1:
                view_details = input("\nView detailed patient info? (y/n): ").strip().lower()
                if view_details == 'y':
                    self.view_patient_details(results[0]['patient_id'])
        else:
            print("\nNo patients found matching the search term.")
        
        input("\nPress Enter to continue...")
    
    def view_patient_details(self, patient_id):
        """View detailed patient information"""
        self.clear_screen()
        print("\n--- Patient Details ---\n")
        
        patient = self.patient.get_patient_by_id(patient_id)
        if patient:
            contact = patient['contact'] if patient['contact'] else 'N/A'
            address = patient['address'] if patient['address'] else 'N/A'
            medical_history = patient['medical_history'] if patient['medical_history'] else 'None'
            
            print(f"Patient ID: {patient['patient_id']}")
            print(f"Full Name: {patient['full_name']}")
            print(f"Age: {patient['age']}")
            print(f"Gender: {patient['gender']}")
            print(f"Contact: {contact}")
            print(f"Address: {address}")
            print(f"Medical History: {medical_history}")
            print(f"Registered: {patient['created_at']}")
            
            # Get prediction history for this patient
            reports = Reports()
            predictions = reports.get_patient_predictions(patient_id)
            
            if predictions:
                print("\nPrediction History:")
                print(f"{'Date':<20} {'Disease':<20} {'Doctor':<20}")
                print("-" * 60)
                for pred in predictions:
                    doctor_name = pred['doctor_name'] if pred['doctor_name'] else 'N/A'
                    predicted_at = pred['predicted_at'] if pred['predicted_at'] else 'N/A'
                    if predicted_at and predicted_at != 'N/A':
                        predicted_at = str(predicted_at)[:19]
                    disease = pred['predicted_disease'] if pred['predicted_disease'] else 'N/A'
                    print(f"{predicted_at:<20} {disease[:20]:<20} {doctor_name[:20]:<20}")
            
            reports.close()
        else:
            print("Patient not found.")
        
        input("\nPress Enter to continue...")
    
    def view_statistics(self):
        """View prediction statistics"""
        self.clear_screen()
        print("\n--- Prediction Statistics ---\n")
        
        # Get doctor ID using dictionary access
        doctor_info = self.doctor.get_all_doctors()
        doctor_id = None
        if doctor_info:
            for doc in doctor_info:
                if self.user_info['full_name'] in doc['full_name']:
                    doctor_id = doc['doctor_id']
                    break
        
        if not doctor_id:
            print("Doctor record not found. Please add doctor profile first.")
            input("\nPress Enter to continue...")
            return
        
        reports = Reports()
        stats = reports.get_doctor_statistics(doctor_id)
        
        print(f"Total Predictions: {stats['total_predictions']}")
        print(f"Average Confidence: {stats['avg_confidence']:.2%}")
        print(f"Unique Patients: {stats['unique_patients']}")
        
        reports.close()
        input("\nPress Enter to continue...")

    def view_medical_history(self):
        print("\n--- Medical History ---\n")

        patient_id = self.user_info['id']

        records = self.patient.get_medical_records(patient_id)

        if records:

            for r in records:
                print(f"\nDoctor: {r['doctor_name']}")
                print(f"Symptoms: {r['symptoms']}")
                print(f"Disease: {r['disease']}")
                print(f"Diagnosis: {r['diagnosis']}")
                print(f"Prescription: {r['prescription']}")
                print(f"Notes: {r['notes']}")
                print(f"Date: {r['visit_date']}")
                print("-" * 40)

        else:
            print("No medical records found.")

        input("\nPress Enter to continue...")