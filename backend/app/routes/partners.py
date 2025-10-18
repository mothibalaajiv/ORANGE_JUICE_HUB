from flask import Blueprint, request, jsonify
from app import get_db
from app.models.delivery_partner import DeliveryPartner
from app.utils.auth import token_required, role_required, get_current_user_id
from app.utils.geo import find_nearby_supermarkets_with_product
from app.services.assignment_service import accept_partner_assignment, reject_partner_assignment
from bson import ObjectId
from datetime import datetime

partners_bp = Blueprint('partners', __name__)


@partners_bp.route('/profile', methods=['GET'])
@role_required('partner')
def get_partner_profile():
    """Get delivery partner profile"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        partner_serialized = DeliveryPartner.serialize(partner)
        
        return jsonify(partner_serialized), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@partners_bp.route('/profile', methods=['PUT'])
@role_required('partner')
def update_partner_profile():
    """Update delivery partner profile"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Update fields
        update_fields = {}
        allowed_fields = ['vehicleType', 'vehicleNumber', 'currentLocation']
        for field in allowed_fields:
            if field in data:
                update_fields[field] = data[field]
        
        if update_fields:
            update_fields['updatedAt'] = datetime.utcnow()
            db.delivery_partners.update_one(
                {'_id': partner['_id']},
                {'$set': update_fields}
            )
        
        # Get updated partner
        partner = db.delivery_partners.find_one({'_id': partner['_id']})
        partner_serialized = DeliveryPartner.serialize(partner)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'partner': partner_serialized
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@partners_bp.route('/status', methods=['PUT'])
@role_required('partner')
def update_partner_status():
    """Update partner availability status"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        data = request.get_json()
        
        status = data.get('status')
        if status not in ['available', 'offline']:
            return jsonify({'error': 'Invalid status. Must be available or offline'}), 400
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Can't go offline if there's an active order
        if status == 'offline' and partner.get('currentOrderId'):
            return jsonify({'error': 'Cannot go offline with active order'}), 400
        
        # Update status
        db.delivery_partners.update_one(
            {'_id': partner['_id']},
            {'$set': {'status': status, 'updatedAt': datetime.utcnow()}}
        )
        
        return jsonify({'message': f'Status updated to {status}'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@partners_bp.route('/location', methods=['PUT'])
@role_required('partner')
def update_partner_location():
    """Update partner current location (for real-time tracking)"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        data = request.get_json()
        
        location = data.get('location')
        if not location or 'coordinates' not in location:
            return jsonify({'error': 'Invalid location format'}), 400
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Update location
        db.delivery_partners.update_one(
            {'_id': partner['_id']},
            {'$set': {'currentLocation': location, 'updatedAt': datetime.utcnow()}}
        )
        
        # If partner has active order, emit location update to user
        if partner.get('currentOrderId'):
            from app import socketio
            order_id = str(partner['currentOrderId'])
            socketio.emit(f'partner_location_{order_id}', {
                'location': location,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({'message': 'Location updated'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@partners_bp.route('/assignment/<order_id>/accept', methods=['POST'])
@role_required('partner')
def accept_assignment(order_id):
    """Accept order assignment"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Accept assignment
        success, message = accept_partner_assignment(order_id, partner['_id'])
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@partners_bp.route('/assignment/<order_id>/reject', methods=['POST'])
@role_required('partner')
def reject_assignment(order_id):
    """Reject order assignment"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Reject assignment
        success, message = reject_partner_assignment(order_id, partner['_id'])
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@partners_bp.route('/nearby-supermarkets', methods=['GET'])
@role_required('partner')
def get_nearby_supermarkets():
    """Get nearby supermarkets with product availability for current order"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Get current order
        current_order_id = partner.get('currentOrderId')
        if not current_order_id:
            return jsonify({'error': 'No active order'}), 400
        
        order = db.orders.find_one({'_id': current_order_id})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Get partner's current location
        partner_location = partner.get('currentLocation', {}).get('coordinates', [0, 0])
        
        # Get all product IDs from order
        product_ids = [item['productId'] for item in order['items']]
        
        # Find supermarkets that have ALL products
        # First get all inventories for these products
        inventories = list(db.supermarket_inventories.find({
            'productId': {'$in': product_ids},
            'quantity': {'$gt': 0}
        }))
        
        # Group by supermarket and check if all products available
        from collections import defaultdict
        supermarket_products = defaultdict(list)
        
        for inv in inventories:
            supermarket_products[str(inv['supermarketId'])].append(str(inv['productId']))
        
        # Filter supermarkets that have all products
        valid_supermarket_ids = []
        for sm_id, available_products in supermarket_products.items():
            if all(str(pid) in available_products for pid in product_ids):
                valid_supermarket_ids.append(ObjectId(sm_id))
        
        if not valid_supermarket_ids:
            return jsonify({'supermarkets': [], 'message': 'No supermarkets have all products in stock'}), 200
        
        # Get nearby supermarkets from valid list
        query = {
            '_id': {'$in': valid_supermarket_ids},
            'active': True,
            'approved': True,
            'location': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': partner_location
                    },
                    '$maxDistance': 10000  # 10km
                }
            }
        }
        
        supermarkets = list(db.supermarkets.find(query).limit(10))
        
        # Enrich with distance and inventory info
        from app.utils.geo import calculate_distance
        from app.models.supermarket import Supermarket
        
        for supermarket in supermarkets:
            # Calculate distance
            if 'location' in supermarket and 'coordinates' in supermarket['location']:
                distance = calculate_distance(partner_location, supermarket['location']['coordinates'])
                supermarket['distance'] = round(distance, 2)
            
            # Get inventory for this order's products
            sm_inventories = list(db.supermarket_inventories.find({
                'supermarketId': supermarket['_id'],
                'productId': {'$in': product_ids}
            }))
            supermarket['inventoryItems'] = len(sm_inventories)
        
        # Sort by distance
        supermarkets.sort(key=lambda x: x.get('distance', float('inf')))
        
        supermarkets_serialized = [Supermarket.serialize(s) for s in supermarkets]
        
        return jsonify({
            'supermarkets': supermarkets_serialized,
            'orderId': str(current_order_id)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@partners_bp.route('/assigned-orders', methods=['GET'])
@role_required('partner')
def get_assigned_orders():
    """Get orders assigned to this partner"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Get assigned orders that are still active
        assigned_orders = list(db.orders.find({
            'assignedPartnerId': partner['_id'],
            'status': {'$in': ['partner_assigned', 'partner_accepted', 'picked_up', 'out_for_delivery']}
        }).sort('createdAt', -1))
        
        # Serialize orders
        from app.models.order import Order
        orders_serialized = [Order.serialize(order) for order in assigned_orders]
        
        return jsonify(orders_serialized), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@partners_bp.route('/earnings', methods=['GET'])
@role_required('partner')
def get_earnings():
    """Get partner earnings and statistics"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Get completed orders
        completed_orders = list(db.orders.find({
            'assignedPartnerId': partner['_id'],
            'status': 'delivered'
        }))
        
        # Calculate statistics
        total_earnings = sum(order.get('deliveryFee', 0) for order in completed_orders)
        total_deliveries = len(completed_orders)
        
        # Get earnings by date (last 30 days)
        from datetime import timedelta
        from collections import defaultdict
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_orders = [o for o in completed_orders if o.get('actualDeliveryTime', datetime.min) > thirty_days_ago]
        
        daily_earnings = defaultdict(float)
        for order in recent_orders:
            if order.get('actualDeliveryTime'):
                date_key = order['actualDeliveryTime'].strftime('%Y-%m-%d')
                daily_earnings[date_key] += order.get('deliveryFee', 0)
        
        earnings_chart = [{'date': k, 'amount': v} for k, v in sorted(daily_earnings.items())]
        
        return jsonify({
            'totalEarnings': total_earnings,
            'totalDeliveries': total_deliveries,
            'rating': partner.get('rating', 0),
            'earningsChart': earnings_chart
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
