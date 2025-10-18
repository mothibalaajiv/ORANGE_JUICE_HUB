from flask import Blueprint, request, jsonify
from app import get_db
from app.models.product import Product
from app.utils.auth import token_required, role_required, get_current_user_id
from bson import ObjectId

products_bp = Blueprint('products', __name__)


@products_bp.route('', methods=['GET'])
def get_products():
    """Get all products with filters"""
    try:
        db = get_db()
        if db is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Build query from query params
        query = {'active': True, 'approved': True}
        
        # Brand filter
        if request.args.get('brandId'):
            try:
                query['brandId'] = ObjectId(request.args.get('brandId'))
            except Exception as e:
                return jsonify({'error': f'Invalid brandId: {str(e)}'}), 400
        
        # Category filter
        if request.args.get('category'):
            query['category'] = request.args.get('category')
        
        # Search by name
        if request.args.get('search'):
            query['name'] = {'$regex': request.args.get('search'), '$options': 'i'}
        
        # Price range
        if request.args.get('minPrice') or request.args.get('maxPrice'):
            price_query = {}
            if request.args.get('minPrice'):
                try:
                    price_query['$gte'] = float(request.args.get('minPrice'))
                except ValueError:
                    return jsonify({'error': 'Invalid minPrice'}), 400
            if request.args.get('maxPrice'):
                try:
                    price_query['$lte'] = float(request.args.get('maxPrice'))
                except ValueError:
                    return jsonify({'error': 'Invalid maxPrice'}), 400
            query['price'] = price_query
        
        # Pagination
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
        except ValueError:
            return jsonify({'error': 'Invalid page or limit parameter'}), 400
        
        skip = (page - 1) * limit
        
        # Get products
        try:
            products = list(db.products.find(query).skip(skip).limit(limit))
            total = db.products.count_documents(query)
        except Exception as e:
            return jsonify({'error': f'Database query failed: {str(e)}'}), 500
        
        # Enrich with brand info
        for product in products:
            try:
                brand = db.brands.find_one({'_id': product['brandId']})
                if brand:
                    product['brand'] = {
                        '_id': str(brand['_id']),
                        'name': brand['name'],
                        'logoUrl': brand.get('logoUrl', '')
                    }
            except Exception as e:
                print(f"Warning: Error enriching product {product.get('_id')} with brand info: {str(e)}")
        
        # Serialize products
        try:
            products_serialized = [Product.serialize(p) for p in products]
        except Exception as e:
            return jsonify({'error': f'Serialization failed: {str(e)}'}), 500
        
        return jsonify({
            'products': products_serialized,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    
    except Exception as e:
        print(f"Products API error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    try:
        db = get_db()
        
        product = db.products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get brand info
        brand = db.brands.find_one({'_id': product['brandId']})
        if brand:
            from app.models.brand import Brand
            product['brand'] = Brand.serialize(brand)
        
        # Get availability from supermarkets
        inventories = list(db.supermarket_inventories.find({
            'productId': ObjectId(product_id),
            'quantity': {'$gt': 0}
        }))
        product['availableAt'] = len(inventories)
        product['totalStock'] = sum(inv['quantity'] for inv in inventories)
        
        product_serialized = Product.serialize(product)
        
        return jsonify(product_serialized), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('', methods=['POST'])
@role_required('brand', 'admin')
def create_product():
    """Create a new product (Brand or Admin only)"""
    try:
        db = get_db()
        data = request.get_json()
        user_id = get_current_user_id()
        
        # Get brand for this user
        brand = db.brands.find_one({'userId': ObjectId(user_id)})
        if not brand:
            return jsonify({'error': 'Brand profile not found'}), 404
        
        # Validate required fields
        required_fields = ['name', 'sku', 'volume', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if SKU already exists
        existing = db.products.find_one({'sku': data['sku']})
        if existing:
            return jsonify({'error': 'SKU already exists'}), 400
        
        # Set brandId
        data['brandId'] = brand['_id']
        
        # Create product
        product_data = Product.create(data)
        result = db.products.insert_one(product_data)
        
        # Get created product
        product = db.products.find_one({'_id': result.inserted_id})
        product_serialized = Product.serialize(product)
        
        return jsonify({
            'message': 'Product created successfully (pending admin approval)',
            'product': product_serialized
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<product_id>', methods=['PUT'])
@role_required('brand', 'admin')
def update_product(product_id):
    """Update a product"""
    try:
        db = get_db()
        data = request.get_json()
        user_id = get_current_user_id()
        
        # Get product
        product = db.products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check ownership (unless admin)
        from app.utils.auth import get_current_user_role
        if get_current_user_role() != 'admin':
            brand = db.brands.find_one({'userId': ObjectId(user_id)})
            if not brand or product['brandId'] != brand['_id']:
                return jsonify({'error': 'Not authorized'}), 403
        
        # Update fields
        update_fields = {}
        allowed_fields = ['name', 'volume', 'price', 'imageUrl', 'description', 'category', 'nutritionalInfo', 'active', 'tags']
        for field in allowed_fields:
            if field in data:
                update_fields[field] = data[field]
        
        if update_fields:
            from datetime import datetime
            update_fields['updatedAt'] = datetime.utcnow()
            
            db.products.update_one(
                {'_id': ObjectId(product_id)},
                {'$set': update_fields}
            )
        
        # Get updated product
        product = db.products.find_one({'_id': ObjectId(product_id)})
        product_serialized = Product.serialize(product)
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product_serialized
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<product_id>', methods=['DELETE'])
@role_required('brand', 'admin')
def delete_product(product_id):
    """Delete a product (soft delete - set inactive)"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Get product
        product = db.products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check ownership (unless admin)
        from app.utils.auth import get_current_user_role
        if get_current_user_role() != 'admin':
            brand = db.brands.find_one({'userId': ObjectId(user_id)})
            if not brand or product['brandId'] != brand['_id']:
                return jsonify({'error': 'Not authorized'}), 403
        
        # Soft delete
        from datetime import datetime
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'active': False, 'updatedAt': datetime.utcnow()}}
        )
        
        return jsonify({'message': 'Product deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
