from datetime import datetime
from bson import ObjectId


class DeliveryPartner:
    """Delivery Partner model"""
    
    STATUS_AVAILABLE = 'available'
    STATUS_BUSY = 'busy'
    STATUS_OFFLINE = 'offline'
    
    @staticmethod
    def create(data):
        """Create a new delivery partner profile"""
        partner_data = {
            'userId': ObjectId(data.get('userId')),
            'vehicleType': data.get('vehicleType', 'bike'),  # bike, scooter, car
            'vehicleNumber': data.get('vehicleNumber', ''),
            'currentLocation': data.get('currentLocation', {
                'type': 'Point',
                'coordinates': [0, 0]  # [longitude, latitude]
            }),
            'status': DeliveryPartner.STATUS_OFFLINE,
            'rating': 0,
            'totalDeliveries': 0,
            'totalEarnings': 0,
            'onlineHours': 0,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'verified': False,
            'documents': {
                'licenseUrl': data.get('licenseUrl', ''),
                'aadharUrl': data.get('aadharUrl', ''),
                'vehicleRcUrl': data.get('vehicleRcUrl', '')
            },
            'bankDetails': {
                'accountNumber': data.get('accountNumber', ''),
                'ifscCode': data.get('ifscCode', ''),
                'accountHolderName': data.get('accountHolderName', '')
            },
            'currentOrderId': None
        }
        return partner_data
    
    @staticmethod
    def serialize(partner):
        """Serialize delivery partner document for JSON response"""
        if not partner:
            return None
        
        partner['_id'] = str(partner['_id'])
        partner['userId'] = str(partner['userId'])
        
        if partner.get('currentOrderId'):
            partner['currentOrderId'] = str(partner['currentOrderId'])
        
        if 'createdAt' in partner:
            partner['createdAt'] = partner['createdAt'].isoformat()
        if 'updatedAt' in partner:
            partner['updatedAt'] = partner['updatedAt'].isoformat()
        
        return partner
