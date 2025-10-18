from flask import Blueprint, request, jsonify
from app import get_db
from app.models.user import User
from app.models.delivery_partner import DeliveryPartner
from app.models.brand import Brand
from app.models.supermarket import Supermarket
from app.utils.auth import generate_access_token, generate_refresh_token, decode_token, token_required, get_current_user_id
from bson import ObjectId

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate role
        if not User.validate_role(data['role']):
            return jsonify({'error': 'Invalid role'}), 400
        
        db = get_db()
        
        # Check if email already exists
        existing_user = db.users.find_one({'email': data['email'].lower()})
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user_data = User.create(data)
        result = db.users.insert_one(user_data)
        user_id = result.inserted_id
        
        # Create role-specific profile
        if data['role'] == 'partner':
            partner_data = DeliveryPartner.create({
                'userId': user_id,
                'vehicleType': data.get('vehicleType', 'bike')
            })
            db.delivery_partners.insert_one(partner_data)
        
        elif data['role'] == 'brand':
            brand_data = Brand.create({
                'userId': user_id,
                'name': data.get('brandName', data['name']),
                'description': data.get('brandDescription', ''),
                'contactEmail': data['email'],
                'contactPhone': data.get('phone', '')
            })
            db.brands.insert_one(brand_data)
        
        elif data['role'] == 'supermarket':
            supermarket_data = Supermarket.create({
                'userId': user_id,
                'name': data.get('supermarketName', data['name']),
                'address': data.get('address', ''),
                'phone': data.get('phone', ''),
                'email': data['email']
            })
            db.supermarkets.insert_one(supermarket_data)
        
        # Generate tokens
        access_token = generate_access_token(user_id, data['role'])
        refresh_token = generate_refresh_token(user_id, data['role'])
        
        # Get user data
        user = db.users.find_one({'_id': user_id})
        user_serialized = User.serialize(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_serialized,
            'accessToken': access_token,
            'refreshToken': refresh_token
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        db = get_db()
        
        # Find user
        user = db.users.find_one({'email': data['email'].lower()})
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not User.verify_password(data['password'], user['passwordHash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user.get('active', True):
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Generate tokens
        access_token = generate_access_token(user['_id'], user['role'])
        refresh_token = generate_refresh_token(user['_id'], user['role'])
        
        user_serialized = User.serialize(user)
        
        return jsonify({
            'message': 'Login successful',
            'user': user_serialized,
            'accessToken': access_token,
            'refreshToken': refresh_token
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refreshToken')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        
        # Decode refresh token
        payload = decode_token(refresh_token, 'refresh')
        if not payload:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        # Generate new access token
        access_token = generate_access_token(payload['user_id'], payload['role'])
        
        return jsonify({
            'accessToken': access_token
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_profile():
    """Get current user profile"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_serialized = User.serialize(user)
        
        # Get role-specific data
        role = user.get('role')
        if role == 'partner':
            partner = db.delivery_partners.find_one({'userId': ObjectId(user_id)})
            if partner:
                user_serialized['partnerProfile'] = DeliveryPartner.serialize(partner)
        
        elif role == 'brand':
            brand = db.brands.find_one({'userId': ObjectId(user_id)})
            if brand:
                user_serialized['brandProfile'] = Brand.serialize(brand)
        
        elif role == 'supermarket':
            supermarket = db.supermarkets.find_one({'userId': ObjectId(user_id)})
            if supermarket:
                user_serialized['supermarketProfile'] = Supermarket.serialize(supermarket)
        
        return jsonify(user_serialized), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_profile():
    """Update current user profile"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Fields that can be updated
        update_fields = {}
        if 'name' in data:
            update_fields['name'] = data['name']
        if 'phone' in data:
            update_fields['phone'] = data['phone']
        if 'address' in data:
            update_fields['address'] = data['address']
        if 'location' in data:
            update_fields['location'] = data['location']
        
        if update_fields:
            from datetime import datetime
            update_fields['updatedAt'] = datetime.utcnow()
            
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_fields}
            )
        
        # Get updated user
        user = db.users.find_one({'_id': ObjectId(user_id)})
        user_serialized = User.serialize(user)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user_serialized
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
