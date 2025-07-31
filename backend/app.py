from flask import Flask
from flask_cors import CORS
from config.config import Config 
from api import chat_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY
    
    # Simple CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": "http://localhost:3000",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    app.register_blueprint(chat_routes.chat_bp, url_prefix='/api')
    
    @app.route('/')
    def health_check():
        return {'status': 'healthy', 'message': 'ADF Pipeline Generator API is running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)