"""
User Service
User management and authentication microservice
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
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
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
            'service': 'user-service',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'user-service',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, first_name, last_name, created_at, updated_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        result = []
        for user in users:
            result.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'first_name': user[3],
                'last_name': user[4],
                'created_at': user[5].isoformat() if user[5] else None,
                'updated_at': user[6].isoformat() if user[6] else None
            })
        
        return jsonify({'users': result, 'count': len(result)}), 200
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            RETURNING id, username, email, first_name, last_name, created_at, updated_at
        """, (username, email, first_name, last_name))
        
        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'first_name': user[3],
            'last_name': user[4],
            'created_at': user[5].isoformat() if user[5] else None,
            'updated_at': user[6].isoformat() if user[6] else None
        }), 201
    except psycopg2.IntegrityError as e:
        return jsonify({'error': 'User already exists'}), 409
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, first_name, last_name, created_at, updated_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'first_name': user[3],
            'last_name': user[4],
            'created_at': user[5].isoformat() if user[5] else None,
            'updated_at': user[6].isoformat() if user[6] else None
        }), 200
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_database()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
