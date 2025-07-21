from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from models.conversation_ai import ConversationAI
from database.connection import DatabaseConnection
import traceback

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Configurar la IA conversacional
ai_instance = None
db_connection = None

def initialize_ai():
    """Inicializar la IA y conexión a la base de datos"""
    global ai_instance, db_connection
    try:
        # Inicializar conexión a la base de datos
        db_connection = DatabaseConnection()
        
        # Inicializar la IA
        ai_instance = ConversationAI(db_connection)
        ai_instance.initialize()
        
        logger.info("IA inicializada correctamente")
        return True
    except Exception as e:
        logger.error(f"Error inicializando IA: {e}")
        return False

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "IA Conversacional activa",
        "version": "1.0.0"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal para conversación con la IA"""
    try:
        # Obtener datos del request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Mensaje requerido"
            }), 400
        
        user_message = data['message']
        user_role = data.get('role', 'alumno')  # alumno, profesor, directivo
        user_id = data.get('user_id', None)
        
        logger.info(f"Mensaje recibido: {user_message} (Role: {user_role})")
        
        # Procesar mensaje con la IA
        response = ai_instance.process_message(
            message=user_message,
            user_role=user_role,
            user_id=user_id
        )
        
        return jsonify({
            "success": True,
            "response": response['text'],
            "data": response.get('data', None),
            "query_used": response.get('query', None),
            "recommendations": response.get('recommendations', []),
            "timestamp": response.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "details": str(e)
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Obtener sugerencias de preguntas"""
    try:
        role = request.args.get('role', 'alumno')
        suggestions = ai_instance.get_suggestions(role)
        
        return jsonify({
            "success": True,
            "suggestions": suggestions
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {e}")
        return jsonify({
            "success": False,
            "error": "Error obteniendo sugerencias"
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Obtener analytics básicos del sistema"""
    try:
        analytics = ai_instance.get_system_analytics()
        
        return jsonify({
            "success": True,
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {e}")
        return jsonify({
            "success": False,
            "error": "Error obteniendo analytics"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint no encontrado"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Error interno del servidor"
    }), 500

# Inicializar la aplicación
if __name__ == '__main__':
    if initialize_ai():
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
    else:
        logger.error("No se pudo inicializar la aplicación")

# Para Vercel
def handler(request):
    """Handler para Vercel"""
    global ai_instance
    if ai_instance is None:
        initialize_ai()
    
    return app(request.environ, lambda *args: None)