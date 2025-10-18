"""
Create Admin User Script
Run this to create the first admin user who can approve brands and supermarkets
"""
from pymongo import MongoClient
from datetime import datetime
import bcrypt
import os

def create_admin():
    """Create an admin user in the database"""
    
    print("=" * 60)
    print("Creating Admin User for Tangy Town")
    print("=" * 60)
    
    # Admin credentials
    ADMIN_EMAIL = "admin@tangytown.com"
    ADMIN_PASSWORD = "Admin@123"  # Change this after first login!
    ADMIN_NAME = "System Administrator"
    
    try:
        # Connect to MongoDB
        mongodb_uri = 'mongodb+srv://mothicaptures:mothi@cluster0.858fyte.mongodb.net/tangytown'
        db_name = 'tangytown'
        
        if not mongodb_uri:
            print("Error: MONGODB_URI not found in .env file")
            return False
        
        # Connect to MongoDB
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000
        )
        db = client[db_name]
        
        print(f"\nAdmin Credentials:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   Role: admin")
        
        # Check if admin already exists
        existing_admin = db.users.find_one({'email': ADMIN_EMAIL})
        if existing_admin:
            print(f"\nAdmin user already exists!")
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Created: {existing_admin.get('createdAt')}")
            print(f"\n   Use these credentials to login:")
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Password: Admin@123")
            return True
        
        # Hash password
        password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user
        admin_data = {
            'name': ADMIN_NAME,
            'email': ADMIN_EMAIL,
            'passwordHash': password_hash,
            'role': 'admin',
            'phone': '+91-1234567890',
            'address': 'Tangy Town HQ',
            'location': {
                'type': 'Point',
                'coordinates': [0, 0]
            },
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'active': True,
            'verified': True,
            'meta': {
                'isSystemAdmin': True,
                'permissions': ['all']
            }
        }
        
        # Insert admin user
        result = db.users.insert_one(admin_data)
        
        print(f"\nAdmin user created successfully!")
        print(f"   User ID: {result.inserted_id}")
        print(f"\n" + "=" * 60)
        print("ADMIN SETUP COMPLETE!")
        print("=" * 60)
        print(f"\nLogin Credentials:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"\nIMPORTANT SECURITY NOTES:")
        print(f"   1. Change the password after first login!")
        print(f"   2. Go to: Admin Dashboard -> Profile -> Change Password")
        print(f"   3. Use a strong password (min 8 chars, uppercase, lowercase, numbers)")
        print(f"\nNext Steps:")
        print(f"   1. Go to: http://localhost:3000/login")
        print(f"   2. Login with admin credentials above")
        print(f"   3. Go to: Admin Dashboard -> Approvals")
        print(f"   4. Approve pending brands and supermarkets")
        print(f"\n" + "=" * 60)
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\nError creating admin user: {str(e)}")
        return False


if __name__ == "__main__":
    create_admin()
