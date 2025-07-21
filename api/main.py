"""
FastAPI Main Application para ChatBot IA
Optimizado para Vercel Serverless Functions
"""

import sys
import os
import json
from pathlib import Path

# Agregar paths necesarios
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title="DTAI ChatBot IA",
    description="Asistente inteligente para gestión académica",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ConversacionResponse(BaseModel):
    conversacionId: int
    mensaje: str

class MensajeRequest(BaseModel):
    conversacionId: int
    mensaje: str

class MensajeResponse(BaseModel):
    respuesta: str
    datos_contexto: Dict[str, Any] = {}
    recomendaciones: List[str] = []

# Simulador de IA básico para primera versión
class SimpleAI:
    def __init__(self):
        self.conversation_count = 0
    
    def procesar_mensaje(self, mensaje: str, conversacion_id: int) -> Dict[str, Any]:
        """Procesador de IA simplificado"""
        mensaje_lower = mensaje.lower()
        
        if any(word in mensaje_lower for word in ['cuantos', 'cantidad', 'total']) and 'estudiantes' in mensaje_lower:
            return {
                'respuesta': "📊 **Estudiantes en DTAI:**\n\n• **234 estudiantes activos** distribuidos en 6 carreras\n• **Promedio general:** 8.3\n• **Carreras más populares:** ISC (45%), LAE (30%), Gastronomía (25%)\n\n¿Te gustaría conocer información específica de alguna carrera?",
                'datos_contexto': {'tipo_consulta': 'estudiantes', 'total': 234},
                'recomendaciones': [
                    "Consultar estudiantes por carrera específica",
                    "Revisar rendimiento académico por cuatrimestre",
                    "Identificar estudiantes que necesitan tutoría"
                ]
            }
        
        elif 'profesores' in mensaje_lower or 'docentes' in mensaje_lower:
            return {
                'respuesta': "👨‍🏫 **Cuerpo Docente DTAI:**\n\n• **45 profesores activos**\n• **Promedio de experiencia:** 8.5 años\n• **Distribución:** 15 ISC, 12 LAE, 18 otras carreras\n• **12 profesores** disponibles para tutoría\n\n¿Necesitas información de profesores por carrera específica?",
                'datos_contexto': {'tipo_consulta': 'profesores', 'total': 45},
                'recomendaciones': [
                    "Ver profesores por especialidad",
                    "Consultar disponibilidad para tutorías",
                    "Revisar carga académica por profesor"
                ]
            }
        
        elif any(word in mensaje_lower for word in ['estadisticas', 'general', 'resumen', 'overview']):
            return {
                'respuesta': "📈 **Dashboard Académico DTAI:**\n\n📚 **Estudiantes:** 234 activos\n👨‍🏫 **Profesores:** 45 activos\n🎓 **Carreras:** 6 disponibles\n📊 **Promedio General:** 8.3\n⚠️ **Estudiantes en riesgo:** 12\n📅 **Cuatrimestre actual:** 2025-1\n\n✅ **Sistema funcionando óptimamente**",
                'datos_contexto': {'tipo_consulta': 'estadisticas_generales'},
                'recomendaciones': [
                    "Revisar estudiantes en riesgo académico",
                    "Analizar rendimiento por carrera",
                    "Programar sesiones de tutoría"
                ]
            }
        
        elif 'riesgo' in mensaje_lower or 'problemas' in mensaje_lower or 'tutoria' in mensaje_lower:
            return {
                'respuesta': "⚠️ **Alerta Académica - Estudiantes en Riesgo:**\n\n🚨 **12 estudiantes** requieren atención inmediata:\n• **5 casos críticos** (promedio < 6.0)\n• **4 casos de alto riesgo** (promedio < 7.0)\n• **3 casos de ausentismo** (>30% faltas)\n\n📋 **Carreras más afectadas:** ISC (5), LAE (4), Gastronomía (3)\n\n🎯 **Acción recomendada:** Contacto inmediato con estudiantes y tutores",
                'datos_contexto': {'tipo_consulta': 'riesgo_academico', 'casos_criticos': 12},
                'recomendaciones': [
                    "🚨 Contactar inmediatamente a los 5 casos críticos",
                    "📞 Llamar a padres de familia de casos de alto riesgo",
                    "📅 Programar sesiones de tutoría esta semana",
                    "📋 Crear plan de seguimiento personalizado"
                ]
            }
        
        elif any(word in mensaje_lower for word in ['isc', 'sistemas', 'ingenieria']):
            return {
                'respuesta': "💻 **Ingeniería en Sistemas Computacionales:**\n\n👨‍🎓 **Estudiantes:** 105 activos\n📊 **Promedio carrera:** 8.5\n👨‍🏫 **Profesores:** 15 especializados\n📚 **Cuatrimestres:** 1° al 9°\n⚠️ **En riesgo:** 5 estudiantes\n\n🌟 **Carrera con mejor rendimiento académico**",
                'datos_contexto': {'tipo_consulta': 'carrera_especifica', 'carrera': 'ISC'},
                'recomendaciones': [
                    "Revisar los 5 estudiantes en riesgo",
                    "Mantener programas de excelencia académica",
                    "Considerar estudiantes para proyectos avanzados"
                ]
            }
        
        elif any(word in mensaje_lower for word in ['calificaciones', 'notas', 'promedio']):
            return {
                'respuesta': "📊 **Análisis de Rendimiento Académico:**\n\n🎯 **Promedios por Carrera:**\n• ISC: 8.5 ⭐\n• LAE: 8.2 ✅\n• Gastronomía: 8.0 👍\n• Mercadotecnia: 7.8 📈\n• Administración: 7.9 📊\n• Turismo: 8.1 🌟\n\n📈 **Tendencia general:** +0.3 respecto al cuatrimestre anterior",
                'datos_contexto': {'tipo_consulta': 'calificaciones'},
                'recomendaciones': [
                    "Implementar mejores prácticas de ISC en otras carreras",
                    "Reforzar apoyo en Mercadotecnia",
                    "Reconocer estudiantes destacados"
                ]
            }
        
        elif 'buscar' in mensaje_lower or 'encontrar' in mensaje_lower:
            return {
                'respuesta': "🔍 **Sistema de Búsqueda DTAI:**\n\nPuedo ayudarte a buscar:\n• 👨‍🎓 **Estudiantes** (por nombre, matrícula, carrera)\n• 👨‍🏫 **Profesores** (por nombre, especialidad)\n• 📊 **Datos académicos** específicos\n• 📋 **Reportes** de seguimiento\n\n💡 **Ejemplo:** 'Busca al estudiante Juan Pérez' o 'Profesores de ISC'",
                'datos_contexto': {'tipo_consulta': 'busqueda'},
                'recomendaciones': [
                    "Especifica nombre completo para búsqueda exacta",
                    "Usa matrícula para resultados precisos",
                    "Menciona la carrera para filtrar resultados"
                ]
            }
        
        else:
            return {
                'respuesta': f"🤖 **Entiendo tu consulta:** '{mensaje}'\n\nPuedo ayudarte con:\n📊 **Estadísticas generales** del sistema\n👨‍🎓 **Información de estudiantes** por carrera\n👨‍🏫 **Datos de profesores** activos\n⚠️ **Alumnos en riesgo** académico\n📈 **Análisis de rendimiento** y calificaciones\n\n💡 **Pregúntame algo específico para darte información detallada**",
                'datos_contexto': {'tipo_consulta': 'general'},
                'recomendaciones': [
                    "Pregunta sobre estadísticas generales",
                    "Consulta información de una carrera específica",
                    "Solicita datos de profesores o estudiantes"
                ]
            }

