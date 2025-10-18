from flask import Blueprint, request, jsonify
from app import get_db, socketio
from app.models.order import Order
from app.utils.auth import token_required, role_required, get_current_user_id, get_current_user_role
from app.services.assignment_service import start_partner_assignment
from bson import ObjectId
from datetime import datetime

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('', methods=['POST'])
@token_required
def create_order():
    """Create a new order"""
    try:
        db = get_db()
        data = request.get_json()
        user_id = get_current_user_id()
        
        # Validate required fields
        required_fields = ['items', 'totalAmount', 'deliveryAddress', 'deliveryLocation']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate items
        if not isinstance(data['items'], list) or len(data['items']) == 0:
            return jsonify({'error': 'Items must be a non-empty array'}), 400
        
        # Set userId
        data['userId'] = user_id
        
        # Create order
        order_data = Order.create(data)
        result = db.orders.insert_one(order_data)
        order_id = result.inserted_id
        
        # Get created order
        order = db.orders.find_one({'_id': order_id})
        order_serialized = Order.serialize(order)
        
        # Note: Partner assignment should be triggered after payment confirmation
        # For now, we'll return the order. Payment webhook will trigger assignment.
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order_serialized
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """Get order details"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        role = get_current_user_role()
        
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Authorization check
        if role == 'user' and str(order['userId']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        
        if role == 'partner':
            partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
            if partner and str(order.get('assignedPartnerId')) != str(partner['_id']):
                return jsonify({'error': 'Not authorized'}), 403
        
        # Enrich with user info
        user = db.users.find_one({'_id': order['userId']})
        if user:
            order['user'] = {
                '_id': str(user['_id']),
                'name': user['name'],
                'phone': user.get('phone', '')
            }
        
        # Enrich with partner info
        if order.get('assignedPartnerId'):
            partner_doc = db.delivery_partners.find_one({'_id': order['assignedPartnerId']})
            if partner_doc:
                partner_user = db.users.find_one({'_id': partner_doc['userId']})
                order['partner'] = {
                    '_id': str(partner_doc['_id']),
                    'name': partner_user.get('name', '') if partner_user else '',
                    'phone': partner_user.get('phone', '') if partner_user else '',
                    'vehicleType': partner_doc.get('vehicleType', ''),
                    'rating': partner_doc.get('rating', 0),
                    'currentLocation': partner_doc.get('currentLocation')
                }
        
        # Enrich with supermarket info
        if order.get('supermarketPickedFrom'):
            supermarket = db.supermarkets.find_one({'_id': order['supermarketPickedFrom']})
            if supermarket:
                from app.models.supermarket import Supermarket
                order['supermarket'] = Supermarket.serialize(supermarket)
        
        order_serialized = Order.serialize(order)
        
        return jsonify(order_serialized), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('', methods=['GET'])
@token_required
def get_orders():
    """Get orders for current user"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        role = get_current_user_role()
        
        # Build query based on role
        query = {}
        
        if role == 'user':
            query['userId'] = ObjectId(user_id)
        
        elif role == 'partner':
            partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
            if partner:
                query['assignedPartnerId'] = partner['_id']
        
        elif role == 'brand':
            # Get orders containing brand's products
            brand = db.brands.find_one({'userId': ObjectId(user_id)})
            if brand:
                products = list(db.products.find({'brandId': brand['_id']}))
                product_ids = [p['_id'] for p in products]
                query['items.productId'] = {'$in': product_ids}
        
        # Status filter
        if request.args.get('status'):
            query['status'] = request.args.get('status')
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        
        # Get orders
        orders = list(db.orders.find(query).sort('createdAt', -1).skip(skip).limit(limit))
        total = db.orders.count_documents(query)
        
        orders_serialized = [Order.serialize(o) for o in orders]
        
        return jsonify({
            'orders': orders_serialized,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>/picked-up', methods=['POST'])
@role_required('partner')
def mark_picked_up(order_id):
    """Partner marks order as picked up from supermarket"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify partner is assigned to this order
        if str(order.get('assignedPartnerId')) != str(partner['_id']):
            return jsonify({'error': 'Not authorized'}), 403
        
        # Verify order status
        if order['status'] not in [Order.STATUS_PARTNER_ASSIGNED, Order.STATUS_PARTNER_ACCEPTED]:
            return jsonify({'error': 'Invalid order status. Order must be assigned or accepted by partner.'}), 400
        
        # Get supermarket ID from request
        supermarket_id = data.get('supermarketId')
        if not supermarket_id:
            return jsonify({'error': 'supermarketId is required'}), 400
        
        # Decrement stock for each item
        for item in order['items']:
            db.supermarket_inventories.update_one(
                {
                    'supermarketId': ObjectId(supermarket_id),
                    'productId': item['productId']
                },
                {'$inc': {'quantity': -item['qty']}, '$set': {'lastUpdated': datetime.utcnow()}}
            )
        
        # Update order status to pickup requested
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': Order.STATUS_PICKUP_REQUESTED,
                    'supermarketPickedFrom': ObjectId(supermarket_id),
                    'pickupRequestedAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        Order.add_log(order_id, db, Order.STATUS_PICKUP_REQUESTED, 'Pickup requested from supermarket')
        
        # Emit socket event to user
        socketio.emit(f'order_update_{order_id}', {
            'status': Order.STATUS_PICKUP_REQUESTED,
            'message': 'Pickup requested from supermarket'
        })
        
        return jsonify({'message': 'Pickup requested from supermarket'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>/ready-for-pickup', methods=['POST'])
@role_required('supermarket')
def mark_ready_for_pickup(order_id):
    """Supermarket marks order as ready for pickup"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket profile not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify order is at pickup requested status
        if order['status'] != Order.STATUS_PICKUP_REQUESTED:
            return jsonify({'error': 'Order is not in pickup requested status'}), 400
        
        # Verify order is for this supermarket
        if str(order.get('supermarketPickedFrom')) != str(supermarket['_id']):
            return jsonify({'error': 'Not authorized for this order'}), 403
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': Order.STATUS_READY_FOR_PICKUP,
                    'readyForPickupAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        Order.add_log(order_id, db, Order.STATUS_READY_FOR_PICKUP, 'Order ready for pickup')
        
        # Emit socket event to partner
        socketio.emit(f'order_update_{order_id}', {
            'status': Order.STATUS_READY_FOR_PICKUP,
            'message': 'Order ready for pickup'
        })
        
        return jsonify({'message': 'Order marked as ready for pickup'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>/collected', methods=['POST'])
@role_required('partner')
def mark_collected(order_id):
    """Partner marks order as collected from supermarket"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify partner is assigned to this order
        if str(order.get('assignedPartnerId')) != str(partner['_id']):
            return jsonify({'error': 'Not authorized'}), 403
        
        # Verify order is ready for pickup
        if order['status'] != Order.STATUS_READY_FOR_PICKUP:
            return jsonify({'error': 'Order is not ready for pickup'}), 400
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': Order.STATUS_PICKED_UP,
                    'pickedUpAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        Order.add_log(order_id, db, Order.STATUS_PICKED_UP, 'Order collected from supermarket')
        
        # Emit socket event to user
        socketio.emit(f'order_update_{order_id}', {
            'status': Order.STATUS_PICKED_UP,
            'message': 'Order collected from supermarket'
        })
        
        return jsonify({'message': 'Order marked as collected'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>/store-mark-out-for-delivery', methods=['POST'])
@role_required('supermarket')
def store_mark_out_for_delivery(order_id):
    """Supermarket marks order as out for delivery"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket profile not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify order is picked up
        if order['status'] != Order.STATUS_PICKED_UP:
            return jsonify({'error': 'Order must be picked up first'}), 400
        
        # Verify order is for this supermarket
        if str(order.get('supermarketPickedFrom')) != str(supermarket['_id']):
            return jsonify({'error': 'Not authorized for this order'}), 403
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': Order.STATUS_OUT_FOR_DELIVERY,
                    'outForDeliveryAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        Order.add_log(order_id, db, Order.STATUS_OUT_FOR_DELIVERY, 'Order out for delivery')
        
        # Emit socket event to user and partner
        socketio.emit(f'order_update_{order_id}', {
            'status': Order.STATUS_OUT_FOR_DELIVERY,
            'message': 'Order is out for delivery'
        })
        
        return jsonify({'message': 'Order marked as out for delivery'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>/out-for-delivery', methods=['POST'])
@role_required('partner')
def mark_out_for_delivery(order_id):
    """Partner marks order as out for delivery"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify partner is assigned to this order
        if str(order.get('assignedPartnerId')) != str(partner['_id']):
            return jsonify({'error': 'Not authorized'}), 403
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': Order.STATUS_OUT_FOR_DELIVERY,
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        Order.add_log(order_id, db, Order.STATUS_OUT_FOR_DELIVERY, 'Order is out for delivery')
        
        # Emit socket event to user
        socketio.emit(f'order_update_{order_id}', {
            'status': Order.STATUS_OUT_FOR_DELIVERY,
            'message': 'Your order is out for delivery'
        })
        
        return jsonify({'message': 'Order marked as out for delivery'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>/delivered', methods=['POST'])
@role_required('partner')
def mark_delivered(order_id):
    """Partner marks order as delivered"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get partner
        partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
        if not partner:
            return jsonify({'error': 'Partner profile not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify partner is assigned to this order
        if str(order.get('assignedPartnerId')) != str(partner['_id']):
            return jsonify({'error': 'Not authorized'}), 403
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': Order.STATUS_DELIVERED,
                    'actualDeliveryTime': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        Order.add_log(order_id, db, Order.STATUS_DELIVERED, 'Order delivered successfully')
        
        # Update partner stats
        db.delivery_partners.update_one(
            {'_id': partner['_id']},
            {
                '$inc': {'totalDeliveries': 1, 'totalEarnings': order.get('deliveryFee', 0)},
                '$set': {'status': 'available', 'currentOrderId': None}
            }
        )
        
        # Emit socket event to user
        socketio.emit(f'order_update_{order_id}', {
            'status': Order.STATUS_DELIVERED,
            'message': 'Your order has been delivered'
        })
        
        return jsonify({'message': 'Order marked as delivered'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>/cancel', methods=['POST'])
@token_required
def cancel_order(order_id):
    """Cancel an order"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        role = get_current_user_role()
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Authorization check
        if role == 'user' and str(order['userId']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        
        # Can only cancel if not yet delivered
        if order['status'] == Order.STATUS_DELIVERED:
            return jsonify({'error': 'Cannot cancel delivered order'}), 400
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': Order.STATUS_CANCELLED,
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        Order.add_log(order_id, db, Order.STATUS_CANCELLED, 'Order cancelled by user')
        
        # If partner was assigned, free them up
        if order.get('assignedPartnerId'):
            db.delivery_partners.update_one(
                {'_id': order['assignedPartnerId']},
                {'$set': {'status': 'available', 'currentOrderId': None}}
            )
        
        return jsonify({'message': 'Order cancelled successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
