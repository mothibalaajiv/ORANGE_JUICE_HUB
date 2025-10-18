from datetime import datetime
from bson import ObjectId


class Brand:
    """Brand model"""
    
    @staticmethod
    def create(data):
        """Create a new brand"""
        brand_data = {
            'userId': ObjectId(data.get('userId')),
            'name': data.get('name'),
            'description': data.get('description', ''),
            'logoUrl': data.get('logoUrl', ''),
            'website': data.get('website', ''),
            'approved': False,  # Admin approval required
            'active': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'rating': 0,
            'totalSales': 0,
            'totalProducts': 0,
            'contactEmail': data.get('contactEmail', ''),
            'contactPhone': data.get('contactPhone', '')
        }
        return brand_data
    
    @staticmethod
    def serialize(brand):
        """Serialize brand document for JSON response"""
        if not brand:
            return None
        
        brand['_id'] = str(brand['_id'])
        brand['userId'] = str(brand['userId'])
        
        if 'createdAt' in brand:
            brand['createdAt'] = brand['createdAt'].isoformat()
        if 'updatedAt' in brand:
            brand['updatedAt'] = brand['updatedAt'].isoformat()
        
        return brand
