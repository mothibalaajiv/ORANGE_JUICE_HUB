#!/usr/bin/env python3
"""
Fix production data issues
"""
from app import create_app, get_db
from bson import ObjectId
from datetime import datetime

def fix_production_data():
    """Fix production data issues"""
    app = create_app('production')
    
    with app.app_context():
        db = get_db()
        
        print("Fixing production data...")
        
        try:
            # Test database connection
            db.admin.command('ping')
            print("Database connection successful")
            
            # Check if we have products
            products_count = db.products.count_documents({'active': True, 'approved': True})
            print(f"Active products: {products_count}")
            
            if products_count == 0:
                print("No active products found. Adding sample data...")
                add_sample_data(db)
            else:
                print("Products exist in database")
                
        except Exception as e:
            print(f"Database error: {e}")
            import traceback
            traceback.print_exc()

def add_sample_data(db):
    """Add sample data"""
    
    # Add sample brand if not exists
    sample_brand = {
        'name': 'Tropicana',
        'description': 'Premium orange juice brand',
        'logoUrl': 'https://via.placeholder.com/150x150/FFA500/FFFFFF?text=T',
        'website': 'https://tropicana.com',
        'active': True,
        'approved': True,
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow()
    }
    
    existing_brand = db.brands.find_one({'name': 'Tropicana'})
    if existing_brand:
        brand_id = existing_brand['_id']
        print(f"Using existing brand: {existing_brand['name']}")
    else:
        result = db.brands.insert_one(sample_brand)
        brand_id = result.inserted_id
        print(f"Created brand: {sample_brand['name']}")
    
    # Add sample products
    sample_products = [
        {
            'name': 'Tropicana Pure Premium Orange Juice',
            'sku': 'TROP-001',
            'volume': '1L',
            'price': 120.0,
            'category': 'Orange Juice',
            'description': 'Fresh, pure orange juice with no added sugar',
            'imageUrl': 'https://via.placeholder.com/300x300/FFA500/FFFFFF?text=Orange+Juice',
            'brandId': brand_id,
            'active': True,
            'approved': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        },
        {
            'name': 'Tropicana White Grape Juice',
            'sku': 'TROP-002',
            'volume': '500ml',
            'price': 80.0,
            'category': 'White Juice',
            'description': 'Refreshing white grape juice',
            'imageUrl': 'https://via.placeholder.com/300x300/32CD32/FFFFFF?text=White+Juice',
            'brandId': brand_id,
            'active': True,
            'approved': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
    ]
    
    for product in sample_products:
        existing = db.products.find_one({'sku': product['sku']})
        if not existing:
            db.products.insert_one(product)
            print(f"Created product: {product['name']}")
        else:
            # Update existing product to ensure it's active and approved
            db.products.update_one(
                {'sku': product['sku']},
                {'$set': {'active': True, 'approved': True}}
            )
            print(f"Updated product: {product['name']}")
    
    print("Sample data added successfully")

if __name__ == '__main__':
    fix_production_data()
