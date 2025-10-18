from datetime import datetime
from bson import ObjectId
import bcrypt


class User:
    """User model for all user types"""
    
    ROLES = ['user', 'brand', 'supermarket', 'partner', 'admin']
    
    @staticmethod
    def create(data):
        """Create a new user"""
        user_data = {
            'name': data.get('name'),
            'email': data.get('email').lower(),
            'passwordHash': User.hash_password(data.get('password')),
            'role': data.get('role', 'user'),
            'phone': data.get('phone'),
            'address': data.get('address'),
            'location': data.get('location', {
                'type': 'Point',
                'coordinates': [0, 0]  # [longitude, latitude]
            }),
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'active': True,
            'verified': False,
            'meta': {}
        }
        return user_data
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def serialize(user):
        """Serialize user document for JSON response (exclude sensitive data)"""
        if not user:
            return None
        
        user['_id'] = str(user['_id'])
        user.pop('passwordHash', None)
        
        # Convert datetime to string
        if 'createdAt' in user:
            user['createdAt'] = user['createdAt'].isoformat()
        if 'updatedAt' in user:
            user['updatedAt'] = user['updatedAt'].isoformat()
        
        return user
    
    @staticmethod
    def validate_role(role):
        """Validate user role"""
        return role in User.ROLES