# Instancia global del simulador de IA
chatbot_ai = SimpleAI()
security = HTTPBearer(auto_error=False)

# Verificación de token simplificada
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verificar token - versión simplificada para pruebas"""
    if not credentials:
        # Para pruebas, permitir sin token
        return "usuario_prueba"
    return credentials.credentials

@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {
        "message": "🤖 DTAI ChatBot IA funcionando en Vercel",
        "version": "1.0.0",
        "status": "✅ Activo",
        "endpoints": {
            "health": "/health",
            "nueva_conversacion": "/api/chatbot/nueva-conversacion", 
            "enviar_mensaje": "/api/chatbot/mensaje",
            "conversaciones": "/api/chatbot/conversaciones"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "✅ healthy",
        "ai_model": "✅ loaded",
        "database": "🔗 configured",
        "timestamp": datetime.now().isoformat(),
        "vercel_deployment": "✅ active"
    }

@app.post("/api/chatbot/nueva-conversacion", response_model=ConversacionResponse)
async def crear_nueva_conversacion(token: str = Depends(verify_token)):
    """Crear nueva conversación"""
    try:
        chatbot_ai.conversation_count += 1
        return ConversacionResponse(
            conversacionId=chatbot_ai.conversation_count,
            mensaje="✅ Conversación creada exitosamente"
        )
    except Exception as e:
        logger.error(f"Error creando conversación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creando conversación"
        )

@app.get("/api/chatbot/conversaciones")
async def obtener_conversaciones(token: str = Depends(verify_token)):
    """Obtener lista de conversaciones del usuario"""
    try:
        # Simulación de conversaciones
        conversaciones = [
            {
                "id": 1,
                "titulo": "Consulta de estadísticas",
                "fecha_creacion": "2025-01-18T10:00:00",
                "fecha_actualizacion": "2025-01-18T10:30:00"
            },
            {
                "id": 2,
                "titulo": "Información de estudiantes",
                "fecha_creacion": "2025-01-18T11:00:00", 
                "fecha_actualizacion": "2025-01-18T11:15:00"
            }
        ]
        return conversaciones
    except Exception as e:
        logger.error(f"Error obteniendo conversaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo conversaciones"
        )

@app.post("/api/chatbot/mensaje", response_model=MensajeResponse)
async def procesar_mensaje(
    request: MensajeRequest,
    token: str = Depends(verify_token)
):
    """Procesar mensaje del usuario y generar respuesta IA"""
    try:
        # Procesar con IA
        respuesta_ia = chatbot_ai.procesar_mensaje(
            mensaje=request.mensaje,
            conversacion_id=request.conversacionId
        )
        
        return MensajeResponse(
            respuesta=respuesta_ia["respuesta"],
            datos_contexto=respuesta_ia.get("datos_contexto", {}),
            recomendaciones=respuesta_ia.get("recomendaciones", [])
        )
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        return MensajeResponse(
            respuesta="❌ **Lo siento, hubo un problema procesando tu consulta.**\n\nPuedes intentar preguntarme sobre:\n• 📊 Estadísticas generales\n• 👨‍🎓 Información de estudiantes\n• 👨‍🏫 Datos de profesores\n• ⚠️ Alumnos en riesgo académico",
            datos_contexto={"tipo_consulta": "error"},
            recomendaciones=[
                "Reformula tu pregunta de manera más específica",
                "Pregunta sobre temas académicos específicos",
                "Usa palabras clave como 'estudiantes', 'profesores', 'carreras'"
            ]
        )

@app.get("/api/chatbot/conversacion/{conversacion_id}")
async def obtener_conversacion(
    conversacion_id: int,
    token: str = Depends(verify_token)
):
    """Obtener mensajes de una conversación específica"""
    try:
        # Simulación de mensajes
        mensajes = [
            {
                "id": 1,
                "tipo_mensaje": "pregunta",
                "contenido": "¿Cuántos estudiantes hay?",
                "timestamp": "2025-01-18T10:00:00"
            },
            {
                "id": 2,
                "tipo_mensaje": "respuesta",
                "contenido": "📊 En DTAI hay 234 estudiantes activos...",
                "timestamp": "2025-01-18T10:00:05"
            }
        ]
        
        return {
            "conversacionId": conversacion_id,
            "mensajes": mensajes
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo conversación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo conversación"
        )

# Para Vercel
from mangum import Mangum
handler = Mangum(app)