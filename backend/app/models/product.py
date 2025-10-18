from datetime import datetime
from bson import ObjectId


class Product:
    """Product model"""
    
    @staticmethod
    def create(data):
        """Create a new product"""
        product_data = {
            'brandId': ObjectId(data.get('brandId')),
            'name': data.get('name'),
            'sku': data.get('sku'),
            'volume': data.get('volume'),  # e.g., "1L", "500ml"
            'price': float(data.get('price')),
            'imageUrl': data.get('imageUrl', ''),
            'description': data.get('description', ''),
            'category': data.get('category', 'orange'),  # orange, white, mixed
            'nutritionalInfo': data.get('nutritionalInfo', {}),
            'active': data.get('active', True),
            'approved': False,  # Admin approval required
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'rating': 0,
            'reviewCount': 0,
            'tags': data.get('tags', [])
        }
        return product_data
    
    @staticmethod
    def serialize(product):
        """Serialize product document for JSON response"""
        if not product:
            return None
        
        product['_id'] = str(product['_id'])
        product['brandId'] = str(product['brandId'])
        
        if 'createdAt' in product:
            product['createdAt'] = product['createdAt'].isoformat()
        if 'updatedAt' in product:
            product['updatedAt'] = product['updatedAt'].isoformat()
        
        return product
