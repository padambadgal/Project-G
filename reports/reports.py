# reports/reports.py
from database.database import Database
import pandas as pd
from datetime import datetime, timedelta

class Reports:
    def __init__(self):
        self.db = Database()
        self.db.connect()
    
    def get_prediction_history(self, days=30):
        """Get prediction history for the last N days"""
        start_date = datetime.now() - timedelta(days=days)
        query = """SELECT p.*, pat.full_name as patient_name, doc.full_name as doctor_name 
                   FROM predictions p
                   LEFT JOIN patients pat ON p.patient_id = pat.patient_id
                   LEFT JOIN doctors doc ON p.doctor_id = doc.doctor_id
                   WHERE p.predicted_at >= ?
                   ORDER BY p.predicted_at DESC"""
        return self.db.fetch_all(query, (start_date.strftime("%Y-%m-%d %H:%M:%S"),))
    
    def get_doctor_predictions(self, doctor_id):
        """Get predictions made by a specific doctor"""
        query = """SELECT p.*, pat.full_name as patient_name 
                   FROM predictions p
                   LEFT JOIN patients pat ON p.patient_id = pat.patient_id
                   WHERE p.doctor_id = ?
                   ORDER BY p.predicted_at DESC"""
        return self.db.fetch_all(query, (doctor_id,))
    
    def get_patient_predictions(self, patient_id):
        """Get predictions for a specific patient"""
        query = """SELECT p.*, doc.full_name as doctor_name 
                   FROM predictions p
                   LEFT JOIN doctors doc ON p.doctor_id = doc.doctor_id
                   WHERE p.patient_id = ?
                   ORDER BY p.predicted_at DESC"""
        return self.db.fetch_all(query, (patient_id,))
    
    def get_prediction_statistics(self):
        """Get statistics about predictions"""
        # Total predictions
        total_query = "SELECT COUNT(*) FROM predictions"
        total = self.db.fetch_one(total_query)[0]
        
        # Predictions by disease
        disease_query = """SELECT predicted_disease, COUNT(*) as count 
                           FROM predictions 
                           GROUP BY predicted_disease 
                           ORDER BY count DESC"""
        disease_stats = self.db.fetch_all(disease_query)
        
        # Predictions by risk level
        risk_query = """SELECT risk_level, COUNT(*) as count 
                        FROM predictions 
                        GROUP BY risk_level"""
        risk_stats = self.db.fetch_all(risk_query)
        
        return {
            'total_predictions': total,
            'disease_distribution': disease_stats,
            'risk_distribution': risk_stats
        }
    
    def get_doctor_statistics(self, doctor_id):
        """Get statistics for a specific doctor"""
        query = """SELECT COUNT(*) as total, 
                   AVG(confidence) as avg_confidence,
                   COUNT(DISTINCT patient_id) as unique_patients
                   FROM predictions 
                   WHERE doctor_id = ?"""
        result = self.db.fetch_one(query, (doctor_id,))
        
        return {
            'total_predictions': result[0] if result else 0,
            'avg_confidence': result[1] if result and result[1] else 0,
            'unique_patients': result[2] if result else 0
        }
    
    def generate_prediction_report(self, days=30):
        """Generate a comprehensive prediction report"""
        predictions = self.get_prediction_history(days)
        
        if not predictions:
            return "No predictions found for the specified period."
        
        report = []
        report.append("=" * 80)
        report.append(f"PREDICTION REPORT - Last {days} Days")
        report.append("=" * 80)
        
        for pred in predictions:
            report.append(f"\nPrediction ID: {pred[0]}")
            report.append(f"Patient: {pred[7] if pred[7] else 'N/A'}")
            report.append(f"Doctor: {pred[8] if pred[8] else 'N/A'}")
            report.append(f"Predicted Disease: {pred[5]}")
            report.append(f"Confidence: {pred[6]:.2%}")
            report.append(f"Risk Level: {pred[7]}")
            report.append(f"Date: {pred[9]}")
            report.append("-" * 40)
        
        return "\n".join(report)
    
    def close(self):
        self.db.close()