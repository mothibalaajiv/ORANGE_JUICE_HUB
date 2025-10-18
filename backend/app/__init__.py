from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from pymongo import MongoClient, GEOSPHERE
from app.config import config
import os
import certifi

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

# MongoDB client
mongo_client = None
db = None


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['FRONTEND_URL'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize MongoDB
    import ssl
    global mongo_client, db
    mongo_client = MongoClient(
        app.config.get('MONGODB_URI', 'mongodb+srv://mothicaptures:mothi@cluster0.858fyte.mongodb.net/tangytown'),
        serverSelectionTimeoutMS=5000
    )
    db = mongo_client[app.config.get('DB_NAME', 'tangytown')]
    
    # Create indexes
    create_indexes()
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.brands import brands_bp
    from app.routes.orders import orders_bp
    from app.routes.partners import partners_bp
    from app.routes.supermarkets import supermarkets_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp
    # from app.routes.analytics import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(brands_bp, url_prefix='/api/brands')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(partners_bp, url_prefix='/api/partners')
    app.register_blueprint(supermarkets_bp, url_prefix='/api/supermarkets')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    # app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'Tangy Town API'}), 200
    
    return app


def create_indexes():
    """Create MongoDB indexes for performance and geospatial queries"""
    try:
        # Users collection indexes
        db.users.create_index('email', unique=True)
        db.users.create_index([('location', GEOSPHERE)])
        
        # Delivery partners collection indexes
        db.delivery_partners.create_index([('currentLocation', GEOSPHERE)])
        db.delivery_partners.create_index('status')
        
        # Supermarket inventories collection indexes
        db.supermarket_inventories.create_index([('location', GEOSPHERE)])
        db.supermarket_inventories.create_index('supermarketId')
        db.supermarket_inventories.create_index('productId')
        
        # Orders collection indexes
        db.orders.create_index('userId')
        db.orders.create_index('status')
        db.orders.create_index('assignedPartnerId')
        db.orders.create_index('createdAt')
        
        # Products collection indexes
        db.products.create_index('brandId')
        db.products.create_index('sku', unique=True)
        db.products.create_index('active')
        
        # Assignment logs collection indexes
        db.assignment_logs.create_index('orderId')
        
        print("✓ MongoDB indexes created successfully")
    except Exception as e:
        print(f"Warning: Error creating indexes: {str(e)}")


def get_db():
    """Get database instance"""
    return db
