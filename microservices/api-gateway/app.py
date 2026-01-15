"""
API Gateway Service
Routes requests to appropriate microservices
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Service URLs from environment variables
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-service:8080')
ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-service:8080')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:8080')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API Gateway root endpoint"""
    return jsonify({
        'message': 'API Gateway - Microservices Platform',
        'version': '1.0.0',
        'services': {
            'users': f'{USER_SERVICE_URL}/api/users',
            'orders': f'{ORDER_SERVICE_URL}/api/orders',
            'products': f'{PRODUCT_SERVICE_URL}/api/products'
        },
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/users', methods=['GET', 'POST'])
@app.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def users_proxy(user_id=None):
    """Proxy requests to User Service"""
    try:
        method = request.method
        url = f'{USER_SERVICE_URL}/api/users'
        if user_id:
            url = f'{url}/{user_id}'
        
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=request.get_json(), timeout=5)
        elif method == 'PUT':
            response = requests.put(url, json=request.get_json(), timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=5)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proxying to user service: {str(e)}")
        return jsonify({'error': 'User service unavailable'}), 503

@app.route('/api/orders', methods=['GET', 'POST'])
@app.route('/api/orders/<order_id>', methods=['GET', 'PUT', 'DELETE'])
def orders_proxy(order_id=None):
    """Proxy requests to Order Service"""
    try:
        method = request.method
        url = f'{ORDER_SERVICE_URL}/api/orders'
        if order_id:
            url = f'{url}/{order_id}'
        
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=request.get_json(), timeout=5)
        elif method == 'PUT':
            response = requests.put(url, json=request.get_json(), timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=5)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proxying to order service: {str(e)}")
        return jsonify({'error': 'Order service unavailable'}), 503

@app.route('/api/products', methods=['GET', 'POST'])
@app.route('/api/products/<product_id>', methods=['GET', 'PUT', 'DELETE'])
def products_proxy(product_id=None):
    """Proxy requests to Product Service"""
    try:
        method = request.method
        url = f'{PRODUCT_SERVICE_URL}/api/products'
        if product_id:
            url = f'{url}/{product_id}'
        
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=request.get_json(), timeout=5)
        elif method == 'PUT':
            response = requests.put(url, json=request.get_json(), timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=5)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proxying to product service: {str(e)}")
        return jsonify({'error': 'Product service unavailable'}), 503

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
