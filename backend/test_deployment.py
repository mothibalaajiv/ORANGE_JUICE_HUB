#!/usr/bin/env python3
"""
Test deployment configuration
"""
import os
from app import create_app, get_db

def test_deployment():
    """Test deployment configuration"""
    print("Testing deployment configuration...")
    
    # Test with production config
    app = create_app('production')
    
    with app.app_context():
        print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
        print(f"MongoDB URI: {app.config.get('MONGODB_URI', 'Not set')[:50]}...")
        print(f"Frontend URL: {app.config.get('FRONTEND_URL', 'Not set')}")
        
        try:
            db = get_db()
            if db is not None:
                print("Database connection: OK")
                # Test a simple query
                collections = db.list_collection_names()
                print(f"Collections: {collections}")
                
                # Test products count
                products_count = db.products.count_documents({'active': True, 'approved': True})
                print(f"Active products: {products_count}")
            else:
                print("Database connection: FAILED")
        except Exception as e:
            print(f"Database error: {e}")

if __name__ == '__main__':
    test_deployment()
