import re
import logging
from datetime import datetime, timedelta
import pandas as pd
from .query_generator import QueryGenerator
from .response_formatter import ResponseFormatter
from utils.text_processor import TextProcessor
from utils.intent_classifier import IntentClassifier

logger = logging.getLogger(__name__)

class ConversationAI:
    def __init__(self, db_connection):
        self.db = db_connection
        self.query_generator = QueryGenerator(db_connection)
        self.response_formatter = ResponseFormatter()
        self.text_processor = TextProcessor()
        self.intent_classifier = IntentClassifier()
        
        self.conversation_history = []
        self.context = {}
        
    def initialize(self):
        """Inicializar todos los componentes de la IA"""
        logger.info("Inicializando IA conversacional...")
        
        # Inicializar clasificador de intenciones
        self.intent_classifier.initialize()
        
        # Cargar esquema de la base de datos
        self.query_generator.load_database_schema()
        
        logger.info("IA inicializada correctamente")
    
    def process_message(self, message, user_role='alumno', user_id=None):
        """Procesar mensaje del usuario y generar respuesta"""
        try:
            timestamp = datetime.now()
            
            # 1. Procesar texto del usuario
            processed_text = self.text_processor.process(message)
            
            # 2. Clasificar intención
            intent = self.intent_classifier.classify(processed_text, user_role)
            
            # 3. Extraer entidades
            entities = self.text_processor.extract_entities(processed_text)
            
            # 4. Generar consulta SQL
            query_info = self.query_generator.generate_query(
                intent=intent,
                entities=entities,
                user_role=user_role,
                user_id=user_id,
                context=self.context
            )
            
            # 5. Ejecutar consulta
            data = None
            if query_info['query']:
                try:
                    data = self.db.execute_query(
                        query_info['query'], 
                        query_info['params']
                    )
                except Exception as e:
                    logger.error(f"Error ejecutando query: {e}")
                    data = None
            
            # 6. Formatear respuesta
            response = self.response_formatter.format_response(
                intent=intent,
                data=data,
                query_info=query_info,
                user_role=user_role,
                original_message=message
            )
            
            # 7. Actualizar contexto y historial
            self._update_context(intent, entities, data)
            self._add_to_history(message, response, user_role, timestamp)
            
            return {
                'text': response['text'],
                'data': data,
                'query': query_info['query'] if query_info['query'] else None,
                'recommendations': response.get('recommendations', []),
                'intent': intent,
                'entities': entities,
                'timestamp': timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return {
                'text': "Lo siento, hubo un error procesando tu mensaje. ¿Puedes intentar reformularlo?",
                'data': None,
                'query': None,
                'recommendations': [],
                'timestamp': datetime.now().isoformat()
            }
    
    def get_suggestions(self, user_role):
        """Obtener sugerencias de preguntas según el rol"""
        suggestions = {
            'alumno': [
                "¿Cuáles son mis calificaciones actuales?",
                "¿Tengo alguna materia en riesgo?",
                "¿Cuándo son mis próximas clases?",
                "¿Hay noticias importantes para mí?",
                "¿Cómo puedo solicitar ayuda académica?"
            ],
            'profesor': [
                "¿Qué alumnos de mis grupos están en riesgo?",
                "¿Cuál es el promedio de calificaciones de mis materias?",
                "¿Hay reportes pendientes por revisar?",
                "¿Qué alumnos necesitan tutoría?",
                "¿Cuántos alumnos tengo por grupo?"
            ],
            'directivo': [
                "¿Cuál es el índice de deserción por carrera?",
                "¿Qué materias tienen más reprobados?",
                "¿Cuántos reportes de riesgo hay pendientes?",
                "Dame un análisis de rendimiento académico",
                "¿Cuáles son las principales problemáticas reportadas?"
            ]
        }
        
        return suggestions.get(user_role, suggestions['alumno'])
    
    def get_system_analytics(self):
        """Obtener analytics básicos del sistema"""
        try:
            analytics = {}
            
            # Total de usuarios por rol
            query = """
            SELECT rol, COUNT(*) as total
            FROM usuarios
            WHERE activo = TRUE
            GROUP BY rol
            """
            users_by_role = self.db.execute_query(query)
            analytics['users_by_role'] = {row['rol']: row['total'] for row in users_by_role}
            
            # Alumnos por estado
            query = """
            SELECT estado_alumno, COUNT(*) as total
            FROM alumnos
            GROUP BY estado_alumno
            """
            students_by_status = self.db.execute_query(query)
            analytics['students_by_status'] = {row['estado_alumno']: row['total'] for row in students_by_status}
            
            # Reportes de riesgo por tipo
            query = """
            SELECT tipo_riesgo, nivel_riesgo, COUNT(*) as total
            FROM reportes_riesgo
            WHERE estado IN ('abierto', 'en_proceso')
            GROUP BY tipo_riesgo, nivel_riesgo
            """
            risk_reports = self.db.execute_query(query)
            analytics['risk_reports'] = risk_reports
            
            # Carreras activas
            query = """
            SELECT COUNT(*) as total
            FROM carreras
            WHERE activa = TRUE
            """
            active_careers = self.db.execute_query(query, fetch_all=False)
            analytics['active_careers'] = active_careers['total']
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error obteniendo analytics: {e}")
            return {}
    
    def _update_context(self, intent, entities, data):
        """Actualizar contexto de la conversación"""
        self.context['last_intent'] = intent
        self.context['last_entities'] = entities
        
        if data:
            self.context['last_data_type'] = type(data).__name__
            self.context['last_data_count'] = len(data) if isinstance(data, list) else 1
    
    def _add_to_history(self, message, response, user_role, timestamp):
        """Agregar intercambio al historial"""
        self.conversation_history.append({
            'user_message': message,
            'ai_response': response['text'],
            'user_role': user_role,
            'timestamp': timestamp,
            'intent': response.get('intent')
        })
        
        # Mantener solo los últimos 10 intercambios
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_conversation_context(self):
        """Obtener contexto actual de la conversación"""
        return {
            'history_count': len(self.conversation_history),
            'last_messages': self.conversation_history[-3:] if self.conversation_history else [],
            'current_context': self.context
        }
    
    def clear_context(self):
        """Limpiar contexto de la conversación"""
        self.conversation_history.clear()
        self.context.clear()
        logger.info("Contexto de conversación limpiado")