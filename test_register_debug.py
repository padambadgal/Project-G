# test_register_debug.py
from authentication.login import Authentication

def test_registration():
    print("=" * 60)
    print("📝 TEST REGISTRATION (DEBUG)")
    print("=" * 60)
    
    auth = Authentication()
    
    # Test data
    username = "test_user2"
    password = "test123"
    role = "patient"
    full_name = "Test User 2"
    email = "test2@email.com"
    phone = "1234567890"
    gender = "Male"
    age = 25
    
    print(f"\n📋 Test Data:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Role: {role}")
    print(f"   Full Name: {full_name}")
    print(f"   Email: {email}")
    print(f"   Phone: {phone}")
    print(f"   Gender: {gender}")
    print(f"   Age: {age}")
    
    # Register
    success, message = auth.register_user(
        username=username,
        password=password,
        role=role,
        full_name=full_name,
        email=email,
        phone=phone,
        gender=gender,
        age=age
    )
    
    print(f"\n📋 Result:")
    print(f"   Success: {success}")
    print(f"   Message: {message}")
    
    # Verify
    if success:
        user = auth.get_user_by_username(username)
        if user:
            print(f"\n✅ User found in database:")
            print(f"   ID: {user['id']}")
            print(f"   Username: {user['username']}")
            print(f"   Role: {user['role']}")
            print(f"   Gender: {user.get('gender', 'N/A')}")
            print(f"   Age: {user.get('age', 'N/A')}")
        else:
            print(f"\n❌ User not found in database!")
    
    auth.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_registration()