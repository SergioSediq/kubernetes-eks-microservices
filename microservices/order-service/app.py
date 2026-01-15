"""
Order Service
Order processing and management microservice
"""

import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'appdb'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Create and return database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def init_database():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                total_amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'service': 'order-service',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'order-service',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, product_id, quantity, total_amount, status, created_at, updated_at FROM orders ORDER BY created_at DESC")
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        
        result = []
        for order in orders:
            result.append({
                'id': order[0],
                'user_id': order[1],
                'product_id': order[2],
                'quantity': order[3],
                'total_amount': float(order[4]),
                'status': order[5],
                'created_at': order[6].isoformat() if order[6] else None,
                'updated_at': order[7].isoformat() if order[7] else None
            })
        
        return jsonify({'orders': result, 'count': len(result)}), 200
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        total_amount = data.get('total_amount')
        status = data.get('status', 'pending')
        
        if not user_id or not product_id or not total_amount:
            return jsonify({'error': 'user_id, product_id, and total_amount are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (user_id, product_id, quantity, total_amount, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, user_id, product_id, quantity, total_amount, status, created_at, updated_at
        """, (user_id, product_id, quantity, total_amount, status))
        
        order = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': order[0],
            'user_id': order[1],
            'product_id': order[2],
            'quantity': order[3],
            'total_amount': float(order[4]),
            'status': order[5],
            'created_at': order[6].isoformat() if order[6] else None,
            'updated_at': order[7].isoformat() if order[7] else None
        }), 201
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, product_id, quantity, total_amount, status, created_at, updated_at FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'id': order[0],
            'user_id': order[1],
            'product_id': order[2],
            'quantity': order[3],
            'total_amount': float(order[4]),
            'status': order[5],
            'created_at': order[6].isoformat() if order[6] else None,
            'updated_at': order[7].isoformat() if order[7] else None
        }), 200
    except Exception as e:
        logger.error(f"Error getting order: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_database()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
