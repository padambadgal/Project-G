class AIEngine:

    def __init__(self):
        # symptom weight system
        self.symptom_weights = {
            "fever": 2,
            "cough": 2,
            "cold": 1,
            "chest pain": 5,
            "headache": 2,
            "vomiting": 3,
            "fatigue": 3,
            "weight loss": 4,
            "body pain": 2,
            "breathing problem": 5
        }

    def analyze(self, symptoms_text):

        symptoms = symptoms_text.lower().split(",")

        score = 0

        for s in symptoms:
            s = s.strip()
            score += self.symptom_weights.get(s, 1)

        # =========================
        # DISEASE PREDICTION ENGINE
        # =========================

        if score >= 10:
            disease = "Heart Disease"
            risk = "High"
            confidence = 0.92

        elif score >= 7:
            disease = "Viral Infection"
            risk = "Medium"
            confidence = 0.85

        elif score >= 4:
            disease = "Flu"
            risk = "Low"
            confidence = 0.80

        else:
            disease = "Minor Infection"
            risk = "Low"
            confidence = 0.70

        return {
            "disease": disease,
            "risk": risk,
            "confidence": confidence
        }