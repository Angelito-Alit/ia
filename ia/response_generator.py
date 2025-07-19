"""
Generador de Respuestas Conversacionales Inteligentes
Convierte datos SQL en respuestas naturales con recomendaciones
"""

import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generador de respuestas conversacionales con IA"""
    
    def __init__(self):
        self.response_templates = self._load_response_templates()
        self.recommendation_rules = self._load_recommendation_rules()
        
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Templates de respuestas por tipo de consulta"""
        return {
            'estadisticas_generales': [
                "📊 **Estadísticas Generales de DTAI:**\n\n{stats}\n\n{analysis}",
                "🎯 **Resumen del Sistema Académico:**\n\n{stats}\n\n{analysis}",
                "📈 **Dashboard Académico Actual:**\n\n{stats}\n\n{analysis}"
            ],
            
            'consulta_alumnos': [
                "👨‍🎓 **Información de Estudiantes:**\n\n{data}\n\n{summary}",
                "📚 **Base de Datos Estudiantil:**\n\n{data}\n\n{summary}",
                "🎓 **Registro Académico:**\n\n{data}\n\n{summary}"
            ],
            
            'consulta_profesores': [
                "👨‍🏫 **Cuerpo Docente:**\n\n{data}\n\n{summary}",
                "🏛️ **Personal Académico:**\n\n{data}\n\n{summary}",
                "📝 **Directorio de Profesores:**\n\n{data}\n\n{summary}"
            ],
            
            'alumnos_riesgo': [
                "⚠️ **Estudiantes que Requieren Atención:**\n\n{data}\n\n{recommendations}",
                "🚨 **Alerta Académica:**\n\n{data}\n\n{recommendations}",
                "📋 **Reporte de Riesgo Estudiantil:**\n\n{data}\n\n{recommendations}"
            ],
            
            'calificaciones_promedio': [
                "📊 **Análisis de Rendimiento Académico:**\n\n{data}\n\n{insights}",
                "🎯 **Evaluación del Desempeño:**\n\n{data}\n\n{insights}",
                "📈 **Métricas Académicas:**\n\n{data}\n\n{insights}"
            ],
            
            'busqueda_especifica': [
                "🔍 **Resultados de Búsqueda:**\n\n{data}\n\n{context}",
                "📋 **Información Encontrada:**\n\n{data}\n\n{context}",
                "✅ **Datos Específicos:**\n\n{data}\n\n{context}"
            ],
            
            'general': [
                "💡 **Información Solicitada:**\n\n{data}\n\n{additional_info}",
                "📌 **Respuesta del Sistema:**\n\n{data}\n\n{additional_info}",
                "🤖 **Análisis de Datos:**\n\n{data}\n\n{additional_info}"
            ],
            
            'error': [
                "❌ **Lo siento, hubo un problema procesando tu consulta.**\n\nPuedes intentar preguntarme sobre:\n• Estadísticas generales\n• Información de estudiantes\n• Datos de profesores\n• Alumnos en riesgo académico",
                "🔧 **No pude procesar esa consulta específica.**\n\nTe recomiendo preguntar:\n• ¿Cuántos estudiantes hay?\n• ¿Qué profesores están activos?\n• ¿Hay alumnos en riesgo?\n• Estadísticas por carrera"
            ]
        }
    
    def _load_recommendation_rules(self) -> Dict[str, Dict]:
        """Reglas para generar recomendaciones inteligentes"""
        return {
            'promedio_bajo': {
                'threshold': 7.0,
                'message': "🎯 **Recomendación:** {count} estudiantes tienen promedio menor a 7.0 y podrían beneficiarse de tutoría académica.",
                'action': "Programar sesiones de apoyo académico"
            },
            
            'riesgo_alto': {
                'levels': ['alto', 'critico'],
                'message': "🚨 **Acción Urgente:** {count} estudiantes en riesgo {level} requieren intervención inmediata.",
                'action': "Contactar a estudiantes y sus tutores"
            },
            
            'carrera_baja_matricula': {
                'threshold': 20,
                'message': "📈 **Oportunidad:** La carrera de {carrera} tiene baja matrícula ({count} estudiantes). Considerar estrategias de promoción.",
                'action': "Revisar plan de marketing académico"
            },
            
            'profesor_experiencia': {
                'threshold': 10,
                'message': "🌟 **Recurso Valioso:** {count} profesores con más de 10 años de experiencia pueden ser mentores.",
                'action': "Crear programa de mentoría docente"
            }
        }
    
    def generate_response(self, intent: str, query_result: Dict[str, Any], entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generar respuesta conversacional completa"""
        
        try:
            if intent == 'estadisticas_generales':
                return self._generate_stats_response(query_result)
            
            elif intent == 'consulta_alumnos':
                return self._generate_students_response(query_result, entities)
            
            elif intent == 'consulta_profesores':
                return self._generate_teachers_response(query_result, entities)
            
            elif intent == 'alumnos_riesgo':
                return self._generate_risk_response(query_result, entities)
            
            elif intent == 'calificaciones_promedio':
                return self._generate_grades_response(query_result, entities)
            
            elif intent == 'busqueda_especifica':
                return self._generate_search_response(query_result, entities)
            
            else:
                return self._generate_general_response(query_result, intent)
                
        except Exception as e:
            logger.error(f"Error generando respuesta para intent '{intent}': {e}")
            return self._generate_error_response()
    
    def _generate_stats_response(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generar respuesta para estadísticas generales"""
        
        if query_result.get('query_type') == 'multiple':
            queries = query_result.get('queries', {})
            stats_data = {}
            
            # Simular ejecución de múltiples consultas (en la implementación real vendrá de la BD)
            stats_text = []
            
            stats_text.append("• **Total de Estudiantes Activos:** Los datos se están calculando...")
            stats_text.append("• **Profesores Activos:** Información en proceso...")
            stats_text.append("• **Carreras Disponibles:** Consultando base de datos...")
            stats_text.append("• **Promedio General:** Calculando métricas...")
            
            stats_formatted = "\n".join(stats_text)
            
            # Análisis inteligente
            analysis = self._generate_stats_analysis({
                'total_alumnos': 234,  # Valores ejemplo para el template
                'total_profesores': 45,
                'total_carreras': 6,
                'promedio_general': 8.3
            })
            
            template = random.choice(self.response_templates['estadisticas_generales'])
            response_text = template.format(
                stats=stats_formatted,
                analysis=analysis['text']
            )
            
            return {
                'respuesta': response_text,
                'datos_contexto': {
                    'tipo_consulta': 'estadisticas_generales',
                    'timestamp': datetime.now().isoformat()
                },
                'recomendaciones': analysis['recommendations']
            }
        
        return self._generate_error_response()
    
    def _generate_students_response(self, query_result: Dict[str, Any], entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generar respuesta para consulta de estudiantes"""
        
        # Esta función procesará los resultados reales de la BD
        data_text = "📊 Los datos de estudiantes se están consultando en tiempo real desde la base de datos..."
        
        if entities and entities.get('carreras'):
            carrera = entities['carreras'][0]
            data_text = f"🎓 Consultando estudiantes de la carrera: **{carrera}**\n\nLos resultados aparecerán aquí..."
        
        # Análisis contextual
        summary = "📈 **Análisis:** La consulta se está procesando. Podrás ver información detallada incluyendo matrículas, nombres, carreras, cuatrimestres y promedios."
        
        template = random.choice(self.response_templates['consulta_alumnos'])
        response_text = template.format(
            data=data_text,
            summary=summary
        )
        
        recommendations = [
            "Filtrar por carrera específica para análisis detallado",
            "Revisar estudiantes con promedio menor a 7.0",
            "Identificar alumnos que necesitan tutoría"
        ]
        
        return {
            'respuesta': response_text,
            'datos_contexto': {
                'tipo_consulta': 'estudiantes',
                'filtros_aplicados': entities or {}
            },
            'recomendaciones': recommendations
        }
    
    def _generate_teachers_response(self, query_result: Dict[str, Any], entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generar respuesta para consulta de profesores"""
        
        data_text = "👨‍🏫 Consultando información del cuerpo docente..."
        
        summary = "📋 **Datos Disponibles:** Número de empleado, nombres, carrera asignada, título académico, especialidad y años de experiencia."
        
        template = random.choice(self.response_templates['consulta_profesores'])
        response_text = template.format(
            data=data_text,
            summary=summary
        )
        
        recommendations = [
            "Identificar profesores con mayor experiencia para mentoría",
            "Revisar distribución de docentes por carrera",
            "Analizar especialidades disponibles"
        ]
        
        return {
            'respuesta': response_text,
            'datos_contexto': {
                'tipo_consulta': 'profesores',
                'filtros': entities or {}
            },
            'recomendaciones': recommendations
        }
    
    def _generate_risk_response(self, query_result: Dict[str, Any], entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generar respuesta para estudiantes en riesgo"""
        
        data_text = "⚠️ **Estudiantes en Situación de Riesgo Académico:**\n\nConsultando reportes activos y casos abiertos..."
        
        recommendations = [
            "🎯 Programar sesiones de tutoría inmediata",
            "📞 Contactar a estudiantes y padres de familia",
            "📋 Crear plan de seguimiento personalizado",
            "🤝 Asignar mentor académico especializado"
        ]
        
        template = random.choice(self.response_templates['alumnos_riesgo'])
        response_text = template.format(
            data=data_text,
            recommendations="\n".join([f"• {rec}" for rec in recommendations])
        )
        
        return {
            'respuesta': response_text,
            'datos_contexto': {
                'tipo_consulta': 'riesgo_academico',
                'urgencia': 'alta'
            },
            'recomendaciones': recommendations
        }
    
    def _generate_grades_response(self, query_result: Dict[str, Any], entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generar respuesta para calificaciones y promedios"""
        
        data_text = "📊 **Análisis de Promedios por Carrera:**\n\nCalculando métricas de rendimiento académico..."
        
        insights = "💡 **Insights:** Los datos incluyen promedio por carrera, mínimos, máximos y número total de estudiantes evaluados."
        
        template = random.choice(self.response_templates['calificaciones_promedio'])
        response_text = template.format(
            data=data_text,
            insights=insights
        )
        
        recommendations = [
            "Identificar carreras con mejor rendimiento",
            "Implementar mejores prácticas en carreras con menor promedio",
            "Reconocer estudiantes destacados",
            "Crear programas de apoyo académico focalizados"
        ]
        
        return {
            'respuesta': response_text,
            'datos_contexto': {
                'tipo_consulta': 'calificaciones',
                'nivel_analisis': 'carrera'
            },
            'recomendaciones': recommendations
        }
    
    def _generate_search_response(self, query_result: Dict[str, Any], entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generar respuesta para búsqueda específica"""
        
        data_text = "🔍 **Búsqueda en Base de Datos:**\n\nBuscando coincidencias en registros de estudiantes y profesores..."
        
        context = "ℹ️ **Contexto:** La búsqueda incluye nombres, apellidos, matrículas y números de empleado."
        
        template = random.choice(self.response_templates['busqueda_especifica'])
        response_text = template.format(
            data=data_text,
            context=context
        )
        
        return {
            'respuesta': response_text,
            'datos_contexto': {
                'tipo_consulta': 'busqueda',
                'terminos_busqueda': entities.get('nombres', [])
            },
            'recomendaciones': [
                "Refinar búsqueda con términos más específicos",
                "Buscar por matrícula para resultados exactos"
            ]
        }
    
    def _generate_general_response(self, query_result: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """Generar respuesta general"""
        
        data_text = "🤖 Procesando tu consulta..."
        additional_info = "💡 Para mejores resultados, puedes preguntar sobre estadísticas, estudiantes, profesores o situaciones de riesgo académico."
        
        template = random.choice(self.response_templates['general'])
        response_text = template.format(
            data=data_text,
            additional_info=additional_info
        )
        
        return {
            'respuesta': response_text,
            'datos_contexto': {'tipo_consulta': 'general'},
            'recomendaciones': [
                "Pregunta sobre estadísticas generales",
                "Consulta información de estudiantes por carrera",
                "Revisa el estado de profesores activos"
            ]
        }
    
    def _generate_error_response(self) -> Dict[str, Any]:
        """Generar respuesta de error"""
        
        template = random.choice(self.response_templates['error'])
        
        return {
            'respuesta': template,
            'datos_contexto': {'tipo_consulta': 'error'},
            'recomendaciones': [
                "Reformula tu pregunta de manera más específica",
                "Pregunta sobre temas académicos específicos",
                "Usa palabras clave como 'estudiantes', 'profesores', 'carreras'"
            ]
        }
    
    def _generate_stats_analysis(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generar análisis inteligente de estadísticas"""
        
        analysis_parts = []
        recommendations = []
        
        # Análisis de estudiantes
        total_estudiantes = stats.get('total_alumnos', 0)
        if total_estudiantes > 200:
            analysis_parts.append(f"✅ **Matrícula Saludable:** {total_estudiantes} estudiantes activos indican una institución en crecimiento.")
            recommendations.append("Mantener programas de retención estudiantil")
        elif total_estudiantes < 100:
            analysis_parts.append(f"📈 **Oportunidad de Crecimiento:** Con {total_estudiantes} estudiantes, hay potencial para aumentar matrícula.")
            recommendations.append("Implementar estrategias de captación")
        
        # Análisis de promedio
        promedio = stats.get('promedio_general', 0)
        if promedio >= 8.5:
            analysis_parts.append(f"🌟 **Excelencia Académica:** Promedio general de {promedio} demuestra alto nivel académico.")
        elif promedio >= 7.5:
            analysis_parts.append(f"👍 **Buen Rendimiento:** Promedio de {promedio} es satisfactorio con margen de mejora.")
            recommendations.append("Implementar programas de apoyo académico")
        else:
            analysis_parts.append(f"⚠️ **Área de Mejora:** Promedio de {promedio} requiere atención especial.")
            recommendations.append("Revisar metodologías de enseñanza")
        
        return {
            'text': "\n\n".join(analysis_parts),
            'recommendations': recommendations
        }
    
    def format_data_table(self, data: List[Dict[str, Any]], max_rows: int = 10) -> str:
        """Formatear datos en tabla legible"""
        
        if not data:
            return "📭 No se encontraron resultados."
        
        # Mostrar solo primeras filas
        display_data = data[:max_rows]
        
        formatted_rows = []
        for i, row in enumerate(display_data, 1):
            row_text = f"**{i}.** "
            row_parts = []
            
            for key, value in row.items():
                if key.lower() in ['nombre', 'apellido', 'carrera', 'matricula']:
                    row_parts.append(f"{key.title()}: {value}")
            
            row_text += " | ".join(row_parts)
            formatted_rows.append(row_text)
        
        result = "\n".join(formatted_rows)
        
        if len(data) > max_rows:
            result += f"\n\n*... y {len(data) - max_rows} resultados más.*"
        
        return result