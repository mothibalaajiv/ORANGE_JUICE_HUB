from datetime import datetime
from bson import ObjectId


class Supermarket:
    """Supermarket model"""
    
    @staticmethod
    def create(data):
        """Create a new supermarket"""
        supermarket_data = {
            'userId': ObjectId(data.get('userId')),
            'name': data.get('name'),
            'address': data.get('address'),
            'location': data.get('location', {
                'type': 'Point',
                'coordinates': [0, 0]  # [longitude, latitude]
            }),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'openingHours': data.get('openingHours', {
                'monday': {'open': '09:00', 'close': '21:00'},
                'tuesday': {'open': '09:00', 'close': '21:00'},
                'wednesday': {'open': '09:00', 'close': '21:00'},
                'thursday': {'open': '09:00', 'close': '21:00'},
                'friday': {'open': '09:00', 'close': '21:00'},
                'saturday': {'open': '09:00', 'close': '21:00'},
                'sunday': {'open': '10:00', 'close': '20:00'}
            }),
            'approved': False,
            'active': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'rating': 0,
            'totalSales': 0
        }
        return supermarket_data
    
    @staticmethod
    def serialize(supermarket):
        """Serialize supermarket document for JSON response"""
        if not supermarket:
            return None
        
        supermarket['_id'] = str(supermarket['_id'])
        supermarket['userId'] = str(supermarket['userId'])
        
        if 'createdAt' in supermarket:
            supermarket['createdAt'] = supermarket['createdAt'].isoformat()
        if 'updatedAt' in supermarket:
            supermarket['updatedAt'] = supermarket['updatedAt'].isoformat()
        
        return supermarket


class SupermarketInventory:
    """Supermarket Inventory model"""
    
    @staticmethod
    def create(data):
        """Create a new inventory item"""
        inventory_data = {
            'supermarketId': ObjectId(data.get('supermarketId')),
            'productId': ObjectId(data.get('productId')),
            'quantity': int(data.get('quantity', 0)),
            'priceOverride': data.get('priceOverride'),  # Optional custom pricing
            'lastUpdated': datetime.utcnow(),
            'createdAt': datetime.utcnow()
        }
        return inventory_data
    
    @staticmethod
    def serialize(inventory):
        """Serialize inventory document for JSON response"""
        if not inventory:
            return None
        
        inventory['_id'] = str(inventory['_id'])
        inventory['supermarketId'] = str(inventory['supermarketId'])
        inventory['productId'] = str(inventory['productId'])
        
        if 'createdAt' in inventory:
            inventory['createdAt'] = inventory['createdAt'].isoformat()
        if 'lastUpdated' in inventory:
            inventory['lastUpdated'] = inventory['lastUpdated'].isoformat()
        
        return inventory
