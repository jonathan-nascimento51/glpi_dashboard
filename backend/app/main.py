from flask import Flask
from flask_cors import CORS
from ..api.routes import api_bp
from ..core.config import active_config
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Factory function para criar a aplica��o Flask"""
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app, origins=["*"])
    
    # Registrar blueprints
    app.register_blueprint(api_bp)
    
    @app.route("/")
    def root():
        return {"message": "GLPI Dashboard API", "status": "running"}
    
    @app.route("/health")
    def health():
        return {"status": "healthy"}
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
