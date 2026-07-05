# check_all_patients.py
import sys
from patient.patient import Patient
from database.database import Database

def check_all():
    print("\n" + "=" * 70)
    print("🔍 PATIENT DATABASE CHECK")
    print("=" * 70)
    
    db = Database()
    db.connect()
    
    # 1. Count all patients
    count = db.fetch_one("SELECT COUNT(*) FROM patients")
    total = count[0] if count else 0
    print(f"\n📊 Total Patients: {total}")
    
    # 2. List all patients
    patients = db.fetch_all("SELECT * FROM patients ORDER BY created_at DESC")
    
    if patients:
        print("\n📋 ALL PATIENTS:")
        print("-" * 70)
        print(f"{'#':<3} {'Patient ID':<15} {'Name':<25} {'Age':<5} {'Gender':<8} {'Contact':<15}")
        print("-" * 70)
        
        for i, p in enumerate(patients, 1):
            age = str(p['age']) if p['age'] else 'N/A'
            contact = p['contact'] if p['contact'] else 'N/A'
            gender = p['gender'] if p['gender'] else 'N/A'
            print(f"{i:<3} {p['patient_id']:<15} {p['full_name']:<25} {age:<5} {gender:<8} {contact:<15}")
    else:
        print("\n⚠️ No patients found in database!")
    
    # 3. Search option
    print("\n" + "=" * 70)
    search = input("🔎 Search for patient (name/ID) or press Enter to exit: ").strip()
    
    if search:
        results = db.fetch_all(
            "SELECT * FROM patients WHERE patient_id LIKE ? OR full_name LIKE ?",
            (f"%{search}%", f"%{search}%")
        )
        
        if results:
            print(f"\n✅ Found {len(results)} matching patients:")
            print("-" * 70)
            for p in results:
                print(f"  • {p['patient_id']} - {p['full_name']} (Age: {p['age']})")
        else:
            print(f"\n❌ No patient found matching '{search}'")
    
    db.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_all()