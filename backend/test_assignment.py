"""
Test script to debug assignment issues
"""
from app import create_app, get_db
from app.services.assignment_service import start_partner_assignment
from bson import ObjectId

def test_assignment():
    """Test the assignment system"""
    # Create app to initialize database
    app = create_app()
    with app.app_context():
        db = get_db()
    
        print("=== ASSIGNMENT DEBUG TEST ===")
        
        # Check if there are any delivery partners
        partners = list(db.delivery_partners.find())
        print(f"\nTotal delivery partners: {len(partners)}")
        
        for partner in partners:
            print(f"Partner: {partner.get('_id')}")
            print(f"  Status: {partner.get('status')}")
            print(f"  Location: {partner.get('currentLocation')}")
            print(f"  Vehicle: {partner.get('vehicleType')}")
        
        # Check if there are any recent orders
        recent_orders = list(db.orders.find().sort('createdAt', -1).limit(5))
        print(f"\nRecent orders: {len(recent_orders)}")
        
        for order in recent_orders:
            print(f"Order: {order.get('_id')}")
            print(f"  Status: {order.get('status')}")
            print(f"  Payment: {order.get('paymentStatus')}")
            print(f"  Assigned Partner: {order.get('assignedPartnerId')}")
            print(f"  Delivery Location: {order.get('deliveryLocation')}")
            print(f"  Created: {order.get('createdAt')}")
        
        # If there's a recent order, try to trigger assignment
        if recent_orders:
            latest_order = recent_orders[0]
            print(f"\n=== TRIGGERING ASSIGNMENT FOR ORDER {latest_order['_id']} ===")
            start_partner_assignment(str(latest_order['_id']))

if __name__ == "__main__":
    test_assignment()

