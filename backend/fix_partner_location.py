"""
Fix delivery partner location to Mumbai coordinates
"""
from app import create_app, get_db
from bson import ObjectId

def fix_partner_location():
    """Update delivery partner location to Mumbai"""
    app = create_app()
    with app.app_context():
        db = get_db()
        
        # Update all delivery partners to Mumbai location
        result = db.delivery_partners.update_many(
            {},
            {
                '$set': {
                    'currentLocation': {
                        'type': 'Point',
                        'coordinates': [72.8777, 19.076]  # Mumbai coordinates
                    }
                }
            }
        )
        
        print(f"Updated {result.modified_count} delivery partners to Mumbai location")
        
        # Verify the update
        partners = list(db.delivery_partners.find())
        for partner in partners:
            print(f"Partner: {partner.get('_id')}")
            print(f"  Status: {partner.get('status')}")
            print(f"  Location: {partner.get('currentLocation')}")

if __name__ == "__main__":
    fix_partner_location()
