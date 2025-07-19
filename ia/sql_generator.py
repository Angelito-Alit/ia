"""
Generador inteligente de consultas SQL
Convierte intenciones en consultas SQL optimizadas
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SQLGenerator:
    """Generador de consultas SQL basado en intenciones y entidades"""
    
    def __init__(self):
        self.table_schemas = self._load_table_schemas()
        self.query_templates = self._load_query_templates()
    
    def _load_table_schemas(self) -> Dict[str, Dict]:
        """Esquemas de las tablas principales"""
        return {
            'alumnos': {
                'primary_table': 'alumnos a',
                'joins': [
                    'JOIN usuarios u ON a.usuario_id = u.id',
                    'JOIN carreras c ON a.carrera_id = c.id'
                ],
                'fields': {
                    'matricula': 'a.matricula',
                    'nombre': 'u.nombre',
                    'apellido': 'u.apellido', 
                    'carrera': 'c.nombre',
                    'cuatrimestre': 'a.cuatrimestre_actual',
                    'promedio': 'a.promedio_general',
                    'estado': 'a.estado_alumno'
                },
                'filters': {
                    'activos': "a.estado_alumno = 'activo'",
                    'carrera': "c.nombre LIKE '%{value}%'",
                    'cuatrimestre': "a.cuatrimestre_actual = {value}",
                    'promedio_bajo': "a.promedio_general < {value}",
                    'promedio_alto': "a.promedio_general >= {value}"
                }
            },
            
            'profesores': {
                'primary_table': 'profesores p',
                'joins': [
                    'JOIN usuarios u ON p.usuario_id = u.id',
                    'JOIN carreras c ON p.carrera_id = c.id'
                ],
                'fields': {
                    'numero_empleado': 'p.numero_empleado',
                    'nombre': 'u.nombre',
                    'apellido': 'u.apellido',
                    'carrera': 'c.nombre',
                    'titulo': 'p.titulo_academico',
                    'especialidad': 'p.especialidad',
                    'experiencia': 'p.experiencia_años'
                },
                'filters': {
                    'activos': 'p.activo = TRUE',
                    'carrera': "c.nombre LIKE '%{value}%'",
                    'tutor': 'p.es_tutor = TRUE'
                }
            },
            
            'reportes_riesgo': {
                'primary_table': 'reportes_riesgo r',
                'joins': [
                    'JOIN alumnos a ON r.alumno_id = a.id',
                    'JOIN usuarios u ON a.usuario_id = u.id',
                    'JOIN carreras c ON a.carrera_id = c.id'
                ],
                'fields': {
                    'matricula': 'a.matricula',
                    'nombre': 'u.nombre',
                    'apellido': 'u.apellido',
                    'carrera': 'c.nombre',
                    'tipo_riesgo': 'r.tipo_riesgo',
                    'nivel_riesgo': 'r.nivel_riesgo',
                    'descripcion': 'r.descripcion',
                    'fecha': 'r.fecha_reporte'
                },
                'filters': {
                    'abiertos': "r.estado IN ('abierto', 'en_proceso')",
                    'tipo': "r.tipo_riesgo = '{value}'",
                    'nivel': "r.nivel_riesgo = '{value}'",
                    'carrera': "c.nombre LIKE '%{value}%'"
                }
            },
            
            'carreras': {
                'primary_table': 'carreras c',
                'joins': [],
                'fields': {
                    'nombre': 'c.nombre',
                    'codigo': 'c.codigo',
                    'descripcion': 'c.descripcion',
                    'duracion': 'c.duracion_cuatrimestres'
                },
                'filters': {
                    'activas': 'c.activa = TRUE'
                }
            }
        }
    
    def _load_query_templates(self) -> Dict[str, str]:
        """Templates de consultas por intención"""
        return {
            'estadisticas_generales': {
                'alumnos_total': "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'",
                'profesores_total': "SELECT COUNT(*) as total FROM profesores WHERE activo = TRUE",
                'carreras_total': "SELECT COUNT(*) as total FROM carreras WHERE activa = TRUE",
                'promedio_general': "SELECT AVG(promedio_general) as promedio FROM alumnos WHERE estado_alumno = 'activo' AND promedio_general > 0"
            },
            
            'consulta_alumnos': """
                SELECT {fields}
                FROM {table} {joins}
                WHERE {filters}
                ORDER BY {order_by}
                LIMIT {limit}
            """,
            
            'consulta_profesores': """
                SELECT {fields}
                FROM {table} {joins}
                WHERE {filters}
                ORDER BY {order_by}
                LIMIT {limit}
            """,
            
            'alumnos_riesgo': """
                SELECT DISTINCT {fields}
                FROM {table} {joins}
                WHERE {filters}
                ORDER BY {order_by}
                LIMIT {limit}
            """,
            
            'promedio_por_carrera': """
                SELECT c.nombre as carrera, 
                       AVG(a.promedio_general) as promedio_carrera,
                       COUNT(a.id) as total_alumnos
                FROM carreras c
                JOIN alumnos a ON c.id = a.carrera_id
                WHERE a.estado_alumno = 'activo' AND a.promedio_general > 0
                GROUP BY c.id, c.nombre
                ORDER BY promedio_carrera DESC
            """
        }
    
    def generate_query(self, intent: str, entities: Dict[str, Any], search_terms: List[str] = None) -> Dict[str, Any]:
        """Generar consulta SQL basada en intención y entidades"""
        
        try:
            if intent == 'estadisticas_generales':
                return self._generate_stats_queries()
            
            elif intent == 'consulta_alumnos':
                return self._generate_students_query(entities, search_terms)
            
            elif intent == 'consulta_profesores':
                return self._generate_teachers_query(entities, search_terms)
            
            elif intent == 'alumnos_riesgo':
                return self._generate_risk_query(entities)
            
            elif intent == 'calificaciones_promedio':
                return self._generate_grades_query(entities)
            
            elif intent == 'busqueda_especifica':
                return self._generate_search_query(entities, search_terms)
            
            else:
                return self._generate_general_query(search_terms)
                
        except Exception as e:
            logger.error(f"Error generando consulta para intent '{intent}': {e}")
            return self._generate_fallback_query()
    
    def _generate_stats_queries(self) -> Dict[str, Any]:
        """Generar consultas para estadísticas generales"""
        return {
            'query_type': 'multiple',
            'queries': {
                'total_alumnos': "SELECT COUNT(*) as total FROM alumnos WHERE estado_alumno = 'activo'",
                'total_profesores': "SELECT COUNT(*) as total FROM profesores WHERE activo = TRUE",
                'total_carreras': "SELECT COUNT(*) as total FROM carreras WHERE activa = TRUE",
                'promedio_general': "SELECT ROUND(AVG(promedio_general), 2) as promedio FROM alumnos WHERE estado_alumno = 'activo' AND promedio_general > 0"
            }
        }
    
    def _generate_students_query(self, entities: Dict[str, Any], search_terms: List[str] = None) -> Dict[str, Any]:
        """Generar consulta para estudiantes"""
        schema = self.table_schemas['alumnos']
        
        # Campos a seleccionar
        fields = [
            'a.matricula',
            'u.nombre',
            'u.apellido', 
            'c.nombre as carrera',
            'a.cuatrimestre_actual',
            'a.promedio_general',
            'a.estado_alumno'
        ]
        
        # Condiciones WHERE
        conditions = [schema['filters']['activos']]
        
        # Filtrar por carrera si se especifica
        if entities.get('carreras'):
            carrera = entities['carreras'][0]
            conditions.append(f"c.nombre LIKE '%{carrera}%'")
        
        # Filtrar por cuatrimestre
        if entities.get('cuatrimestres'):
            cuatri = entities['cuatrimestres'][0]
            if cuatri.isdigit():
                conditions.append(f"a.cuatrimestre_actual = {cuatri}")
        
        # Búsqueda por términos
        if search_terms:
            search_conditions = []
            for term in search_terms:
                search_conditions.extend([
                    f"u.nombre LIKE '%{term}%'",
                    f"u.apellido LIKE '%{term}%'",
                    f"a.matricula LIKE '%{term}%'"
                ])
            if search_conditions:
                conditions.append(f"({' OR '.join(search_conditions)})")
        
        query = f"""
            SELECT {', '.join(fields)}
            FROM {schema['primary_table']}
            {' '.join(schema['joins'])}
            WHERE {' AND '.join(conditions)}
            ORDER BY u.apellido, u.nombre
            LIMIT 30
        """
        
        return {
            'query_type': 'single',
            'query': query.strip(),
            'description': 'Consulta de profesores'
        }
    
    def _generate_risk_query(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generar consulta para alumnos en riesgo"""
        schema = self.table_schemas['reportes_riesgo']
        
        fields = [
            'DISTINCT a.matricula',
            'u.nombre',
            'u.apellido',
            'c.nombre as carrera',
            'r.tipo_riesgo',
            'r.nivel_riesgo',
            'r.descripcion',
            'r.fecha_reporte'
        ]
        
        conditions = [schema['filters']['abiertos']]
        
        # Filtrar por tipo de riesgo
        if entities.get('tipos_riesgo'):
            tipo = entities['tipos_riesgo'][0]
            conditions.append(f"r.tipo_riesgo = '{tipo}'")
        
        # Filtrar por nivel de riesgo
        if entities.get('niveles_riesgo'):
            nivel = entities['niveles_riesgo'][0]
            conditions.append(f"r.nivel_riesgo = '{nivel}'")
        
        # Filtrar por carrera
        if entities.get('carreras'):
            carrera = entities['carreras'][0]
            conditions.append(f"c.nombre LIKE '%{carrera}%'")
        
        query = f"""
            SELECT {', '.join(fields)}
            FROM {schema['primary_table']}
            {' '.join(schema['joins'])}
            WHERE {' AND '.join(conditions)}
            ORDER BY r.nivel_riesgo DESC, r.fecha_reporte DESC
            LIMIT 40
        """
        
        return {
            'query_type': 'single',
            'query': query.strip(),
            'description': 'Consulta de alumnos en riesgo'
        }
    
    def _generate_grades_query(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generar consulta para calificaciones y promedios"""
        
        if entities.get('carreras'):
            # Promedio por carrera específica
            carrera = entities['carreras'][0]
            query = f"""
                SELECT c.nombre as carrera,
                       ROUND(AVG(a.promedio_general), 2) as promedio_carrera,
                       COUNT(a.id) as total_alumnos,
                       ROUND(MIN(a.promedio_general), 2) as promedio_minimo,
                       ROUND(MAX(a.promedio_general), 2) as promedio_maximo
                FROM carreras c
                JOIN alumnos a ON c.id = a.carrera_id
                WHERE a.estado_alumno = 'activo' 
                AND a.promedio_general > 0
                AND c.nombre LIKE '%{carrera}%'
                GROUP BY c.id, c.nombre
            """
        else:
            # Promedio general por todas las carreras
            query = """
                SELECT c.nombre as carrera,
                       ROUND(AVG(a.promedio_general), 2) as promedio_carrera,
                       COUNT(a.id) as total_alumnos,
                       ROUND(MIN(a.promedio_general), 2) as promedio_minimo,
                       ROUND(MAX(a.promedio_general), 2) as promedio_maximo
                FROM carreras c
                JOIN alumnos a ON c.id = a.carrera_id
                WHERE a.estado_alumno = 'activo' AND a.promedio_general > 0
                GROUP BY c.id, c.nombre
                ORDER BY promedio_carrera DESC
            """
        
        return {
            'query_type': 'single',
            'query': query.strip(),
            'description': 'Consulta de promedios por carrera'
        }
    
    def _generate_search_query(self, entities: Dict[str, Any], search_terms: List[str]) -> Dict[str, Any]:
        """Generar consulta de búsqueda específica"""
        
        if not search_terms:
            return self._generate_fallback_query()
        
        # Búsqueda combinada en estudiantes y profesores
        search_conditions = []
        for term in search_terms:
            search_conditions.extend([
                f"u.nombre LIKE '%{term}%'",
                f"u.apellido LIKE '%{term}%'",
                f"a.matricula LIKE '%{term}%'" if 'a.matricula' in search_conditions else f"'{term}' LIKE '%{term}%'"
            ])
        
        search_clause = ' OR '.join(search_conditions[:6])  # Limitar condiciones
        
        query = f"""
            SELECT 'estudiante' as tipo,
                   a.matricula as identificador,
                   u.nombre,
                   u.apellido,
                   c.nombre as carrera,
                   a.promedio_general as dato_adicional
            FROM alumnos a
            JOIN usuarios u ON a.usuario_id = u.id
            JOIN carreras c ON a.carrera_id = c.id
            WHERE a.estado_alumno = 'activo' AND ({search_clause})
            
            UNION ALL
            
            SELECT 'profesor' as tipo,
                   p.numero_empleado as identificador,
                   u.nombre,
                   u.apellido,
                   c.nombre as carrera,
                   p.experiencia_años as dato_adicional
            FROM profesores p
            JOIN usuarios u ON p.usuario_id = u.id
            JOIN carreras c ON p.carrera_id = c.id
            WHERE p.activo = TRUE AND ({search_clause.replace('a.matricula', 'p.numero_empleado')})
            
            ORDER BY tipo, apellido
            LIMIT 20
        """
        
        return {
            'query_type': 'single',
            'query': query.strip(),
            'description': 'Búsqueda específica'
        }
    
    def _generate_general_query(self, search_terms: List[str]) -> Dict[str, Any]:
        """Generar consulta general cuando no se identifica intención específica"""
        
        if search_terms:
            return self._generate_search_query({}, search_terms)
        else:
            return self._generate_stats_queries()
    
    def _generate_fallback_query(self) -> Dict[str, Any]:
        """Consulta de respaldo cuando no se puede generar una específica"""
        return {
            'query_type': 'single',
            'query': "SELECT 'No se pudo procesar la consulta' as mensaje",
            'description': 'Consulta de respaldo'
        }
    
    def optimize_query(self, query: str) -> str:
        """Optimizar consulta SQL"""
        
        # Agregar DISTINCT si hay JOINs múltiples
        if query.count('JOIN') > 2 and 'DISTINCT' not in query.upper():
            query = query.replace('SELECT ', 'SELECT DISTINCT ', 1)
        
        # Asegurar LIMIT para evitar consultas muy grandes
        if 'LIMIT' not in query.upper():
            query += ' LIMIT 100'
        
        return query
    
    def validate_query(self, query: str) -> bool:
        """Validar completamente que la consulta sea segura"""
        
        # Palabras prohibidas
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE',
            'INSERT', 'UPDATE', 'EXEC', 'EXECUTE', 'CALL', 'DECLARE', 'UNION',
            'INTO OUTFILE', 'LOAD_FILE', 'DUMPFILE', 'SLEEP', 'BENCHMARK'
        ]
        
        query_upper = query.upper()
        
        # Verificar palabras peligrosas
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Consulta rechazada por palabra peligrosa: {keyword}")
                return False
        
        # Debe empezar con SELECT
        if not query_upper.strip().startswith('SELECT'):
            logger.warning("Consulta rechazada: no empieza con SELECT")
            return False
        
        # No debe tener comentarios SQL
        if '--' in query or '/*' in query or '*/' in query:
            logger.warning("Consulta rechazada: contiene comentarios")
            return False
        
        # No debe tener subconsultas anidadas complejas
        if query_upper.count('SELECT') > 3:
            logger.warning("Consulta rechazada: demasiadas subconsultas")
            return False
        
        # Verificar longitud máxima
        if len(query) > 2000:
            logger.warning("Consulta rechazada: demasiado larga")
            return False
        
        return True
        
        """Validar que la consulta sea segura"""
        
        # Palabras prohibidas
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE',
            'INSERT', 'UPDATE', 'EXEC', 'EXECUTE', 'CALL', 'DECLARE'
        ]
        
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        
        # Debe empezar con SELECT
        if not query_upper.strip().startswith('SELECT'):
            return False
        
        return True