"""
ChatBot IA con conexión real a MySQL
Optimizado para Vercel
"""

import os
import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from mangum import Mangum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de BD
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'bluebyte.space'),
    'user': os.getenv('DB_USER', 'bluebyte_angel'),
    'password': os.getenv('DB_PASSWORD', 'orbitalsoft'),
    'database': os.getenv('DB_NAME', 'bluebyte_dtai_web'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'autocommit': True,
    'charset': 'utf8mb4',
    'connect_timeout': 10
}

# FastAPI app
app = FastAPI(
    title="DTAI ChatBot IA con BD",
    description="IA conectada a MySQL en producción",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Modelos
class MensajeRequest(BaseModel):
    conversacionId: int
    mensaje: str

class MensajeResponse(BaseModel):
    respuesta: str
    datos_contexto: Dict[str, Any] = {}
    recomendaciones: List[str] = []

class ConversacionResponse(BaseModel):
    conversacionId: int
    mensaje: str

# Funciones de BD
def get_db_connection():
    """Crear conexión a MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error conectando a MySQL: {e}")
        raise

def ejecutar_consulta(query: str, params: tuple = None) -> List[Dict]:
    """Ejecutar consulta SQL"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return results
        else:
            return [{"affected_rows": cursor.rowcount, "lastrowid": cursor.lastrowid}]
            
    except Error as e:
        logger.error(f"Error ejecutando consulta: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Procesador de IA con BD real
class ChatBotIA:
    """IA que usa datos reales de MySQL"""
    
    def procesar_mensaje(self, mensaje: str, conversacion_id: int) -> Dict[str, Any]:
        """Procesar mensaje con datos reales de BD"""
        mensaje_lower = mensaje.lower()
        
        try:
            if any(word in mensaje_lower for word in ['cuantos', 'cantidad', 'total']) and 'estudiantes' in mensaje_lower:
                return self._consultar_estudiantes(mensaje_lower)
            
            elif 'profesores' in mensaje_lower or 'docentes' in mensaje_lower:
                return self._consultar_profesores(mensaje_lower)
            
            elif any(word in mensaje_lower for word in ['estadisticas', 'general', 'resumen']):
                return self._consultar_estadisticas()
            
            elif 'riesgo' in mensaje_lower:
                return self._consultar_riesgo()
            
            elif any(word in mensaje_lower for word in ['isc', 'sistemas']):
                return self._consultar_carrera('ISC')
            
            elif any(word in mensaje_lower for word in ['lae', 'administracion']):
                return self._consultar_carrera('LAE')
            
            elif 'calificaciones' in mensaje_lower or 'promedio' in mensaje_lower:
                return self._consultar_calificaciones()
            
            else:
                return self._respuesta_general(mensaje)
                
        except Exception as e:
            logger.error(f"Error en IA: {e}")
            return self._respuesta_error()
    
    def _consultar_estudiantes(self, mensaje: str) -> Dict[str, Any]:
        """Consultar estudiantes reales"""
        try:
            # Consulta principal de estudiantes
            query = """
            SELECT COUNT(*) as total 
            FROM alumnos 
            WHERE estado_alumno = 'activo'
            """
            resultado = ejecutar_consulta(query)
            total_estudiantes = resultado[0]['total'] if resultado else 0
            
            # Consulta por carreras
            query_carreras = """
            SELECT c.nombre as carrera, COUNT(a.id) as total
            FROM carreras c
            LEFT JOIN alumnos a ON c.id = a.carrera_id AND a.estado_alumno = 'activo'
            WHERE c.activa = TRUE
            GROUP BY c.id, c.nombre
            ORDER BY total DESC
            """
            carreras_data = ejecutar_consulta(query_carreras)
            
            # Promedio general
            query_promedio = """
            SELECT ROUND(AVG(promedio_general), 2) as promedio
            FROM alumnos 
            WHERE estado_alumno = 'activo' AND promedio_general > 0
            """
            promedio_result = ejecutar_consulta(query_promedio)
            promedio = promedio_result[0]['promedio'] if promedio_result and promedio_result[0]['promedio'] else 0
            
            # Formatear respuesta
            carreras_texto = "\n".join([f"• **{row['carrera']}:** {row['total']} estudiantes" for row in carreras_data[:5]])
            
            respuesta = f"""📊 **Estudiantes en DTAI (Datos en Tiempo Real):**

👨‍🎓 **Total de estudiantes activos:** {total_estudiantes}
📈 **Promedio general:** {promedio}

📚 **Distribución por carreras:**
{carreras_texto}

✅ **Datos actualizados desde la base de datos**"""

            return {
                'respuesta': respuesta,
                'datos_contexto': {
                    'tipo_consulta': 'estudiantes_reales',
                    'total': total_estudiantes,
                    'promedio': float(promedio) if promedio else 0,
                    'carreras': len(carreras_data)
                },
                'recomendaciones': [
                    "Consultar estudiantes por carrera específica",
                    "Revisar rendimiento académico detallado", 
                    "Identificar estudiantes que necesitan tutoría"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error consultando estudiantes: {e}")
            return self._respuesta_error()
    
    def _consultar_profesores(self, mensaje: str) -> Dict[str, Any]:
        """Consultar profesores reales"""
        try:
            query = """
            SELECT COUNT(*) as total
            FROM profesores 
            WHERE activo = TRUE
            """
            resultado = ejecutar_consulta(query)
            total_profesores = resultado[0]['total'] if resultado else 0
            
            # Profesores por carrera
            query_carreras = """
            SELECT c.nombre as carrera, COUNT(p.id) as total
            FROM carreras c
            LEFT JOIN profesores p ON c.id = p.carrera_id AND p.activo = TRUE
            WHERE c.activa = TRUE
            GROUP BY c.id, c.nombre
            ORDER BY total DESC
            """
            carreras_data = ejecutar_consulta(query_carreras)
            
            carreras_texto = "\n".join([f"• **{row['carrera']}:** {row['total']} profesores" for row in carreras_data[:5]])
            
            respuesta = f"""👨‍🏫 **Cuerpo Docente DTAI (Base de Datos Real):**

🎓 **Total de profesores activos:** {total_profesores}

📚 **Distribución por carreras:**
{carreras_texto}

✅ **Información actualizada en tiempo real**"""

            return {
                'respuesta': respuesta,
                'datos_contexto': {
                    'tipo_consulta': 'profesores_reales',
                    'total': total_profesores
                },
                'recomendaciones': [
                    "Ver profesores por especialidad",
                    "Consultar disponibilidad para tutorías",
                    "Revisar experiencia académica"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error consultando profesores: {e}")
            return self._respuesta_error()
    
    def _consultar_estadisticas(self) -> Dict[str, Any]:
        """Consultar estadísticas generales reales"""
        try:
            queries = {
                'estudiantes': "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'",
                'profesores': "SELECT COUNT(*) as total FROM profesores WHERE activo = TRUE",
                'carreras': "SELECT COUNT(*) as total FROM carreras WHERE activa = TRUE",
                'promedio': "SELECT ROUND(AVG(promedio_general), 2) as promedio FROM alumnos WHERE estado_alumno = 'activo' AND promedio_general > 0"
            }
            
            stats = {}
            for key, query in queries.items():
                resultado = ejecutar_consulta(query)
                if key == 'promedio':
                    stats[key] = resultado[0]['promedio'] if resultado and resultado[0]['promedio'] else 0
                else:
                    stats[key] = resultado[0]['total'] if resultado else 0
            
            respuesta = f"""📈 **Dashboard Académico DTAI (Tiempo Real):**

📚 **Estudiantes activos:** {stats['estudiantes']}
👨‍🏫 **Profesores activos:** {stats['profesores']}
🎓 **Carreras disponibles:** {stats['carreras']}
📊 **Promedio general:** {stats['promedio']}

✅ **Datos extraídos directamente de MySQL**
🔄 **Actualizado:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

            return {
                'respuesta': respuesta,
                'datos_contexto': {
                    'tipo_consulta': 'estadisticas_mysql',
                    'stats': stats,
                    'timestamp': datetime.now().isoformat()
                },
                'recomendaciones': [
                    "Revisar tendencias por período",
                    "Analizar crecimiento de matrícula",
                    "Consultar métricas específicas por carrera"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error consultando estadísticas: {e}")
            return self._respuesta_error()
    
    def _consultar_riesgo(self) -> Dict[str, Any]:
        """Consultar estudiantes en riesgo real"""
        try:
            # Verificar si existe la tabla de reportes de riesgo
            query_riesgo = """
            SELECT COUNT(*) as total_reportes
            FROM reportes_riesgo r
            JOIN alumnos a ON r.alumno_id = a.id
            WHERE r.estado IN ('abierto', 'en_proceso')
            """
            
            try:
                resultado = ejecutar_consulta(query_riesgo)
                total_riesgo = resultado[0]['total_reportes'] if resultado else 0
                
                # Si hay tabla de reportes, usarla
                if total_riesgo > 0:
                    query_detalle = """
                    SELECT r.nivel_riesgo, COUNT(*) as cantidad
                    FROM reportes_riesgo r
                    WHERE r.estado IN ('abierto', 'en_proceso')
                    GROUP BY r.nivel_riesgo
                    ORDER BY cantidad DESC
                    """
                    detalle = ejecutar_consulta(query_detalle)
                    
                    detalle_texto = "\n".join([f"• **{row['nivel_riesgo'].title()}:** {row['cantidad']} casos" for row in detalle])
                    
                    respuesta = f"""⚠️ **Estudiantes en Riesgo (Base de Datos Real):**

🚨 **Total de reportes activos:** {total_riesgo}

📊 **Distribución por nivel:**
{detalle_texto}

✅ **Datos actualizados de la tabla reportes_riesgo**"""
                else:
                    respuesta = "✅ **Excelente noticia:** No hay reportes de riesgo activos en el sistema actualmente."
                    
            except:
                # Si no existe la tabla, usar promedio bajo como indicador
                query_promedio_bajo = """
                SELECT COUNT(*) as total
                FROM alumnos 
                WHERE estado_alumno = 'activo' AND promedio_general < 7.0 AND promedio_general > 0
                """
                resultado = ejecutar_consulta(query_promedio_bajo)
                total_riesgo = resultado[0]['total'] if resultado else 0
                
                respuesta = f"""⚠️ **Análisis de Riesgo Académico (Basado en Promedios):**

📊 **Estudiantes con promedio < 7.0:** {total_riesgo}

💡 **Criterio usado:** Promedio general menor a 7.0
✅ **Datos extraídos de la tabla de alumnos**"""

            return {
                'respuesta': respuesta,
                'datos_contexto': {
                    'tipo_consulta': 'riesgo_real',
                    'total_casos': total_riesgo
                },
                'recomendaciones': [
                    "Programar sesiones de tutoría inmediata",
                    "Contactar a estudiantes identificados",
                    "Crear plan de seguimiento personalizado"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error consultando riesgo: {e}")
            return self._respuesta_error()
    
    def _consultar_carrera(self, carrera_codigo: str) -> Dict[str, Any]:
        """Consultar información específica de una carrera"""
        try:
            query = """
            SELECT c.nombre, COUNT(a.id) as total_estudiantes,
                   ROUND(AVG(a.promedio_general), 2) as promedio_carrera
            FROM carreras c
            LEFT JOIN alumnos a ON c.id = a.carrera_id AND a.estado_alumno = 'activo'
            WHERE c.codigo LIKE %s OR c.nombre LIKE %s
            GROUP BY c.id, c.nombre
            """
            
            like_pattern = f"%{carrera_codigo}%"
            resultado = ejecutar_consulta(query, (like_pattern, like_pattern))
            
            if resultado:
                carrera_data = resultado[0]
                nombre = carrera_data['nombre']
                total = carrera_data['total_estudiantes'] or 0
                promedio = carrera_data['promedio_carrera'] or 0
                
                respuesta = f"""🎓 **{nombre} (Datos Reales):**

👨‍🎓 **Estudiantes activos:** {total}
📊 **Promedio de carrera:** {promedio}

✅ **Información extraída directamente de MySQL**"""
            else:
                respuesta = f"❓ No se encontraron datos para la carrera '{carrera_codigo}' en la base de datos."

            return {
                'respuesta': respuesta,
                'datos_contexto': {
                    'tipo_consulta': 'carrera_especifica',
                    'carrera': carrera_codigo
                },
                'recomendaciones': [
                    "Consultar otras carreras disponibles",
                    "Ver distribución de estudiantes por cuatrimestre",
                    "Analizar rendimiento comparativo"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error consultando carrera: {e}")
            return self._respuesta_error()
    
    def _consultar_calificaciones(self) -> Dict[str, Any]:
        """Consultar análisis de calificaciones"""
        try:
            query = """
            SELECT c.nombre as carrera,
                   COUNT(a.id) as total_estudiantes,
                   ROUND(AVG(a.promedio_general), 2) as promedio,
                   ROUND(MIN(a.promedio_general), 2) as min_promedio,
                   ROUND(MAX(a.promedio_general), 2) as max_promedio
            FROM carreras c
            JOIN alumnos a ON c.id = a.carrera_id
            WHERE a.estado_alumno = 'activo' AND a.promedio_general > 0
            GROUP BY c.id, c.nombre
            ORDER BY promedio DESC
            """
            
            resultado = ejecutar_consulta(query)
            
            if resultado:
                calificaciones_texto = "\n".join([
                    f"• **{row['carrera']}:** {row['promedio']} (Min: {row['min_promedio']}, Max: {row['max_promedio']})"
                    for row in resultado[:6]
                ])
                
                respuesta = f"""📊 **Análisis de Calificaciones (Base de Datos Real):**

🎯 **Promedios por carrera:**
{calificaciones_texto}

✅ **Datos calculados en tiempo real desde MySQL**"""
            else:
                respuesta = "📊 No se encontraron datos de calificaciones en el sistema."

            return {
                'respuesta': respuesta,
                'datos_contexto': {
                    'tipo_consulta': 'calificaciones_reales',
                    'carreras_analizadas': len(resultado) if resultado else 0
                },
                'recomendaciones': [
                    "Implementar mejores prácticas de la carrera líder",
                    "Crear programas de apoyo para carreras con menor promedio",
                    "Reconocer estudiantes destacados"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error consultando calificaciones: {e}")
            return self._respuesta_error()
    
    def _respuesta_general(self, mensaje: str) -> Dict[str, Any]:
        """Respuesta general cuando no se identifica la consulta"""
        return {
            'respuesta': f"""🤖 **He recibido tu consulta:** "{mensaje}"

💡 **Puedo ayudarte con datos reales de la base de datos:**
📊 Estadísticas generales del sistema
👨‍🎓 Información de estudiantes por carrera  
👨‍🏫 Datos de profesores activos
⚠️ Análisis de estudiantes en riesgo
📈 Calificaciones y rendimiento académico
🎓 Información específica por carrera (ISC, LAE, etc.)

🔍 **Pregúntame algo específico para consultar la base de datos**""",
            'datos_contexto': {'tipo_consulta': 'general'},
            'recomendaciones': [
                "Pregunta sobre estadísticas generales",
                "Consulta información de una carrera específica", 
                "Solicita datos de estudiantes o profesores"
            ]
        }
    
    def _respuesta_error(self) -> Dict[str, Any]:
        """Respuesta en caso de error"""
        return {
            'respuesta': """❌ **Error temporal en la consulta a la base de datos**

🔧 **Posibles causas:**
• Conectividad temporal con MySQL
• Consulta muy compleja
• Sobrecarga del servidor

💡 **Sugerencias:**
• Intenta nuevamente en unos segundos
• Reformula tu pregunta de manera más simple
• Pregunta sobre temas generales primero""",
            'datos_contexto': {'tipo_consulta': 'error_bd'},
            'recomendaciones': [
                "Reintentar la consulta",
                "Verificar conectividad de red",
                "Probar con consultas más simples"
            ]
        }

# Instancia global del chatbot
chatbot = ChatBotIA()

# Endpoints
@app.get("/")
async def root():
    """Endpoint principal con test de BD"""
    try:
        # Test rápido de conexión
        query = "SELECT 1 as test"
        resultado = ejecutar_consulta(query)
        db_status = "✅ Conectada" if resultado else "❌ Error"
    except:
        db_status = "❌ Sin conexión"
    
    return {
        "message": "🤖 DTAI ChatBot IA con MySQL",
        "version": "2.0.0",
        "status": "✅ Activo",
        "database": db_status,
        "endpoints": {
            "health": "/health",
            "nueva_conversacion": "/api/chatbot/nueva-conversacion",
            "mensaje": "/api/chatbot/mensaje",
            "test_bd": "/test-bd"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check con verificación de BD"""
    try:
        # Test de BD más completo
        query = "SELECT COUNT(*) as total FROM usuarios LIMIT 1"
        resultado = ejecutar_consulta(query)
        db_status = "✅ MySQL conectado"
        tabla_usuarios = resultado[0]['total'] if resultado else 0
    except Exception as e:
        db_status = f"❌ Error BD: {str(e)[:50]}"
        tabla_usuarios = 0
    
    return {
        "status": "✅ healthy",
        "database": db_status,
        "usuarios_en_bd": tabla_usuarios,
        "ai_model": "✅ ChatBot activo",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-bd")
async def test_database():
    """Endpoint específico para probar BD"""
    try:
        tests = {}
        
        # Test 1: Conexión básica
        tests["conexion"] = "✅ OK"
        
        # Test 2: Contar usuarios
        query = "SELECT COUNT(*) as total FROM usuarios"
        resultado = ejecutar_consulta(query)
        tests["usuarios"] = resultado[0]['total'] if resultado else 0
        
        # Test 3: Contar alumnos
        query = "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'"
        resultado = ejecutar_consulta(query)
        tests["alumnos_activos"] = resultado[0]['total'] if resultado else 0
        
        # Test 4: Contar profesores
        query = "SELECT COUNT(*) as total FROM profesores WHERE activo = TRUE"
        resultado = ejecutar_consulta(query)
        tests["profesores_activos"] = resultado[0]['total'] if resultado else 0
        
        return {
            "status": "✅ Todas las pruebas exitosas",
            "tests": tests,
            "database_config": {
                "host": DB_CONFIG['host'],
                "database": DB_CONFIG['database'],
                "user": DB_CONFIG['user']
            }
        }
        
    except Exception as e:
        return {
            "status": "❌ Error en pruebas",
            "error": str(e),
            "database_config": {
                "host": DB_CONFIG['host'],
                "database": DB_CONFIG['database']
            }
        }

@app.post("/api/chatbot/nueva-conversacion", response_model=ConversacionResponse)
async def crear_nueva_conversacion():
    """Crear nueva conversación"""
    try:
        # Podrías guardar en BD si tienes tabla de conversaciones
        import random
        conv_id = random.randint(1000, 9999)
        
        return ConversacionResponse(
            conversacionId=conv_id,
            mensaje="✅ Conversación creada - Conectada a BD MySQL"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chatbot/mensaje", response_model=MensajeResponse)
async def procesar_mensaje(request: MensajeRequest):
    """Procesar mensaje con IA conectada a BD"""
    try:
        respuesta = chatbot.procesar_mensaje(
            mensaje=request.mensaje,
            conversacion_id=request.conversacionId
        )
        
        return MensajeResponse(
            respuesta=respuesta["respuesta"],
            datos_contexto=respuesta.get("datos_contexto", {}),
            recomendaciones=respuesta.get("recomendaciones", [])
        )
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        return MensajeResponse(
            respuesta=f"❌ Error procesando mensaje: {str(e)[:100]}...",
            datos_contexto={"error": True},
            recomendaciones=["Reintentar la consulta", "Verificar conectividad"]
        )

@app.get("/api/chatbot/conversaciones")
async def obtener_conversaciones():
    """Obtener conversaciones"""
    return [
        {
            "id": 1,
            "titulo": "Consulta con BD MySQL",
            "fecha_creacion": datetime.now().isoformat(),
            "fecha_actualizacion": datetime.now().isoformat()
        }
    ]

# Para Vercel
handler = Mangum(app)