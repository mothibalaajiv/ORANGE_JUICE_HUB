"""
Tangy Town - Flask Backend Application
Main entry point
"""
from flask import send_from_directory, jsonify
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


    # Serve React app for all non-API routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        """Serve React app for all non-API routes"""
        from flask import send_from_directory
        import os
        
        # If path is an API route, let it be handled by blueprints
        if path.startswith('api/'):
            return jsonify({'error': 'API endpoint not found'}), 404
        
        # If path exists as a static file, serve it
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        
        # Otherwise serve index.html for React routing
        return send_from_directory(app.static_folder, 'index.html')
    
    # Run with SocketIO for real-time features
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG'],
        allow_unsafe_werkzeug=True
    )
