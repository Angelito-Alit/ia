"""
Gestor de Base de Datos para ChatBot IA
"""

import mysql.connector
from mysql.connector import Error
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexiones y consultas a MySQL"""
    
    def __init__(self):
        self.connection_config = {
            'host': settings.DB_HOST,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'database': settings.DB_NAME,
            'port': settings.DB_PORT,
            'autocommit': True,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
    
    def get_connection(self):
        """Crear nueva conexión a la BD"""
        try:
            connection = mysql.connector.connect(**self.connection_config)
            return connection
        except Error as e:
            logger.error(f"Error conectando a MySQL: {e}")
            raise
    
    async def check_connection(self) -> bool:
        """Verificar conexión a la BD"""
        try:
            connection = self.get_connection()
            if connection.is_connected():
                connection.close()
                return True
            return False
        except:
            return False
    
    async def ejecutar_consulta(self, query: str, params: tuple = None) -> List[Dict]:
        """Ejecutar consulta SQL y retornar resultados"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Si es SELECT, retornar resultados
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return results
            else:
                # Para INSERT, UPDATE, DELETE
                return [{"affected_rows": cursor.rowcount, "lastrowid": cursor.lastrowid}]
                
        except Error as e:
            logger.error(f"Error ejecutando consulta: {e}")
            logger.error(f"Query: {query}")
            raise
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    async def crear_conversacion(self, directivo_id: int) -> int:
        """Crear nueva conversación"""
        query = """
        INSERT INTO conversaciones_chatbot (directivo_id, titulo, fecha_creacion, fecha_actualizacion)
        VALUES (%s, %s, NOW(), NOW())
        """
        params = (directivo_id, "Nueva conversación")
        
        result = await self.ejecutar_consulta(query, params)
        return result[0]["lastrowid"]
    
    async def obtener_conversaciones(self, directivo_id: int) -> List[Dict]:
        """Obtener conversaciones del usuario"""
        query = """
        SELECT id, titulo, fecha_creacion, fecha_actualizacion
        FROM conversaciones_chatbot 
        WHERE directivo_id = %s 
        ORDER BY fecha_actualizacion DESC
        LIMIT 20
        """
        params = (directivo_id,)
        
        return await self.ejecutar_consulta(query, params)
    
    async def guardar_mensaje(self, conversacion_id: int, tipo_mensaje: str, contenido: str):
        """Guardar mensaje en la conversación"""
        query = """
        INSERT INTO mensajes_chatbot (conversacion_id, tipo_mensaje, contenido, timestamp)
        VALUES (%s, %s, %s, NOW())
        """
        params = (conversacion_id, tipo_mensaje, contenido)
        
        await self.ejecutar_consulta(query, params)
        
        # Actualizar timestamp de la conversación
        update_query = """
        UPDATE conversaciones_chatbot 
        SET fecha_actualizacion = NOW() 
        WHERE id = %s
        """
        await self.ejecutar_consulta(update_query, (conversacion_id,))
    
    async def obtener_mensajes_conversacion(self, conversacion_id: int) -> List[Dict]:
        """Obtener mensajes de una conversación"""
        query = """
        SELECT id, tipo_mensaje, contenido, timestamp
        FROM mensajes_chatbot 
        WHERE conversacion_id = %s 
        ORDER BY timestamp ASC
        """
        params = (conversacion_id,)
        
        return await self.ejecutar_consulta(query, params)
    
    # CONSULTAS ESPECIALIZADAS PARA LA IA
    
    async def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtener estadísticas generales del sistema"""
        queries = {
            "total_alumnos": "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'",
            "total_profesores": "SELECT COUNT(*) as total FROM profesores WHERE activo = TRUE",
            "total_carreras": "SELECT COUNT(*) as total FROM carreras WHERE activa = TRUE", 
            "total_grupos": "SELECT COUNT(*) as total FROM grupos WHERE activo = TRUE"
        }
        
        estadisticas = {}
        for key, query in queries.items():
            result = await self.ejecutar_consulta(query)
            estadisticas[key] = result[0]["total"] if result else 0
        
        return estadisticas
    
    async def obtener_alumnos_por_carrera(self, carrera_nombre: str = None) -> List[Dict]:
        """Obtener alumnos por carrera"""
        if carrera_nombre:
            query = """
            SELECT a.matricula, u.nombre, u.apellido, c.nombre as carrera, 
                   a.cuatrimestre_actual, a.promedio_general, a.estado_alumno
            FROM alumnos a
            JOIN usuarios u ON a.usuario_id = u.id
            JOIN carreras c ON a.carrera_id = c.id
            WHERE c.nombre LIKE %s AND a.estado_alumno = 'activo'
            ORDER BY a.promedio_general DESC
            """
            params = (f"%{carrera_nombre}%",)
        else:
            query = """
            SELECT a.matricula, u.nombre, u.apellido, c.nombre as carrera, 
                   a.cuatrimestre_actual, a.promedio_general, a.estado_alumno
            FROM alumnos a
            JOIN usuarios u ON a.usuario_id = u.id
            JOIN carreras c ON a.carrera_id = c.id
            WHERE a.estado_alumno = 'activo'
            ORDER BY c.nombre, a.promedio_general DESC
            """
            params = None
        
        return await self.ejecutar_consulta(query, params)
    
    async def obtener_alumnos_riesgo(self, nivel_riesgo: str = None) -> List[Dict]:
        """Obtener alumnos en riesgo académico"""
        base_query = """
        SELECT DISTINCT a.matricula, u.nombre, u.apellido, c.nombre as carrera,
               r.tipo_riesgo, r.nivel_riesgo, r.descripcion, r.fecha_reporte
        FROM reportes_riesgo r
        JOIN alumnos a ON r.alumno_id = a.id
        JOIN usuarios u ON a.usuario_id = u.id
        JOIN carreras c ON a.carrera_id = c.id
        WHERE r.estado IN ('abierto', 'en_proceso')
        """
        
        if nivel_riesgo:
            query = base_query + " AND r.nivel_riesgo = %s ORDER BY r.fecha_reporte DESC"
            params = (nivel_riesgo,)
        else:
            query = base_query + " ORDER BY r.nivel_riesgo DESC, r.fecha_reporte DESC"
            params = None
        
        return await self.ejecutar_consulta(query, params)
    
    async def obtener_profesores_activos(self) -> List[Dict]:
        """Obtener profesores activos"""
        query = """
        SELECT p.numero_empleado, u.nombre, u.apellido, c.nombre as carrera,
               p.titulo_academico, p.especialidad, p.experiencia_años
        FROM profesores p
        JOIN usuarios u ON p.usuario_id = u.id
        JOIN carreras c ON p.carrera_id = c.id
        WHERE p.activo = TRUE
        ORDER BY c.nombre, u.apellido
        """
        
        return await self.ejecutar_consulta(query)
    
    async def obtener_promedio_por_carrera(self) -> List[Dict]:
        """Obtener promedio general por carrera"""
        query = """
        SELECT c.nombre as carrera, 
               AVG(a.promedio_general) as promedio_carrera,
               COUNT(a.id) as total_alumnos
        FROM carreras c
        JOIN alumnos a ON c.id = a.carrera_id
        WHERE a.estado_alumno = 'activo' AND a.promedio_general > 0
        GROUP BY c.id, c.nombre
        ORDER BY promedio_carrera DESC
        """
        
        return await self.ejecutar_consulta(query)
    
    async def buscar_estudiante(self, termino_busqueda: str) -> List[Dict]:
        """Buscar estudiante por nombre, apellido o matrícula"""
        query = """
        SELECT a.matricula, u.nombre, u.apellido, c.nombre as carrera,
               a.cuatrimestre_actual, a.promedio_general, a.estado_alumno
        FROM alumnos a
        JOIN usuarios u ON a.usuario_id = u.id
        JOIN carreras c ON a.carrera_id = c.id
        WHERE (u.nombre LIKE %s OR u.apellido LIKE %s OR a.matricula LIKE %s)
        AND a.estado_alumno = 'activo'
        ORDER BY u.apellido, u.nombre
        """
        termino = f"%{termino_busqueda}%"
        params = (termino, termino, termino)
        
        return await self.ejecutar_consulta(query, params)