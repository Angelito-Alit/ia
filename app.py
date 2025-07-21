from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import traceback
import mysql.connector
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'bluebyte.space'),
    'user': os.getenv('DB_USER', 'bluebyte_angel'),
    'password': os.getenv('DB_PASSWORD', 'orbitalsoft'),
    'database': os.getenv('DB_NAME', 'bluebyte_dtai_web'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        return None

def execute_query(query, params=None):
    """Ejecutar consulta en la base de datos"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or [])
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        logger.error(f"Error ejecutando consulta: {e}")
        if connection:
            connection.close()
        return None

def classify_intent(message):
    """Clasificador simple de intenciones"""
    message_lower = message.lower()
    
    # Patrones simples para clasificar intenciones
    if any(word in message_lower for word in ['calificaciones', 'notas', 'puntuaciones']):
        return 'ver_calificaciones'
    elif any(word in message_lower for word in ['riesgo', 'problema', 'dificultad']):
        return 'alumnos_riesgo' 
    elif any(word in message_lower for word in ['promedio', 'carrera', 'rendimiento']):
        return 'promedio_carreras'
    elif any(word in message_lower for word in ['horario', 'clases', 'calendario']):
        return 'mi_horario'
    elif any(word in message_lower for word in ['grupos', 'materias', 'asignados']):
        return 'mis_grupos'
    elif any(word in message_lower for word in ['solicitudes', 'ayuda', 'pendientes']):
        return 'solicitudes_pendientes'
    elif any(word in message_lower for word in ['estadisticas', 'resumen', 'general']):
        return 'estadisticas_generales'
    else:
        return 'consulta_general'

def generate_sql_query(intent, user_role, user_id=None):
    """Generar consulta SQL basada en la intención"""
    
    if intent == 'ver_calificaciones' and user_role == 'alumno':
        return """
        SELECT a.nombre, a.codigo, c.calificacion_final, c.estatus
        FROM calificaciones c
        JOIN asignaturas a ON c.asignatura_id = a.id
        JOIN alumnos al ON c.alumno_id = al.id
        WHERE al.usuario_id = %s
        ORDER BY a.nombre
        """, [user_id]
    
    elif intent == 'alumnos_riesgo':
        return """
        SELECT u.nombre, u.apellido, al.matricula, rr.nivel_riesgo, rr.tipo_riesgo
        FROM reportes_riesgo rr
        JOIN alumnos al ON rr.alumno_id = al.id
        JOIN usuarios u ON al.usuario_id = u.id
        WHERE rr.estado IN ('abierto', 'en_proceso')
        ORDER BY CASE rr.nivel_riesgo 
            WHEN 'critico' THEN 1 
            WHEN 'alto' THEN 2 
            ELSE 3 END
        LIMIT 10
        """, []
    
    elif intent == 'promedio_carreras':
        return """
        SELECT c.nombre as carrera, 
               COUNT(al.id) as total_alumnos,
               AVG(al.promedio_general) as promedio_carrera
        FROM carreras c
        LEFT JOIN alumnos al ON c.id = al.carrera_id
        WHERE al.estado_alumno = 'activo'
        GROUP BY c.id, c.nombre
        ORDER BY promedio_carrera DESC
        """, []
    
    elif intent == 'estadisticas_generales':
        return """
        SELECT 
            'Total Alumnos' as concepto,
            COUNT(*) as valor
        FROM alumnos WHERE estado_alumno = 'activo'
        UNION ALL
        SELECT 
            'Alumnos en Riesgo' as concepto,
            COUNT(*) as valor
        FROM alumnos WHERE promedio_general < 7.0 AND estado_alumno = 'activo'
        """, []
    
    else:
        return """
        SELECT 'Consulta no implementada' as mensaje, 
               %s as intent_detectado
        """, [intent]

def format_response(data, intent):
    """Formatear respuesta de manera natural"""
    if not data:
        return "No encontré información para tu consulta."
    
    if intent == 'ver_calificaciones':
        response = "📊 **Tus Calificaciones:**\n\n"
        for row in data:
            status = "✅" if row['estatus'] == 'aprobado' else "⚠️"
            response += f"{status} **{row['nombre']}** ({row['codigo']})\n"
            response += f"   Calificación: {row['calificacion_final'] or 'Sin calificar'}\n\n"
        return response
    
    elif intent == 'alumnos_riesgo':
        response = f"🚨 **Alumnos en Riesgo** ({len(data)} encontrados)\n\n"
        for row in data:
            emoji = "🔴" if row['nivel_riesgo'] == 'critico' else "🟡"
            response += f"{emoji} **{row['nombre']} {row['apellido']}** ({row['matricula']})\n"
            response += f"   Riesgo: {row['nivel_riesgo']} - {row['tipo_riesgo']}\n\n"
        return response
    
    elif intent == 'promedio_carreras':
        response = "📈 **Rendimiento por Carrera:**\n\n"
        for row in data:
            response += f"**{row['carrera']}**\n"
            response += f"   Alumnos: {row['total_alumnos']}\n"
            response += f"   Promedio: {row['promedio_carrera']:.2f}\n\n"
        return response
    
    elif intent == 'estadisticas_generales':
        response = "📊 **Estadísticas del Sistema:**\n\n"
        for row in data:
            response += f"• **{row['concepto']}**: {row['valor']}\n"
        return response
    
    else:
        return f"He encontrado {len(data)} resultados para tu consulta."

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
    """Endpoint principal para conversación"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Mensaje requerido"}), 400
        
        user_message = data['message']
        user_role = data.get('role', 'alumno')
        user_id = data.get('user_id', 1)
        
        # Clasificar intención
        intent = classify_intent(user_message)
        
        # Generar consulta SQL
        query, params = generate_sql_query(intent, user_role, user_id)
        
        # Ejecutar consulta
        result_data = execute_query(query, params)
        
        # Formatear respuesta
        response_text = format_response(result_data, intent)
        
        return jsonify({
            "success": True,
            "response": response_text,
            "intent": intent,
            "data": result_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        return jsonify({
            "success": False,
            "error": "Error procesando mensaje",
            "details": str(e)
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Obtener sugerencias de preguntas"""
    role = request.args.get('role', 'alumno')
    
    suggestions = {
        'alumno': [
            "¿Cuáles son mis calificaciones?",
            "¿Cómo van mis notas este cuatrimestre?",
            "¿Cuál es mi horario de clases?",
            "¿Tengo alguna materia en riesgo?"
        ],
        'profesor': [
            "¿Qué alumnos están en riesgo?",
            "¿Cuáles son mis grupos asignados?",
            "¿Hay reportes pendientes?",
            "¿Cómo van las calificaciones de mis grupos?"
        ],
        'directivo': [
            "¿Cuáles son las estadísticas generales?",
            "¿Cómo va el rendimiento por carrera?",
            "¿Qué alumnos necesitan atención?",
            "¿Hay solicitudes de ayuda pendientes?"
        ]
    }
    
    return jsonify({
        "success": True,
        "suggestions": suggestions.get(role, suggestions['alumno'])
    })

@app.route('/api/test', methods=['GET'])
def test_db():
    """Probar conexión a la base de datos"""
    try:
        result = execute_query("SELECT 1 as test")
        if result:
            return jsonify({
                "success": True,
                "message": "Conexión a BD exitosa",
                "test_result": result[0]
            })
        else:
            return jsonify({
                "success": False,
                "message": "Error conectando a BD"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Para desarrollo local
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# Para Vercel - Export requerido
def handler(event, context):
    return app(event, context)