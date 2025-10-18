"""
Tangy Town - Flask Backend Application
Main entry point
"""
from app import create_app, socketio
import os

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    print("=" * 60)
    print("🍊 Tangy Town Backend Server")
    print("=" * 60)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Port: {port}")
    print(f"API URL: http://localhost:{port}/api")
    print(f"Health Check: http://localhost:{port}/api/health")
    print("=" * 60)
    
    # Run with SocketIO for real-time features
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG'],
        allow_unsafe_werkzeug=True
    )
