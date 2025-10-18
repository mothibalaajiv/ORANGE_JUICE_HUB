import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
from bson import ObjectId


def generate_access_token(user_id, role):
    """Generate JWT access token"""
    payload = {
        'user_id': str(user_id),
        'role': role,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def generate_refresh_token(user_id, role):
    """Generate JWT refresh token"""
    payload = {
        'user_id': str(user_id),
        'role': role,
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['JWT_REFRESH_SECRET_KEY'], algorithm='HS256')


def decode_token(token, token_type='access'):
    """Decode and validate JWT token"""
    try:
        secret_key = current_app.config['JWT_SECRET_KEY'] if token_type == 'access' else current_app.config['JWT_REFRESH_SECRET_KEY']
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        if payload.get('type') != token_type:
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Decode token
        payload = decode_token(token, 'access')
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        request.current_user = {
            'user_id': payload['user_id'],
            'role': payload['role']
        }
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(*allowed_roles):
    """Decorator to require specific user role(s)"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user_role = request.current_user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def get_current_user_id():
    """Get current user ID from request context"""
    return request.current_user.get('user_id') if hasattr(request, 'current_user') else None


def get_current_user_role():
    """Get current user role from request context"""
    return request.current_user.get('role') if hasattr(request, 'current_user') else None
