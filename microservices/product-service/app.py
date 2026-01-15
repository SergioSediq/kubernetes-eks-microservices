"""
Product Service
Product catalog and inventory microservice using MongoDB
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# MongoDB configuration
MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGODB_PORT = int(os.getenv('MONGODB_PORT', '27017'))
MONGODB_DB = os.getenv('MONGODB_DB', 'products')
MONGODB_USER = os.getenv('MONGODB_USER', 'admin')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', 'password')

def get_mongodb_client():
    """Create and return MongoDB client"""
    try:
        connection_string = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB}?authSource=admin"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        raise

def get_db():
    """Get MongoDB database"""
    client = get_mongodb_client()
    return client[MONGODB_DB]

def init_database():
    """Initialize database collections"""
    try:
        db = get_db()
        # Create products collection if it doesn't exist
        if 'products' not in db.list_collection_names():
            db.create_collection('products')
            logger.info("Products collection created")
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        client = get_mongodb_client()
        client.admin.command('ping')
        client.close()
        return jsonify({
            'status': 'healthy',
            'service': 'product-service',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'product-service',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        db = get_db()
        products = list(db.products.find({}, {'_id': 0}))
        
        # Convert ObjectId to string if present
        for product in products:
            if '_id' in product:
                product['id'] = str(product['_id'])
                del product['_id']
        
        return jsonify({'products': products, 'count': len(products)}), 200
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        price = data.get('price')
        stock = data.get('stock', 0)
        
        if not name or price is None:
            return jsonify({'error': 'name and price are required'}), 400
        
        db = get_db()
        product = {
            'name': name,
            'description': description,
            'price': float(price),
            'stock': int(stock),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        result = db.products.insert_one(product)
        product['id'] = str(result.inserted_id)
        del product['_id']
        
        return jsonify(product), 201
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product"""
    try:
        from bson import ObjectId
        db = get_db()
        product = db.products.find_one({'_id': ObjectId(product_id)}, {'_id': 0})
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        product['id'] = product_id
        return jsonify(product), 200
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_database()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
