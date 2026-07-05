# check_all_doctors.py
from database.database import Database

def check_all_doctors():
    print("\n" + "=" * 70)
    print("👨‍⚕️ DOCTOR DATABASE CHECK")
    print("=" * 70)
    
    db = Database()
    db.connect()
    
    # 1. Count all doctors
    count = db.fetch_one("SELECT COUNT(*) FROM doctors")
    total = count[0] if count else 0
    print(f"\n📊 Total Doctors: {total}")
    
    # 2. List all doctors
    doctors = db.fetch_all("SELECT * FROM doctors ORDER BY created_at DESC")
    
    if doctors:
        print("\n📋 ALL DOCTORS:")
        print("-" * 90)
        print(f"{'#':<3} {'Doctor ID':<15} {'Name':<25} {'Specialization':<25} {'Experience':<10}")
        print("-" * 90)
        
        for i, d in enumerate(doctors, 1):
            exp = str(d['years_experience']) if d['years_experience'] else 'N/A'
            spec = d['specialization'] if d['specialization'] else 'N/A'
            print(f"{i:<3} {d['doctor_id']:<15} {d['full_name']:<25} {spec:<25} {exp:<10}")
    else:
        print("\n⚠️ No doctors found in database!")
    
    # 3. Detailed view option
    if doctors:
        print("\n" + "=" * 70)
        view = input("🔍 Enter Doctor ID for details (or press Enter to skip): ").strip()
        
        if view:
            doctor = db.fetch_one("SELECT * FROM doctors WHERE doctor_id = ?", (view,))
            if doctor:
                print("\n📋 DOCTOR DETAILS:")
                print("-" * 50)
                print(f"  ID            : {doctor['doctor_id']}")
                print(f"  Name          : {doctor['full_name']}")
                print(f"  Specialization: {doctor['specialization']}")
                print(f"  Experience    : {doctor['years_experience']} years")
                print(f"  Contact       : {doctor['contact']}")
                print(f"  Email         : {doctor['email']}")
                print(f"  Registered    : {doctor['created_at']}")
                
                # Check if this doctor has predictions
                predictions = db.fetch_one(
                    "SELECT COUNT(*) FROM predictions WHERE doctor_id = ?",
                    (view,)
                )
                pred_count = predictions[0] if predictions else 0
                print(f"  Predictions   : {pred_count}")
            else:
                print(f"\n❌ Doctor with ID '{view}' not found.")
    
    db.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_all_doctors()