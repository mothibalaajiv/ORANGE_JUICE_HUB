from flask import Blueprint, request, jsonify
from app import get_db
from app.models.brand import Brand
from app.utils.auth import token_required, role_required, get_current_user_id
from bson import ObjectId

brands_bp = Blueprint('brands', __name__)


@brands_bp.route('', methods=['GET'])
def get_brands():
    """Get all approved brands"""
    try:
        db = get_db()
        
        # Build query
        query = {'approved': True, 'active': True}
        
        # Search filter
        if request.args.get('search'):
            query['name'] = {'$regex': request.args.get('search'), '$options': 'i'}
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        
        brands = list(db.brands.find(query).skip(skip).limit(limit))
        total = db.brands.count_documents(query)
        
        # Enrich with product count
        for brand in brands:
            product_count = db.products.count_documents({'brandId': brand['_id'], 'active': True})
            brand['productCount'] = product_count
        
        brands_serialized = [Brand.serialize(b) for b in brands]
        
        return jsonify({
            'brands': brands_serialized,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@brands_bp.route('/<brand_id>', methods=['GET'])
def get_brand(brand_id):
    """Get single brand by ID"""
    try:
        db = get_db()
        
        brand = db.brands.find_one({'_id': ObjectId(brand_id)})
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Get products
        products = list(db.products.find({'brandId': ObjectId(brand_id), 'active': True, 'approved': True}))
        from app.models.product import Product
        brand['products'] = [Product.serialize(p) for p in products]
        
        brand_serialized = Brand.serialize(brand)
        
        return jsonify(brand_serialized), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@brands_bp.route('', methods=['POST'])
@role_required('brand', 'admin')
def create_brand():
    """Create a new brand"""
    try:
        db = get_db()
        data = request.get_json()
        user_id = get_current_user_id()
        
        # Check if user already has a brand
        existing = db.brands.find_one({'userId': ObjectId(user_id)})
        if existing:
            return jsonify({'error': 'Brand already exists for this user'}), 400
        
        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Set userId
        data['userId'] = user_id
        
        # Create brand
        brand_data = Brand.create(data)
        result = db.brands.insert_one(brand_data)
        
        # Get created brand
        brand = db.brands.find_one({'_id': result.inserted_id})
        brand_serialized = Brand.serialize(brand)
        
        return jsonify({
            'message': 'Brand created successfully (pending admin approval)',
            'brand': brand_serialized
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@brands_bp.route('/<brand_id>', methods=['PUT'])
@role_required('brand', 'admin')
def update_brand(brand_id):
    """Update brand details"""
    try:
        db = get_db()
        data = request.get_json()
        user_id = get_current_user_id()
        
        # Get brand
        brand = db.brands.find_one({'_id': ObjectId(brand_id)})
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Check ownership (unless admin)
        from app.utils.auth import get_current_user_role
        if get_current_user_role() != 'admin' and str(brand['userId']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        
        # Update fields
        update_fields = {}
        allowed_fields = ['name', 'description', 'logoUrl', 'website', 'contactEmail', 'contactPhone']
        for field in allowed_fields:
            if field in data:
                update_fields[field] = data[field]
        
        if update_fields:
            from datetime import datetime
            update_fields['updatedAt'] = datetime.utcnow()
            db.brands.update_one(
                {'_id': ObjectId(brand_id)},
                {'$set': update_fields}
            )
        
        # Get updated brand
        brand = db.brands.find_one({'_id': ObjectId(brand_id)})
        brand_serialized = Brand.serialize(brand)
        
        return jsonify({
            'message': 'Brand updated successfully',
            'brand': brand_serialized
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@brands_bp.route('/my-brand', methods=['GET'])
@role_required('brand')
def get_my_brand():
    """Get current user's brand"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        brand = db.brands.find_one({'userId': ObjectId(user_id)})
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Get products count
        product_count = db.products.count_documents({'brandId': brand['_id']})
        brand['productCount'] = product_count
        
        brand_serialized = Brand.serialize(brand)
        
        return jsonify(brand_serialized), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@brands_bp.route('/my-products', methods=['GET'])
@role_required('brand')
def get_my_products():
    """Get products for current user's brand"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get brand
        brand = db.brands.find_one({'userId': ObjectId(user_id)})
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Get products
        products = list(db.products.find({'brandId': brand['_id']}))
        
        from app.models.product import Product
        products_serialized = [Product.serialize(p) for p in products]
        
        return jsonify({'products': products_serialized}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
