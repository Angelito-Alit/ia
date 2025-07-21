from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import traceback
import sys

# Configurar logging para Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app, origins=["*"])

# Variables globales para conexión
db_connection = None

def get_db_connection():
    """Crear conexión a la base de datos con manejo de errores"""
    global db_connection
    
    try:
        import mysql.connector
        
        config = {
            'host': os.environ.get('DB_HOST', 'bluebyte.space'),
            'user': os.environ.get('DB_USER', 'bluebyte_angel'), 
            'password': os.environ.get('DB_PASSWORD', 'orbitalsoft'),
            'database': os.environ.get('DB_NAME', 'bluebyte_dtai_web'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'autocommit': True,
            'connect_timeout': 10,
            'use_unicode': True
        }
        
        logger.info("Intentando conectar a la base de datos...")
        connection = mysql.connector.connect(**config)
        logger.info("Conexión exitosa a la base de datos")
        return connection
        
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def execute_query(query, params=None):
    """Ejecutar consulta con manejo robusto de errores"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if not connection:
            logger.error("No se pudo establecer conexión a la BD")
            return None
        
        cursor = connection.cursor(dictionary=True)
        logger.info(f"Ejecutando query: {query[:100]}...")
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        result = cursor.fetchall()
        logger.info(f"Query ejecutada exitosamente, {len(result)} filas")
        return result
        
    except Exception as e:
        logger.error(f"Error ejecutando consulta: {str(e)}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None
        
    finally:
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
        except Exception as e:
            logger.error(f"Error cerrando conexión: {str(e)}")

def classify_intent(message):
    """Clasificador simple de intenciones"""
    try:
        if not message:
            return 'consulta_general'
            
        message_lower = message.lower().strip()
        logger.info(f"Clasificando mensaje: {message_lower}")
        
        # Patrones de intenciones
        patterns = {
            'ver_calificaciones': ['calificaciones', 'notas', 'puntuaciones', 'resultados'],
            'alumnos_riesgo': ['riesgo', 'problema', 'dificultad', 'ayuda', 'atencion'],
            'promedio_carreras': ['promedio', 'carrera', 'rendimiento', 'desempeño'],
            'estadisticas_generales': ['estadisticas', 'resumen', 'general', 'numeros', 'total'],
            'mi_horario': ['horario', 'clases', 'calendario', 'cuando'],
            'mis_grupos': ['grupos', 'materias', 'asignados', 'imparto']
        }
        
        for intent, keywords in patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                logger.info(f"Intención detectada: {intent}")
                return intent
        
        logger.info("Intención no específica, usando general")
        return 'consulta_general'
        
    except Exception as e:
        logger.error(f"Error clasificando intención: {str(e)}")
        return 'consulta_general'

def generate_sql_query(intent, user_role='alumno', user_id=1):
    """Generar consulta SQL simple y segura"""
    try:
        logger.info(f"Generando SQL para intent: {intent}, role: {user_role}")
        
        queries = {
            'ver_calificaciones': (
                """SELECT a.nombre, a.codigo, c.calificacion_final, c.estatus
                   FROM calificaciones c
                   JOIN asignaturas a ON c.asignatura_id = a.id  
                   JOIN alumnos al ON c.alumno_id = al.id
                   WHERE al.usuario_id = %s
                   LIMIT 10""",
                [user_id]
            ),
            
            'alumnos_riesgo': (
                """SELECT u.nombre, u.apellido, al.matricula, 
                          rr.nivel_riesgo, rr.tipo_riesgo, rr.descripcion
                   FROM reportes_riesgo rr
                   JOIN alumnos al ON rr.alumno_id = al.id
                   JOIN usuarios u ON al.usuario_id = u.id  
                   WHERE rr.estado IN ('abierto', 'en_proceso')
                   ORDER BY rr.nivel_riesgo DESC
                   LIMIT 5""",
                []
            ),
            
            'promedio_carreras': (
                """SELECT c.nombre as carrera, 
                          COUNT(al.id) as total_alumnos,
                          ROUND(AVG(al.promedio_general), 2) as promedio_carrera
                   FROM carreras c
                   LEFT JOIN alumnos al ON c.id = al.carrera_id 
                   WHERE al.estado_alumno = 'activo'
                   GROUP BY c.id, c.nombre
                   ORDER BY promedio_carrera DESC
                   LIMIT 10""",
                []
            ),
            
            'estadisticas_generales': (
                """SELECT 'Total Alumnos Activos' as concepto, COUNT(*) as valor
                   FROM alumnos WHERE estado_alumno = 'activo'
                   UNION ALL
                   SELECT 'Total Carreras', COUNT(*) FROM carreras WHERE activa = 1
                   UNION ALL  
                   SELECT 'Reportes Abiertos', COUNT(*) FROM reportes_riesgo 
                   WHERE estado IN ('abierto', 'en_proceso')""",
                []
            )
        }
        
        return queries.get(intent, (
            "SELECT 'Consulta no disponible' as mensaje, %s as intent",
            [intent]
        ))
        
    except Exception as e:
        logger.error(f"Error generando SQL: {str(e)}")
        return "SELECT 'Error en consulta' as mensaje", []

def format_response(data, intent):
    """Formatear respuesta de manera simple"""
    try:
        if not data:
            return "No encontré información para tu consulta. 🤔"
        
        if intent == 'ver_calificaciones':
            response = "📊 **Tus Calificaciones:**\n\n"
            for row in data:
                status = "✅" if row.get('estatus') == 'aprobado' else "📝"
                response += f"{status} {row.get('nombre', 'N/A')} - {row.get('calificacion_final', 'Sin calificar')}\n"
            return response
            
        elif intent == 'alumnos_riesgo':
            response = f"🚨 **Alumnos en Riesgo** ({len(data)} encontrados):\n\n"
            for row in data:
                response += f"• {row.get('nombre', '')} {row.get('apellido', '')} - {row.get('nivel_riesgo', '')}\n"
            return response
            
        elif intent == 'promedio_carreras':
            response = "📈 **Promedios por Carrera:**\n\n"
            for row in data:
                response += f"• {row.get('carrera', '')}: {row.get('promedio_carrera', 0)} ({row.get('total_alumnos', 0)} alumnos)\n"
            return response
            
        elif intent == 'estadisticas_generales':
            response = "📊 **Estadísticas Generales:**\n\n"
            for row in data:
                response += f"• {row.get('concepto', '')}: {row.get('valor', 0)}\n"
            return response
        
        else:
            return f"Encontré {len(data)} resultados para tu consulta."
            
    except Exception as e:
        logger.error(f"Error formateando respuesta: {str(e)}")
        return "Error procesando la respuesta. 😅"

@app.route('/', methods=['GET'])
def health_check():
    """Health check básico"""
    try:
        return jsonify({
            "status": "ok",
            "message": "IA Conversacional funcionando",
            "version": "1.0.0",
            "timestamp": "2024"
        })
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return jsonify({"error": "Health check failed"}), 500

@app.route('/api/test', methods=['GET'])
def test_connection():
    """Probar conexión a la base de datos"""
    try:
        logger.info("Probando conexión a la base de datos...")
        result = execute_query("SELECT 1 as test, 'Conexión exitosa' as mensaje")
        
        if result:
            return jsonify({
                "success": True,
                "message": "Conexión a BD exitosa ✅",
                "result": result[0]
            })
        else:
            return jsonify({
                "success": False,
                "message": "Error conectando a BD ❌"
            }), 500
            
    except Exception as e:
        logger.error(f"Error en test de conexión: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Endpoint principal para chat"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
        
    try:
        logger.info("Procesando mensaje de chat...")
        
        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        message = data.get('message', '').strip()
        if not message:
            return jsonify({"error": "Mensaje vacío"}), 400
            
        user_role = data.get('role', 'alumno')
        user_id = data.get('user_id', 1)
        
        logger.info(f"Mensaje: '{message}', Role: {user_role}, ID: {user_id}")
        
        # Clasificar intención
        intent = classify_intent(message)
        
        # Generar y ejecutar consulta
        query, params = generate_sql_query(intent, user_role, user_id)
        result_data = execute_query(query, params)
        
        # Formatear respuesta
        response_text = format_response(result_data, intent)
        
        return jsonify({
            "success": True,
            "response": response_text,
            "intent": intent,
            "data_count": len(result_data) if result_data else 0,
            "timestamp": "2024"
        })
        
    except Exception as e:
        logger.error(f"Error en chat endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "message": "Intenta de nuevo en un momento",
            "details": str(e) if os.environ.get('DEBUG') else None
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Obtener sugerencias simples"""
    try:
        role = request.args.get('role', 'alumno')
        
        suggestions = {
            'alumno': [
                "¿Cuáles son mis calificaciones?",
                "¿Cómo van mis notas?",
                "Mostrar mis resultados"
            ],
            'profesor': [
                "¿Qué alumnos están en riesgo?",
                "¿Cuáles son mis grupos?",
                "Mostrar reportes pendientes"
            ],
            'directivo': [
                "¿Cuáles son las estadísticas generales?",
                "¿Cómo va el rendimiento por carrera?",
                "Mostrar alumnos en riesgo"
            ]
        }
        
        return jsonify({
            "success": True,
            "suggestions": suggestions.get(role, suggestions['alumno'])
        })
        
    except Exception as e:
        logger.error(f"Error en suggestions: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error 500: {str(error)}")
    return jsonify({"error": "Error interno del servidor"}), 500

# Para desarrollo local
if __name__ == '__main__':
    logger.info("Iniciando aplicación en modo desarrollo...")
    app.run(host='0.0.0.0', port=5000, debug=True)

# Export para Vercel
application = app