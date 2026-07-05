# reports/reports.py
from database.database import Database
from datetime import datetime, timedelta


class Reports:
    def __init__(self):
        self.db = Database()
        self.db.connect()

    def get_prediction_history(self, days=30):
        start_date = datetime.now() - timedelta(days=days)

        query = """
        SELECT
            p.*,
            pat.full_name AS patient_name,
            doc.full_name AS doctor_name
        FROM predictions p
        LEFT JOIN users pat ON pat.id = p.patient_id AND pat.role = 'patient'
        LEFT JOIN users doc ON doc.id = p.doctor_id AND doc.role = 'doctor'
        WHERE p.predicted_at >= ?
        ORDER BY p.predicted_at DESC
        """

        return self.db.fetch_all(
            query,
            (start_date.strftime("%Y-%m-%d %H:%M:%S"),),
        )

    def get_doctor_predictions(self, doctor_id):
        query = """
        SELECT
            p.*,
            pat.full_name AS patient_name
        FROM predictions p
        LEFT JOIN users pat ON pat.id = p.patient_id
        WHERE p.doctor_id = ?
        ORDER BY p.predicted_at DESC
        """

        return self.db.fetch_all(query, (doctor_id,))

    def get_patient_predictions(self, patient_id):
        query = """
        SELECT
            p.*,
            doc.full_name AS doctor_name
        FROM predictions p
        LEFT JOIN users doc ON doc.id = p.doctor_id
        WHERE p.patient_id = ?
        ORDER BY p.predicted_at DESC
        """

        return self.db.fetch_all(query, (patient_id,))

    def get_prediction_statistics(self):
        total = self.db.fetch_one("SELECT COUNT(*) FROM predictions")[0]

        disease_stats = self.db.fetch_all("""
            SELECT predicted_disease, COUNT(*) as count
            FROM predictions
            GROUP BY predicted_disease
            ORDER BY COUNT(*) DESC
        """)

        risk_stats = self.db.fetch_all("""
            SELECT risk_level, COUNT(*) as count
            FROM predictions
            GROUP BY risk_level
        """)

        return {
            "total_predictions": total,
            "disease_distribution": disease_stats,
            "risk_distribution": risk_stats,
        }

    def get_doctor_statistics(self, doctor_id):
        query = """
        SELECT
            COUNT(*) as total,
            AVG(confidence) as avg_conf,
            COUNT(DISTINCT patient_id) as unique_patients
        FROM predictions
        WHERE doctor_id = ?
        """

        result = self.db.fetch_one(query, (doctor_id,))

        if result:
            return {
                "total_predictions": result['total'] or 0,
                "avg_confidence": result['avg_conf'] or 0,
                "unique_patients": result['unique_patients'] or 0,
            }
        return {"total_predictions": 0, "avg_confidence": 0, "unique_patients": 0}

    def close(self):
        self.db.close()