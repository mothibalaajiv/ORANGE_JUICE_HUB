from flask import Blueprint, request, jsonify
from app import get_db
from app.models.user import User
from app.models.brand import Brand
from app.models.product import Product
from app.models.supermarket import Supermarket
from app.models.delivery_partner import DeliveryPartner
from app.models.order import Order
from app.utils.auth import role_required
from bson import ObjectId
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        db = get_db()
        
        # Count statistics
        total_users = db.users.count_documents({'role': 'user'})
        total_brands = db.brands.count_documents({})
        total_supermarkets = db.supermarkets.count_documents({})
        total_partners = db.delivery_partners.count_documents({})
        total_products = db.products.count_documents({})
        total_orders = db.orders.count_documents({})
        
        # Active partners
        active_partners = db.delivery_partners.count_documents({'status': 'available'})
        
        # Pending approvals
        pending_brands = db.brands.count_documents({'approved': False})
        pending_products = db.products.count_documents({'approved': False})
        pending_supermarkets = db.supermarkets.count_documents({'approved': False})
        
        # Recent orders
        recent_orders = list(db.orders.find().sort('createdAt', -1).limit(10))
        recent_orders_serialized = [Order.serialize(o) for o in recent_orders]
        
        # Revenue
        completed_orders = list(db.orders.find({'status': 'delivered'}))
        total_revenue = sum(o.get('totalAmount', 0) for o in completed_orders)
        
        return jsonify({
            'totalUsers': total_users,
            'totalBrands': total_brands,
            'totalSupermarkets': total_supermarkets,
            'totalPartners': total_partners,
            'activePartners': active_partners,
            'totalProducts': total_products,
            'totalOrders': total_orders,
            'totalRevenue': total_revenue,
            'pendingApprovals': {
                'brands': pending_brands,
                'products': pending_products,
                'supermarkets': pending_supermarkets
            },
            'recentOrders': recent_orders_serialized
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    """Get all users with filters"""
    try:
        db = get_db()
        
        query = {}
        
        # Role filter
        if request.args.get('role'):
            query['role'] = request.args.get('role')
        
        # Search filter
        if request.args.get('search'):
            query['$or'] = [
                {'name': {'$regex': request.args.get('search'), '$options': 'i'}},
                {'email': {'$regex': request.args.get('search'), '$options': 'i'}}
            ]
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit
        
        users = list(db.users.find(query).skip(skip).limit(limit))
        total = db.users.count_documents(query)
        
        users_serialized = [User.serialize(u) for u in users]
        
        return jsonify({
            'users': users_serialized,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/brands/pending', methods=['GET'])
@role_required('admin')
def get_pending_brands():
    """Get brands pending approval"""
    try:
        db = get_db()
        
        brands = list(db.brands.find({'approved': False}))
        brands_serialized = [Brand.serialize(b) for b in brands]
        
        return jsonify({'brands': brands_serialized}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/brands/<brand_id>/approve', methods=['POST'])
@role_required('admin')
def approve_brand(brand_id):
    """Approve a brand"""
    try:
        db = get_db()
        
        db.brands.update_one(
            {'_id': ObjectId(brand_id)},
            {'$set': {'approved': True, 'updatedAt': datetime.utcnow()}}
        )
        
        return jsonify({'message': 'Brand approved successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/brands/<brand_id>/reject', methods=['POST'])
@role_required('admin')
def reject_brand(brand_id):
    """Reject a brand"""
    try:
        db = get_db()
        
        db.brands.update_one(
            {'_id': ObjectId(brand_id)},
            {'$set': {'approved': False, 'active': False, 'updatedAt': datetime.utcnow()}}
        )
        
        return jsonify({'message': 'Brand rejected'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/products/pending', methods=['GET'])
@role_required('admin')
def get_pending_products():
    """Get products pending approval"""
    try:
        db = get_db()
        
        products = list(db.products.find({'approved': False}))
        
        # Enrich with brand info
        for product in products:
            brand = db.brands.find_one({'_id': product['brandId']})
            if brand:
                product['brand'] = Brand.serialize(brand)
        
        products_serialized = [Product.serialize(p) for p in products]
        
        return jsonify({'products': products_serialized}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/products/<product_id>/approve', methods=['POST'])
@role_required('admin')
def approve_product(product_id):
    """Approve a product"""
    try:
        db = get_db()
        
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'approved': True, 'updatedAt': datetime.utcnow()}}
        )
        
        return jsonify({'message': 'Product approved successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/supermarkets/pending', methods=['GET'])
@role_required('admin')
def get_pending_supermarkets():
    """Get supermarkets pending approval"""
    try:
        db = get_db()
        
        supermarkets = list(db.supermarkets.find({'approved': False}))
        supermarkets_serialized = [Supermarket.serialize(s) for s in supermarkets]
        
        return jsonify({'supermarkets': supermarkets_serialized}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/supermarkets/<supermarket_id>/approve', methods=['POST'])
@role_required('admin')
def approve_supermarket(supermarket_id):
    """Approve a supermarket"""
    try:
        db = get_db()
        
        db.supermarkets.update_one(
            {'_id': ObjectId(supermarket_id)},
            {'$set': {'approved': True, 'updatedAt': datetime.utcnow()}}
        )
        
        return jsonify({'message': 'Supermarket approved successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/orders', methods=['GET'])
@role_required('admin')
def get_all_orders():
    """Get all orders with filters"""
    try:
        db = get_db()
        
        query = {}
        
        # Status filter
        if request.args.get('status'):
            query['status'] = request.args.get('status')
        
        # Date range filter
        if request.args.get('startDate') or request.args.get('endDate'):
            date_query = {}
            if request.args.get('startDate'):
                date_query['$gte'] = datetime.fromisoformat(request.args.get('startDate'))
            if request.args.get('endDate'):
                date_query['$lte'] = datetime.fromisoformat(request.args.get('endDate'))
            query['createdAt'] = date_query
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit
        
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


@admin_bp.route('/orders/<order_id>/reassign', methods=['POST'])
@role_required('admin')
def reassign_order(order_id):
    """Manually reassign order to a different partner"""
    try:
        db = get_db()
        data = request.get_json()
        
        new_partner_id = data.get('partnerId')
        if not new_partner_id:
            return jsonify({'error': 'partnerId is required'}), 400
        
        # Verify partner exists
        partner = db.delivery_partners.find_one({'_id': ObjectId(new_partner_id)})
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        # Get order
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Free up old partner if any
        if order.get('assignedPartnerId'):
            db.delivery_partners.update_one(
                {'_id': order['assignedPartnerId']},
                {'$set': {'status': 'available', 'currentOrderId': None}}
            )
        
        # Assign to new partner
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'assignedPartnerId': ObjectId(new_partner_id),
                    'partnerAssignedAt': datetime.utcnow(),
                    'partnerAccepted': True,
                    'partnerAcceptedAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        # Update partner
        db.delivery_partners.update_one(
            {'_id': ObjectId(new_partner_id)},
            {'$set': {'status': 'busy', 'currentOrderId': ObjectId(order_id)}}
        )
        
        Order.add_log(order_id, db, 'manual_reassignment', f'Manually reassigned by admin')
        
        return jsonify({'message': 'Order reassigned successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/assignment-logs', methods=['GET'])
@role_required('admin')
def get_assignment_logs():
    """Get assignment logs for monitoring"""
    try:
        db = get_db()
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit
        
        logs = list(db.assignment_logs.find().sort('createdAt', -1).skip(skip).limit(limit))
        total = db.assignment_logs.count_documents({})
        
        # Serialize logs
        for log in logs:
            log['_id'] = str(log['_id'])
            log['orderId'] = str(log['orderId'])
            if log.get('finalAssignedPartnerId'):
                log['finalAssignedPartnerId'] = str(log['finalAssignedPartnerId'])
            
            for attempt in log.get('attempts', []):
                attempt['partnerId'] = str(attempt['partnerId'])
                if attempt.get('assignedAt'):
                    attempt['assignedAt'] = attempt['assignedAt'].isoformat()
                if attempt.get('expiredAt'):
                    attempt['expiredAt'] = attempt['expiredAt'].isoformat()
            
            if log.get('createdAt'):
                log['createdAt'] = log['createdAt'].isoformat()
        
        return jsonify({
            'logs': logs,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
