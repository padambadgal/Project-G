# utils/helper.py
import datetime
import random
import string

def generate_id(prefix="P"):
    """Generate a unique ID"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"

def format_date(date_str):
    """Format date string"""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime("%B %d, %Y at %I:%M %p")
    except:
        return date_str

def validate_symptoms(symptoms):
    """Validate symptoms input"""
    if not symptoms or len(symptoms.strip()) < 3:
        return False, "Please enter valid symptoms"
    return True, ""

def calculate_risk_level(confidence):
    """Calculate risk level based on confidence score"""
    if confidence >= 0.8:
        return "High"
    elif confidence >= 0.5:
        return "Medium"
    else:
        return "Low"

def generate_recommendation(disease, risk_level):
    """Generate recommendation based on disease and risk level"""
    recommendations = {
        "Low": f"Monitor symptoms and consult a doctor if they persist. For {disease}, maintain proper hygiene and follow standard health guidelines.",
        "Medium": f"Schedule a doctor's appointment within 1-2 weeks. For {disease}, consider lifestyle modifications and medication if prescribed.",
        "High": f"Immediate medical attention recommended. For {disease}, please visit a hospital emergency department or consult a specialist today."
    }
    return recommendations.get(risk_level, "Consult a healthcare professional for personalized advice.")