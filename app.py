from flask import Flask, request, jsonify, render_template
from authentication.login import Authentication

app = Flask(__name__)

auth = Authentication()

# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return render_template("login.html")


# =========================
# REGISTER API (UPDATED)
# =========================
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    success, message = auth.register_user(
        username=data["username"],
        password=data["password"],
        role=data["role"],
        full_name=data["full_name"],

        # common fields
        email=data.get("email"),
        phone=data.get("phone"),
        gender=data.get("gender"),
        age=data.get("age"),

        # patient profile fields
        address=data.get("address"),
        medical_history=data.get("medical_history"),
        emergency_contact=data.get("emergency_contact"),
        blood_group=data.get("blood_group"),

        # doctor profile fields
        specialization=data.get("specialization"),
        years_experience=data.get("years_experience"),
        qualification=data.get("qualification"),
        hospital_name=data.get("hospital_name"),
        consultation_fee=data.get("consultation_fee"),
        bio=data.get("bio"),
        available_days=data.get("available_days"),
        available_time=data.get("available_time")
    )

    return jsonify({
        "success": success,
        "message": message
    })


# =========================
# LOGIN API
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = auth.login(data["username"], data["password"])

    if user:
        return jsonify({
            "success": True,
            "role": user["role"],
            "user": dict(user)   # safer conversion
        })

    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    })


# =========================
# DASHBOARDS
# =========================
@app.route("/doctor")
def doctor_page():
    return render_template("doctor_dashboard.html")


@app.route("/patient")
def patient_page():
    return render_template("patient_dashboard.html")


@app.route("/admin")
def admin_page():
    return render_template("admin_dashboard.html")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)