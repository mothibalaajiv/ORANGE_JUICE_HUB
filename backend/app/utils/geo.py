import math
from bson import ObjectId


def calculate_distance(coord1, coord2):
    """
    Calculate distance between two coordinates using Haversine formula
    coord1, coord2: [longitude, latitude]
    Returns distance in meters
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    
    # Convert to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in meters
    r = 6371000
    
    return c * r


def find_nearest_partners(db, location, radius, limit=10):
    """
    Find nearest available delivery partners
    location: [longitude, latitude]
    radius: search radius in meters
    Returns list of partners sorted by distance
    """
    query = {
        'status': 'available',
        'currentLocation': {
            '$near': {
                '$geometry': {
                    'type': 'Point',
                    'coordinates': location
                },
                '$maxDistance': radius
            }
        }
    }
    
    partners = list(db.delivery_partners.find(query).limit(limit))
    return partners


def find_nearby_supermarkets_with_product(db, location, product_id, radius):
    """
    Find supermarkets near location that have the product in stock
    location: [longitude, latitude]
    product_id: ObjectId of product
    radius: search radius in meters
    Returns list of supermarkets with inventory info
    """
    # First, find inventories with the product and sufficient quantity
    inventories = list(db.supermarket_inventories.find({
        'productId': ObjectId(product_id),
        'quantity': {'$gt': 0}
    }))
    
    if not inventories:
        return []
    
    supermarket_ids = [inv['supermarketId'] for inv in inventories]
    
    # Find nearby supermarkets from the list
    query = {
        '_id': {'$in': supermarket_ids},
        'active': True,
        'approved': True,
        'location': {
            '$near': {
                '$geometry': {
                    'type': 'Point',
                    'coordinates': location
                },
                '$maxDistance': radius
            }
        }
    }
    
    supermarkets = list(db.supermarkets.find(query))
    
    # Enrich with inventory data
    inventory_map = {str(inv['supermarketId']): inv for inv in inventories}
    
    for supermarket in supermarkets:
        supermarket_id_str = str(supermarket['_id'])
        if supermarket_id_str in inventory_map:
            supermarket['inventory'] = inventory_map[supermarket_id_str]
            # Calculate distance
            if 'location' in supermarket and 'coordinates' in supermarket['location']:
                distance = calculate_distance(location, supermarket['location']['coordinates'])
                supermarket['distance'] = round(distance, 2)
    
    # Sort by distance
    supermarkets.sort(key=lambda x: x.get('distance', float('inf')))
    
    return supermarkets


def validate_coordinates(coordinates):
    """
    Validate longitude and latitude coordinates
    coordinates: [longitude, latitude]
    """
    if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2:
        return False
    
    lon, lat = coordinates
    
    # Longitude: -180 to 180
    # Latitude: -90 to 90
    if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
        return False
    
    return True


def create_point(longitude, latitude):
    """Create a GeoJSON Point object"""
    return {
        'type': 'Point',
        'coordinates': [float(longitude), float(latitude)]
    }
