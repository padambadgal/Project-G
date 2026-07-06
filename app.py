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
# REGISTER API
# =========================
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    success, message = auth.register_user(
        username=data["username"],
        password=data["password"],
        role=data["role"],
        full_name=data["full_name"],
        email=data.get("email"),
        phone=data.get("phone")
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
            "user": user
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


if __name__ == "__main__":
    app.run(debug=True)