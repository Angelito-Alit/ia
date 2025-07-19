"""
ChatBot IA Principal - Cerebro del Sistema
Coordina NLP, SQL Generator y Response Generator
"""

from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime

# Imports locales
from .nlp_processor import NLPProcessor
from .sql_generator import SQLGenerator  
from .response_generator import ResponseGenerator
from core.database import DatabaseManager

logger = logging.getLogger(__name__)

class ChatBotAI:
    """Sistema de IA Conversacional para DTAI"""
    
    def __init__(self):
        """Inicializar componentes de la IA"""
        self.nlp_processor = NLPProcessor()
        self.sql_generator = SQLGenerator()
        self.response_generator = ResponseGenerator()
        self.db_manager = DatabaseManager()
        self.conversation_memory = {}
        
        logger.info("ChatBot IA inicializado exitosamente")
    
    async def procesar_mensaje(self, mensaje: str, conversacion_id: int, usuario_id: int) -> Dict[str, Any]:
        """
        Proceso principal de la IA:
        1. Analizar mensaje con NLP
        2. Generar consulta SQL
        3. Ejecutar consulta en BD
        4. Generar respuesta conversacional
        5. Guardar en memoria conversacional
        """
        
        try:
            logger.info(f"Procesando mensaje: '{mensaje}' para conversación {conversacion_id}")
            
            # PASO 1: Análisis NLP del mensaje
            analisis_nlp = self.nlp_processor.analyze_message(mensaje)
            
            logger.info(f"Intent detectado: {analisis_nlp['intent']} (confianza: {analisis_nlp['confidence']:.2f})")
            
            # PASO 2: Generar consulta SQL basada en la intención
            sql_info = self.sql_generator.generate_query(
                intent=analisis_nlp['intent'],
                entities=analisis_nlp['entities'],
                search_terms=analisis_nlp['search_terms']
            )
            
            # PASO 3: Ejecutar consulta(s) en la base de datos
            datos_resultado = await self._ejecutar_consultas(sql_info)
            
            # PASO 4: Generar respuesta conversacional
            respuesta_ia = self.response_generator.generate_response(
                intent=analisis_nlp['intent'],
                query_result=datos_resultado,
                entities=analisis_nlp['entities']
            )
            
            # PASO 5: Actualizar memoria conversacional
            self._actualizar_memoria_conversacional(
                conversacion_id=conversacion_id,
                mensaje=mensaje,
                analisis=analisis_nlp,
                respuesta=respuesta_ia
            )
            
            # PASO 6: Personalizar respuesta basada en contexto
            respuesta_final = await self._personalizar_respuesta(
                respuesta=respuesta_ia,
                conversacion_id=conversacion_id,
                datos=datos_resultado
            )
            
            logger.info(f"Respuesta generada exitosamente para conversación {conversacion_id}")
            
            return respuesta_final
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return self._generar_respuesta_error()
    
    async def _ejecutar_consultas(self, sql_info: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar consultas SQL en la base de datos"""
        
        try:
            if sql_info['query_type'] == 'multiple':
                # Múltiples consultas (ej: estadísticas generales)
                resultados = {}
                
                for key, query in sql_info.get('queries', {}).items():
                    if self.sql_generator.validate_query(query):
                        optimized_query = self.sql_generator.optimize_query(query)
                        result = await self.db_manager.ejecutar_consulta(optimized_query)
                        resultados[key] = result
                    else:
                        logger.warning(f"Consulta invalidada por seguridad: {query}")
                        resultados[key] = []
                
                return {
                    'query_type': 'multiple',
                    'data': resultados,
                    'total_queries': len(resultados)
                }
                
            elif sql_info['query_type'] == 'single':
                # Consulta única
                query = sql_info.get('query', '')
                
                if self.sql_generator.validate_query(query):
                    optimized_query = self.sql_generator.optimize_query(query)
                    result = await self.db_manager.ejecutar_consulta(optimized_query)
                    
                    return {
                        'query_type': 'single',
                        'data': result,
                        'total_rows': len(result) if result else 0,
                        'description': sql_info.get('description', 'Consulta ejecutada')
                    }
                else:
                    logger.warning(f"Consulta invalidada por seguridad: {query}")
                    return {'query_type': 'error', 'data': [], 'error': 'Consulta no válida'}
                    
            else:
                return {'query_type': 'error', 'data': [], 'error': 'Tipo de consulta no reconocido'}
                
        except Exception as e:
            logger.error(f"Error ejecutando consultas: {e}")
            return {'query_type': 'error', 'data': [], 'error': str(e)}
    
    async def _personalizar_respuesta(self, respuesta: Dict[str, Any], conversacion_id: int, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Personalizar respuesta con datos reales y análisis"""
        
        respuesta_personalizada = respuesta.copy()
        
        try:
            # Incorporar datos reales en la respuesta
            if datos['query_type'] == 'multiple':
                respuesta_personalizada = await self._integrar_datos_multiples(respuesta, datos)
            elif datos['query_type'] == 'single':
                respuesta_personalizada = await self._integrar_datos_unicos(respuesta, datos)
            
            # Agregar contexto conversacional
            memoria = self.conversation_memory.get(conversacion_id, [])
            if len(memoria) > 1:
                respuesta_personalizada = self._agregar_contexto_conversacional(respuesta_personalizada, memoria)
            
            # Agregar timestamp y metadata
            respuesta_personalizada['datos_contexto']['timestamp'] = datetime.now().isoformat()
            respuesta_personalizada['datos_contexto']['total_datos'] = self._contar_datos(datos)
            
        except Exception as e:
            logger.error(f"Error personalizando respuesta: {e}")
        
        return respuesta_personalizada
    
    async def _integrar_datos_multiples(self, respuesta: Dict[str, Any], datos: Dict[str, Any]) -> Dict[str, Any]:
        """Integrar múltiples consultas en la respuesta"""
        
        respuesta_actualizada = respuesta.copy()
        datos_consultas = datos.get('data', {})
        
        # Construir estadísticas reales
        stats_reales = []
        
        if 'total_alumnos' in datos_consultas and datos_consultas['total_alumnos']:
            total_alumnos = datos_consultas['total_alumnos'][0].get('total', 0)
            stats_reales.append(f"• **{total_alumnos} Estudiantes Activos** 👨‍🎓")
        
        if 'total_profesores' in datos_consultas and datos_consultas['total_profesores']:
            total_profesores = datos_consultas['total_profesores'][0].get('total', 0)
            stats_reales.append(f"• **{total_profesores} Profesores Activos** 👨‍🏫")
        
        if 'total_carreras' in datos_consultas and datos_consultas['total_carreras']:
            total_carreras = datos_consultas['total_carreras'][0].get('total', 0)
            stats_reales.append(f"• **{total_carreras} Carreras Disponibles** 📚")
        
        if 'promedio_general' in datos_consultas and datos_consultas['promedio_general']:
            promedio = datos_consultas['promedio_general'][0].get('promedio', 0)
            if promedio:
                stats_reales.append(f"• **Promedio General: {promedio:.2f}** 📊")
        
        if stats_reales:
            stats_text = "\n".join(stats_reales)
            
            # Generar análisis inteligente
            analisis = self._generar_analisis_inteligente(datos_consultas)
            
            # Actualizar respuesta con datos reales
            respuesta_actualizada['respuesta'] = respuesta_actualizada['respuesta'].replace(
                "Los datos se están calculando...", stats_text
            ).replace(
                "Información en proceso...", analisis
            )
            
            # Actualizar datos de contexto
            respuesta_actualizada['datos_contexto'].update({
                'estadisticas_reales': {
                    'alumnos': datos_consultas.get('total_alumnos', [{}])[0].get('total', 0),
                    'profesores': datos_consultas.get('total_profesores', [{}])[0].get('total', 0),
                    'carreras': datos_consultas.get('total_carreras', [{}])[0].get('total', 0),
                    'promedio': datos_consultas.get('promedio_general', [{}])[0].get('promedio', 0)
                }
            })
        
        return respuesta_actualizada
    
    async def _integrar_datos_unicos(self, respuesta: Dict[str, Any], datos: Dict[str, Any]) -> Dict[str, Any]:
        """Integrar datos de consulta única en la respuesta"""
        
        respuesta_actualizada = respuesta.copy()
        datos_resultado = datos.get('data', [])
        
        if datos_resultado:
            # Formatear datos en tabla legible
            tabla_formateada = self.response_generator.format_data_table(datos_resultado)
            
            # Actualizar respuesta con datos reales
            respuesta_actualizada['respuesta'] = respuesta_actualizada['respuesta'].replace(
                "Los datos de estudiantes se están consultando en tiempo real desde la base de datos...",
                tabla_formateada
            ).replace(
                "Consultando información del cuerpo docente...",
                tabla_formateada
            ).replace(
                "Consultando reportes activos y casos abiertos...",
                tabla_formateada
            )
            
            # Agregar resumen estadístico
            total_filas = len(datos_resultado)
            respuesta_actualizada['datos_contexto']['total_resultados'] = total_filas
            
            # Generar recomendaciones específicas basadas en datos
            recomendaciones_especificas = self._generar_recomendaciones_datos(datos_resultado, datos.get('description', ''))
            if recomendaciones_especificas:
                respuesta_actualizada['recomendaciones'].extend(recomendaciones_especificas)
        else:
            respuesta_actualizada['respuesta'] = respuesta_actualizada['respuesta'].replace(
                "Los datos de estudiantes se están consultando en tiempo real desde la base de datos...",
                "📭 No se encontraron resultados para esta consulta."
            )
        
        return respuesta_actualizada
    
    def _generar_analisis_inteligente(self, datos: Dict[str, Any]) -> str:
        """Generar análisis inteligente de los datos"""
        
        analisis_partes = []
        
        # Análisis de matrícula
        total_alumnos = datos.get('total_alumnos', [{}])[0].get('total', 0)
        total_profesores = datos.get('total_profesores', [{}])[0].get('total', 0)
        
        if total_alumnos and total_profesores:
            ratio = total_alumnos / total_profesores
            if ratio > 20:
                analisis_partes.append(f"⚠️ **Alta carga docente:** {ratio:.1f} estudiantes por profesor.")
            elif ratio < 10:
                analisis_partes.append(f"✅ **Buena ratio profesor-alumno:** {ratio:.1f} estudiantes por profesor.")
            else:
                analisis_partes.append(f"👍 **Ratio equilibrada:** {ratio:.1f} estudiantes por profesor.")
        
        # Análisis de promedio
        promedio = datos.get('promedio_general', [{}])[0].get('promedio', 0)
        if promedio:
            if promedio >= 8.5:
                analisis_partes.append("🌟 **Excelente rendimiento académico general.**")
            elif promedio >= 7.5:
                analisis_partes.append("👍 **Buen rendimiento académico con oportunidades de mejora.**")
            else:
                analisis_partes.append("📈 **Oportunidad de implementar programas de apoyo académico.**")
        
        return " ".join(analisis_partes) if analisis_partes else "📊 **Sistema funcionando normalmente.**"
    
    def _generar_recomendaciones_datos(self, datos: List[Dict], descripcion: str) -> List[str]:
        """Generar recomendaciones específicas basadas en los datos"""
        
        recomendaciones = []
        
        if 'estudiantes' in descripcion.lower() or 'alumnos' in descripcion.lower():
            # Analizar datos de estudiantes
            if len(datos) > 30:
                recomendaciones.append("Considerar dividir en grupos más pequeños para mejor seguimiento")
            
            # Buscar promedios bajos
            promedios_bajos = [d for d in datos if d.get('promedio_general', 10) < 7.0]
            if promedios_bajos:
                recomendaciones.append(f"Revisar {len(promedios_bajos)} estudiantes con promedio menor a 7.0")
        
        elif 'riesgo' in descripcion.lower():
            # Analizar reportes de riesgo
            if len(datos) > 10:
                recomendaciones.append("Alta cantidad de reportes - implementar intervención masiva")
            
            niveles_criticos = [d for d in datos if d.get('nivel_riesgo') in ['alto', 'critico']]
            if niveles_criticos:
                recomendaciones.append(f"Atención URGENTE: {len(niveles_criticos)} casos críticos")
        
        return recomendaciones
    
    def _actualizar_memoria_conversacional(self, conversacion_id: int, mensaje: str, analisis: Dict, respuesta: Dict):
        """Actualizar memoria conversacional para contexto"""
        
        if conversacion_id not in self.conversation_memory:
            self.conversation_memory[conversacion_id] = []
        
        entrada_memoria = {
            'timestamp': datetime.now().isoformat(),
            'mensaje_usuario': mensaje,
            'intent_detectado': analisis['intent'],
            'entidades': analisis['entities'],
            'respuesta_generada': respuesta['respuesta'][:100] + "..." if len(respuesta['respuesta']) > 100 else respuesta['respuesta']
        }
        
        self.conversation_memory[conversacion_id].append(entrada_memoria)
        
        # Mantener solo últimas 10 interacciones
        if len(self.conversation_memory[conversacion_id]) > 10:
            self.conversation_memory[conversacion_id] = self.conversation_memory[conversacion_id][-10:]
    
    def _agregar_contexto_conversacional(self, respuesta: Dict[str, Any], memoria: List[Dict]) -> Dict[str, Any]:
        """Agregar contexto de conversaciones anteriores"""
        
        if len(memoria) > 1:
            ultimo_intent = memoria[-2]['intent_detectado']
            
            # Agregar referencia contextual
            if ultimo_intent == respuesta['datos_contexto'].get('tipo_consulta'):
                respuesta['respuesta'] = "🔄 **Continuando con el análisis anterior...**\n\n" + respuesta['respuesta']
            
            # Sugerir consultas relacionadas
            if ultimo_intent == 'consulta_alumnos' and 'riesgo' not in respuesta['respuesta'].lower():
                respuesta['recomendaciones'].append("¿Te gustaría revisar si alguno de estos estudiantes está en riesgo?")
        
        return respuesta
    
    def _contar_datos(self, datos: Dict[str, Any]) -> int:
        """Contar total de datos procesados"""
        
        if datos['query_type'] == 'multiple':
            return sum(len(v) if isinstance(v, list) else 1 for v in datos.get('data', {}).values())
        elif datos['query_type'] == 'single':
            return len(datos.get('data', []))
        else:
            return 0
    
    def _generar_respuesta_error(self) -> Dict[str, Any]:
        """Generar respuesta de error del sistema"""
        
        return {
            'respuesta': "❌ **Lo siento, hubo un problema procesando tu consulta.**\n\nPor favor intenta de nuevo o pregúntame sobre:\n• Estadísticas generales del sistema\n• Información de estudiantes por carrera\n• Estado de profesores activos\n• Alumnos en riesgo académico",
            'datos_contexto': {
                'tipo_consulta': 'error_sistema',
                'timestamp': datetime.now().isoformat()
            },
            'recomendaciones': [
                "Reformular la pregunta de manera más específica",
                "Usar palabras clave como 'estudiantes', 'profesores', 'carreras'",
                "Preguntar sobre estadísticas o datos específicos"
            ]
        }
    
    async def obtener_sugerencias_contextuales(self, conversacion_id: int) -> List[str]:
        """Obtener sugerencias basadas en el contexto de la conversación"""
        
        memoria = self.conversation_memory.get(conversacion_id, [])
        
        if not memoria:
            return [
                "¿Cuántos estudiantes hay en total?",
                "Muéstrame las estadísticas generales",
                "¿Qué profesores están activos?",
                "¿Hay alumnos en riesgo académico?"
            ]
        
        ultimo_intent = memoria[-1]['intent_detectado']
        
        sugerencias_contextuales = {
            'estadisticas_generales': [
                "¿Puedes mostrarme los estudiantes de ISC?",
                "¿Qué profesores tenemos activos?",
                "¿Hay alumnos en riesgo?"
            ],
            'consulta_alumnos': [
                "¿Algunos de estos estudiantes están en riesgo?",
                "¿Cuál es el promedio por carrera?",
                "¿Quiénes son sus profesores?"
            ],
            'alumnos_riesgo': [
                "¿Qué profesores pueden ayudar con tutoría?",
                "¿Cuáles son las carreras más afectadas?",
                "¿Cómo está el rendimiento general?"
            ]
        }
        
        return sugerencias_contextuales.get(ultimo_intent, [
            "¿Qué más te gustaría saber?",
            "¿Necesitas otro tipo de análisis?",
            "¿Quieres información de alguna carrera específica?"
        ])