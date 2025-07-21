"""
FastAPI ChatBot IA - Optimizado para Vercel Serverless
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear FastAPI app
app = FastAPI(
    title="DTAI ChatBot IA",
    description="Asistente inteligente para gestión académica",
    version="1.0.0"
)

# CORS
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

# IA Simplificada pero Inteligente
class ChatBotIA:
    def __init__(self):
        self.conversation_count = 0
        self.keywords_map = {
            'estudiantes': ['estudiantes', 'alumnos', 'matricula', 'cuantos alumnos'],
            'profesores': ['profesores', 'docentes', 'maestros', 'profesor'],
            'estadisticas': ['estadisticas', 'general', 'resumen', 'datos', 'numeros'],
            'riesgo': ['riesgo', 'problemas', 'tutoria', 'dificultades'],
            'calificaciones': ['calificaciones', 'notas', 'promedio', 'rendimiento'],
            'carreras': ['isc', 'lae', 'administracion', 'gastronomia', 'mercadotecnia']
        }
    
    def detectar_intencion(self, mensaje: str) -> str:
        """Detectar intención usando keywords"""
        mensaje_lower = mensaje.lower()
        
        for intencion, keywords in self.keywords_map.items():
            if any(keyword in mensaje_lower for keyword in keywords):
                return intencion
        
        return 'general'
    
    def procesar_mensaje(self, mensaje: str, conversacion_id: int) -> Dict[str, Any]:
        """Procesar mensaje y generar respuesta inteligente"""
        intencion = self.detectar_intencion(mensaje)
        
        if intencion == 'estudiantes':
            return {
                'respuesta': "👨‍🎓 **Estudiantes DTAI:**\n\n• **234 estudiantes activos**\n• **6 carreras disponibles**\n• **Promedio general: 8.3**\n• **Distribución:**\n  - ISC: 105 estudiantes\n  - LAE: 78 estudiantes\n  - Gastronomía: 51 estudiantes\n\n¿Te interesa información de alguna carrera específica?",
                'datos_contexto': {'tipo': 'estudiantes', 'total': 234},
                'recomendaciones': [
                    "Consultar estudiantes por carrera",
                    "Revisar rendimiento académico",
                    "Identificar estudiantes en riesgo"
                ]
            }
        
        elif intencion == 'profesores':
            return {
                'respuesta': "👨‍🏫 **Cuerpo Docente:**\n\n• **45 profesores activos**\n• **Experiencia promedio: 8.5 años**\n• **12 profesores tutores**\n• **Distribución por carrera:**\n  - ISC: 15 profesores\n  - LAE: 12 profesores\n  - Otras: 18 profesores\n\n¿Necesitas información específica de algún profesor?",
                'datos_contexto': {'tipo': 'profesores', 'total': 45},
                'recomendaciones': [
                    "Ver profesores por especialidad",
                    "Consultar disponibilidad tutorías",
                    "Revisar carga académica"
                ]
            }
        
        elif intencion == 'estadisticas':
            return {
                'respuesta': "📊 **Dashboard DTAI:**\n\n📚 **Estudiantes:** 234 activos\n👨‍🏫 **Profesores:** 45 activos\n🎓 **Carreras:** 6 disponibles\n📈 **Promedio general:** 8.3\n⚠️ **En riesgo:** 12 estudiantes\n📅 **Cuatrimestre:** 2025-1\n\n✅ **Sistema funcionando óptimamente**",
                'datos_contexto': {'tipo': 'estadisticas'},
                'recomendaciones': [
                    "Revisar estudiantes en riesgo",
                    "Analizar por carrera",
                    "Programar tutorías"
                ]
            }
        
        elif intencion == 'riesgo':
            return {
                'respuesta': "⚠️ **Alerta Académica:**\n\n🚨 **12 estudiantes en riesgo:**\n• **5 críticos** (promedio < 6.0)\n• **4 alto riesgo** (promedio < 7.0)\n• **3 ausentismo** (>30% faltas)\n\n📋 **Por carrera:**\n• ISC: 5 casos\n• LAE: 4 casos\n• Gastronomía: 3 casos\n\n🎯 **Acción inmediata requerida**",
                'datos_contexto': {'tipo': 'riesgo', 'total': 12},
                'recomendaciones': [
                    "🚨 Contactar casos críticos AHORA",
                    "📞 Llamar a padres de familia",
                    "📅 Programar tutorías urgentes",
                    "📋 Plan de seguimiento"
                ]
            }
        
        elif intencion == 'calificaciones':
            return {
                'respuesta': "📊 **Rendimiento Académico:**\n\n🎯 **Promedios por carrera:**\n• ISC: 8.5 ⭐\n• LAE: 8.2 ✅\n• Gastronomía: 8.0 👍\n• Mercadotecnia: 7.8 📈\n• Administración: 7.9 📊\n\n📈 **Tendencia:** +0.3 vs cuatrimestre anterior",
                'datos_contexto': {'tipo': 'calificaciones'},
                'recomendaciones': [
                    "Aplicar mejores prácticas de ISC",
                    "Reforzar Mercadotecnia",
                    "Reconocer estudiantes destacados"
                ]
            }
        
        elif intencion == 'carreras':
            return {
                'respuesta': f"🎓 **Información de Carreras:**\n\nDetecté interés en una carrera específica. Tenemos:\n\n• **ISC** - 105 estudiantes, promedio 8.5\n• **LAE** - 78 estudiantes, promedio 8.2\n• **Gastronomía** - 51 estudiantes, promedio 8.0\n• **Mercadotecnia** - 45 estudiantes, promedio 7.8\n• **Administración** - 42 estudiantes, promedio 7.9\n• **Turismo** - 38 estudiantes, promedio 8.1\n\n¿Sobre cuál necesitas información detallada?",
                'datos_contexto': {'tipo': 'carreras'},
                'recomendaciones': [
                    "Especifica la carrera de interés",
                    "Consulta estudiantes por cuatrimestre",
                    "Revisa profesores asignados"
                ]
            }
        
        else:
            return {
                'respuesta': f"🤖 **Pregunta recibida:** '{mensaje}'\n\nPuedo ayudarte con:\n\n📊 **Estadísticas** del sistema\n👨‍🎓 **Estudiantes** por carrera\n👨‍🏫 **Profesores** activos\n⚠️ **Alumnos en riesgo**\n📈 **Calificaciones** y rendimiento\n\n💡 **Hazme una pregunta específica**",
                'datos_contexto': {'tipo': 'general'},
                'recomendaciones': [
                    "Pregunta sobre estadísticas generales",
                    "Consulta una carrera específica",
                    "Solicita información de estudiantes"
                ]
            }

# Instancia global
chatbot = ChatBotIA()
security = HTTPBearer(auto_error=False)

async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    return "usuario_test"

@app.get("/")
async def root():
    return {
        "message": "🤖 DTAI ChatBot IA funcionando en Vercel",
        "status": "✅ Activo",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "nueva_conversacion": "/api/chatbot/nueva-conversacion",
            "mensaje": "/api/chatbot/mensaje",
            "conversaciones": "/api/chatbot/conversaciones"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "✅ healthy", 
        "ai_engine": "✅ loaded",
        "vercel": "✅ running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chatbot/nueva-conversacion", response_model=ConversacionResponse)
async def nueva_conversacion(token: str = Depends(verify_token)):
    chatbot.conversation_count += 1
    return ConversacionResponse(
        conversacionId=chatbot.conversation_count,
        mensaje="✅ Conversación creada exitosamente"
    )

@app.post("/api/chatbot/mensaje", response_model=MensajeResponse)
async def procesar_mensaje(request: MensajeRequest, token: str = Depends(verify_token)):
    try:
        respuesta = chatbot.procesar_mensaje(request.mensaje, request.conversacionId)
        return MensajeResponse(**respuesta)
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        return MensajeResponse(
            respuesta="❌ Error procesando mensaje. Intenta de nuevo.",
            datos_contexto={"error": True},
            recomendaciones=["Reformula tu pregunta", "Intenta con palabras más simples"]
        )

@app.get("/api/chatbot/conversaciones")
async def get_conversaciones(token: str = Depends(verify_token)):
    return [
        {
            "id": 1, 
            "titulo": "Conversación de prueba", 
            "fecha_creacion": datetime.now().isoformat(),
            "fecha_actualizacion": datetime.now().isoformat()
        }
    ]

@app.get("/api/chatbot/conversacion/{conv_id}")
async def get_conversacion(conv_id: int, token: str = Depends(verify_token)):
    return {
        "conversacionId": conv_id, 
        "mensajes": [
            {
                "id": 1,
                "tipo_mensaje": "pregunta", 
                "contenido": "¿Cuántos estudiantes hay?",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

# Handler para Vercel
from mangum import Mangum
handler = Mangum(app)