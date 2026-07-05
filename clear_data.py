# clear_data.py
import sqlite3
from database.database import Database

def clear_all_data():
    print("=" * 60)
    print("🗑️  CLEARING ALL DATA (Except Admin)")
    print("=" * 60)
    
    db = Database()
    db.connect()
    
    # Show current counts
    print("\n📊 Current Records:")
    print("-" * 40)
    
    count_before = {}
    tables = ['patients', 'doctors', 'predictions', 'users']
    for table in tables:
        result = db.fetch_one(f"SELECT COUNT(*) FROM {table}")
        count_before[table] = result[0] if result else 0
        print(f"  {table}: {count_before[table]}")
    
    print("\n" + "=" * 60)
    confirm = input("⚠️  This will delete ALL records except admin. Continue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("\n❌ Operation cancelled.")
        db.close()
        return
    
    try:
        # Delete in correct order (respect foreign keys)
        print("\n🗑️  Deleting predictions...")
        db.execute_query("DELETE FROM predictions")
        
        print("🗑️  Deleting patients...")
        db.execute_query("DELETE FROM patients")
        
        print("🗑️  Deleting doctors...")
        db.execute_query("DELETE FROM doctors")
        
        print("🗑️  Deleting users (except admin)...")
        db.execute_query("DELETE FROM users WHERE username != 'admin'")
        
        # Verify admin still exists
        admin = db.fetch_one("SELECT * FROM users WHERE username = 'admin'")
        if admin:
            print("\n✅ Admin user preserved!")
            print(f"   Username: {admin['username']}")
            print(f"   Full Name: {admin['full_name']}")
            print(f"   Role: {admin['role']}")
        else:
            print("\n❌ ERROR: Admin user was deleted! Recreating...")
            from authentication.login import Authentication
            auth = Authentication()
            auth.initialize_admin()
        
        # Show new counts
        print("\n📊 Records After Cleanup:")
        print("-" * 40)
        for table in tables:
            result = db.fetch_one(f"SELECT COUNT(*) FROM {table}")
            count_after = result[0] if result else 0
            print(f"  {table}: {count_after}")
        
        print("\n✅ All data cleared successfully!")
        print("   - Patients: 0")
        print("   - Doctors: 0")
        print("   - Predictions: 0")
        print("   - Users: 1 (admin only)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    db.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    clear_all_data()