from datetime import datetime
from bson import ObjectId


class Order:
    """Order model"""
    
    STATUS_AWAITING_ASSIGNMENT = 'awaiting_partner_assignment'
    STATUS_PARTNER_ASSIGNED = 'partner_assigned'
    STATUS_PARTNER_ACCEPTED = 'partner_accepted'
    STATUS_PICKUP_REQUESTED = 'pickup_requested'
    STATUS_READY_FOR_PICKUP = 'ready_for_pickup'
    STATUS_PICKUP_REJECTED = 'pickup_rejected'
    STATUS_PICKED_UP = 'picked_up'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    
    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_FAILED = 'failed'
    PAYMENT_REFUNDED = 'refunded'
    
    @staticmethod
    def create(data):
        """Create a new order"""
        order_data = {
            'userId': ObjectId(data.get('userId')),
            'items': [
                {
                    'productId': ObjectId(item['productId']),
                    'qty': item['qty'],
                    'unitPrice': float(item['unitPrice']),
                    'name': item.get('name', ''),
                    'imageUrl': item.get('imageUrl', '')
                }
                for item in data.get('items', [])
            ],
            'totalAmount': float(data.get('totalAmount')),
            'subtotal': float(data.get('subtotal', 0)),
            'deliveryFee': float(data.get('deliveryFee', 0)),
            'tax': float(data.get('tax', 0)),
            'paymentStatus': Order.PAYMENT_PENDING,
            'paymentMethod': data.get('paymentMethod', 'razorpay'),
            'assignedPartnerId': None,
            'partnerAssignedAt': None,
            'partnerAcceptedAt': None,
            'partnerAccepted': False,
            'status': Order.STATUS_AWAITING_ASSIGNMENT,
            'deliveryAddress': data.get('deliveryAddress'),
            'deliveryLocation': data.get('deliveryLocation', {
                'type': 'Point',
                'coordinates': [0, 0]
            }),
            'supermarketPickedFrom': None,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'estimatedDeliveryTime': None,
            'actualDeliveryTime': None,
            'logs': [
                {
                    'status': Order.STATUS_AWAITING_ASSIGNMENT,
                    'timestamp': datetime.utcnow(),
                    'note': 'Order created'
                }
            ],
            'customerNotes': data.get('customerNotes', ''),
            'rating': None,
            'review': None
        }
        return order_data
    
    @staticmethod
    def add_log(order_id, db, status, note=''):
        """Add a log entry to order"""
        log_entry = {
            'status': status,
            'timestamp': datetime.utcnow(),
            'note': note
        }
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$push': {'logs': log_entry},
                '$set': {'updatedAt': datetime.utcnow()}
            }
        )
    
    @staticmethod
    def serialize(order):
        """Serialize order document for JSON response"""
        if not order:
            return None
        
        order['_id'] = str(order['_id'])
        order['userId'] = str(order['userId'])
        
        if order.get('assignedPartnerId'):
            order['assignedPartnerId'] = str(order['assignedPartnerId'])
        
        if order.get('supermarketPickedFrom'):
            order['supermarketPickedFrom'] = str(order['supermarketPickedFrom'])
        
        # Serialize items
        for item in order.get('items', []):
            item['productId'] = str(item['productId'])
        
        # Serialize datetime fields
        if 'createdAt' in order:
            order['createdAt'] = order['createdAt'].isoformat()
        if 'updatedAt' in order:
            order['updatedAt'] = order['updatedAt'].isoformat()
        if 'partnerAssignedAt' in order and order['partnerAssignedAt']:
            order['partnerAssignedAt'] = order['partnerAssignedAt'].isoformat()
        if 'partnerAcceptedAt' in order and order['partnerAcceptedAt']:
            order['partnerAcceptedAt'] = order['partnerAcceptedAt'].isoformat()
        if 'estimatedDeliveryTime' in order and order['estimatedDeliveryTime']:
            order['estimatedDeliveryTime'] = order['estimatedDeliveryTime'].isoformat()
        if 'actualDeliveryTime' in order and order['actualDeliveryTime']:
            order['actualDeliveryTime'] = order['actualDeliveryTime'].isoformat()
        
        # Serialize logs
        for log in order.get('logs', []):
            if 'timestamp' in log:
                log['timestamp'] = log['timestamp'].isoformat()
        
        return order
