from flask import Blueprint, request, jsonify
from app import get_db
from app.models.supermarket import Supermarket, SupermarketInventory
from app.utils.auth import token_required, role_required, get_current_user_id
from bson import ObjectId
from datetime import datetime

supermarkets_bp = Blueprint('supermarkets', __name__)


@supermarkets_bp.route('', methods=['GET'])
def get_supermarkets():
    """Get all approved supermarkets"""
    try:
        db = get_db()
        
        query = {'approved': True, 'active': True}
        
        # Location-based search
        if request.args.get('lng') and request.args.get('lat'):
            lng = float(request.args.get('lng'))
            lat = float(request.args.get('lat'))
            radius = int(request.args.get('radius', 10000))  # 10km default
            
            query['location'] = {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    '$maxDistance': radius
                }
            }
        
        supermarkets = list(db.supermarkets.find(query).limit(20))
        
        supermarkets_serialized = [Supermarket.serialize(s) for s in supermarkets]
        
        return jsonify({'supermarkets': supermarkets_serialized}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/my-supermarket', methods=['GET'])
@role_required('supermarket')
def get_my_supermarket():
    """Get current user's supermarket"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        supermarket_serialized = Supermarket.serialize(supermarket)
        
        return jsonify(supermarket_serialized), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/my-supermarket', methods=['PUT'])
@role_required('supermarket')
def update_my_supermarket():
    """Update supermarket details"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        data = request.get_json()
        
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        # Update fields
        update_fields = {}
        allowed_fields = ['name', 'address', 'location', 'phone', 'email', 'openingHours']
        for field in allowed_fields:
            if field in data:
                update_fields[field] = data[field]
        
        if update_fields:
            update_fields['updatedAt'] = datetime.utcnow()
            db.supermarkets.update_one(
                {'_id': supermarket['_id']},
                {'$set': update_fields}
            )
        
        supermarket = db.supermarkets.find_one({'_id': supermarket['_id']})
        supermarket_serialized = Supermarket.serialize(supermarket)
        
        return jsonify({
            'message': 'Supermarket updated successfully',
            'supermarket': supermarket_serialized
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/inventory', methods=['GET'])
@role_required('supermarket')
def get_my_inventory():
    """Get inventory for current user's supermarket"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        # Get inventory
        inventories = list(db.supermarket_inventories.find({'supermarketId': supermarket['_id']}))
        
        # Enrich with product details
        for inv in inventories:
            product = db.products.find_one({'_id': inv['productId']})
            if product:
                from app.models.product import Product
                inv['product'] = Product.serialize(product)
                
                # Get brand info
                brand = db.brands.find_one({'_id': product['brandId']})
                if brand:
                    inv['product']['brandName'] = brand['name']
        
        inventories_serialized = [SupermarketInventory.serialize(i) for i in inventories]
        
        return jsonify({'inventory': inventories_serialized}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/inventory', methods=['POST'])
@role_required('supermarket')
def add_inventory():
    """Add or update inventory item"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        # Validate required fields
        if not data.get('productId') or not data.get('quantity'):
            return jsonify({'error': 'productId and quantity are required'}), 400
        
        # Check if product exists
        product = db.products.find_one({'_id': ObjectId(data['productId'])})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if inventory item exists
        existing = db.supermarket_inventories.find_one({
            'supermarketId': supermarket['_id'],
            'productId': ObjectId(data['productId'])
        })
        
        if existing:
            # Update existing
            db.supermarket_inventories.update_one(
                {'_id': existing['_id']},
                {
                    '$set': {
                        'quantity': int(data['quantity']),
                        'priceOverride': data.get('priceOverride'),
                        'lastUpdated': datetime.utcnow()
                    }
                }
            )
            inventory = db.supermarket_inventories.find_one({'_id': existing['_id']})
            message = 'Inventory updated successfully'
        else:
            # Create new
            data['supermarketId'] = supermarket['_id']
            inventory_data = SupermarketInventory.create(data)
            result = db.supermarket_inventories.insert_one(inventory_data)
            inventory = db.supermarket_inventories.find_one({'_id': result.inserted_id})
            message = 'Inventory added successfully'
        
        inventory_serialized = SupermarketInventory.serialize(inventory)
        
        return jsonify({
            'message': message,
            'inventory': inventory_serialized
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/inventory/<inventory_id>', methods=['DELETE'])
@role_required('supermarket')
def delete_inventory(inventory_id):
    """Delete inventory item"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        # Get inventory
        inventory = db.supermarket_inventories.find_one({'_id': ObjectId(inventory_id)})
        if not inventory:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        # Check ownership
        if inventory['supermarketId'] != supermarket['_id']:
            return jsonify({'error': 'Not authorized'}), 403
        
        # Delete
        db.supermarket_inventories.delete_one({'_id': ObjectId(inventory_id)})
        
        return jsonify({'message': 'Inventory item deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/pickup-requests', methods=['GET'])
@role_required('supermarket')
def get_pickup_requests():
    """Get orders that are picking up from this supermarket (view only)"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        # Get orders being picked up or picked up from this supermarket
        orders = list(db.orders.find({
            'supermarketPickedFrom': supermarket['_id']
        }).sort('createdAt', -1).limit(50))
        
        from app.models.order import Order
        orders_serialized = [Order.serialize(o) for o in orders]
        
        return jsonify({'pickupRequests': orders_serialized}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/pickup-requests/<order_id>/ready', methods=['POST'])
@role_required('supermarket')
def mark_order_ready_for_pickup(order_id):
    """Mark order as ready for pickup"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify order is for this supermarket and in pickup_requested status
        if str(order.get('supermarketPickedFrom')) != str(supermarket['_id']):
            return jsonify({'error': 'Not authorized for this order'}), 403
        
        if order.get('status') != 'pickup_requested':
            return jsonify({'error': 'Order is not in pickup_requested status'}), 400
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': 'ready_for_pickup',
                    'readyForPickupAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        from app.models.order import Order
        Order.add_log(order_id, db, 'ready_for_pickup', 'Order ready for pickup')
        
        # Emit socket event to partner
        from app import socketio
        socketio.emit(f'order_update_{order_id}', {
            'status': 'ready_for_pickup',
            'message': 'Order ready for pickup'
        })
        
        return jsonify({'message': 'Order marked as ready for pickup'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/pickup-requests/<order_id>/reject', methods=['POST'])
@role_required('supermarket')
def reject_pickup_request(order_id):
    """Reject pickup request"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify order is for this supermarket and in pickup_requested status
        if str(order.get('supermarketPickedFrom')) != str(supermarket['_id']):
            return jsonify({'error': 'Not authorized for this order'}), 403
        
        if order.get('status') != 'pickup_requested':
            return jsonify({'error': 'Order is not in pickup_requested status'}), 400
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': 'pickup_rejected',
                    'rejectionReason': data.get('reason', 'No reason provided'),
                    'rejectedAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        from app.models.order import Order
        Order.add_log(order_id, db, 'pickup_rejected', f'Pickup request rejected: {data.get("reason", "No reason provided")}')
        
        # Emit socket event to partner
        from app import socketio
        socketio.emit(f'order_update_{order_id}', {
            'status': 'pickup_rejected',
            'message': 'Pickup request rejected by supermarket'
        })
        
        return jsonify({'message': 'Pickup request rejected'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supermarkets_bp.route('/pickup-requests/<order_id>/mark-out-for-delivery', methods=['POST'])
@role_required('supermarket')
def mark_order_out_for_delivery(order_id):
    """Mark order as out for delivery after pickup"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get supermarket
        supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
        if not supermarket:
            return jsonify({'error': 'Supermarket not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify order is for this supermarket and picked up
        if str(order.get('supermarketPickedFrom')) != str(supermarket['_id']):
            return jsonify({'error': 'Not authorized for this order'}), 403
        
        if order.get('status') != 'picked_up':
            return jsonify({'error': 'Order must be picked up first'}), 400
        
        # Update order status
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': 'out_for_delivery',
                    'outForDeliveryAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Add log
        from app.models.order import Order
        Order.add_log(order_id, db, 'out_for_delivery', 'Order marked as out for delivery')
        
        # Emit socket event to user and partner
        from app import socketio
        socketio.emit(f'order_update_{order_id}', {
            'status': 'out_for_delivery',
            'message': 'Order is out for delivery'
        })
        
        return jsonify({'message': 'Order marked as out for delivery'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
