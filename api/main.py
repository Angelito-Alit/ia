"""
FastAPI Main Application para ChatBot IA
Compatible con Vercel Serverless Functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime
import json
import logging

# Imports locales
from core.config import settings
from core.database import DatabaseManager
from ia.chatbot_ai import ChatBotAI
from models.chat_models import (
    ConversacionCreate, 
    ConversacionResponse, 
    MensajeRequest, 
    MensajeResponse
)

# Configurar logging
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
    allow_origins=["*"],  # En producción, especifica tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancias globales
db_manager = DatabaseManager()
chatbot_ai = ChatBotAI()
security = HTTPBearer()

# Verificación de token (simplificada para tu caso)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT - simplificado"""
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido"
        )
    return token

@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {
        "message": "DTAI ChatBot IA funcionando",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexión a BD
        db_status = await db_manager.check_connection()
        
        return {
            "status": "healthy",
            "database": "connected" if db_status else "disconnected",
            "ai_model": "loaded",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/chatbot/nueva-conversacion", response_model=ConversacionResponse)
async def crear_nueva_conversacion(token: str = Depends(verify_token)):
    """Crear nueva conversación"""
    try:
        # Obtener usuario desde token (simplificado)
        usuario_id = 1  # Por ahora hardcodeado, después implementaremos JWT completo
        
        conversacion_id = await db_manager.crear_conversacion(usuario_id)
        
        return ConversacionResponse(
            conversacionId=conversacion_id,
            mensaje="Conversación creada exitosamente"
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
        usuario_id = 1  # Hardcodeado por ahora
        conversaciones = await db_manager.obtener_conversaciones(usuario_id)
        
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
        usuario_id = 1  # Hardcodeado por ahora
        
        # Guardar mensaje del usuario
        await db_manager.guardar_mensaje(
            conversacion_id=request.conversacionId,
            tipo_mensaje="pregunta",
            contenido=request.mensaje
        )
        
        # Procesar con IA
        respuesta_ia = await chatbot_ai.procesar_mensaje(
            mensaje=request.mensaje,
            conversacion_id=request.conversacionId,
            usuario_id=usuario_id
        )
        
        # Guardar respuesta de la IA
        await db_manager.guardar_mensaje(
            conversacion_id=request.conversacionId,
            tipo_mensaje="respuesta", 
            contenido=respuesta_ia["respuesta"]
        )
        
        return MensajeResponse(
            respuesta=respuesta_ia["respuesta"],
            datos_contexto=respuesta_ia.get("datos_contexto", {}),
            recomendaciones=respuesta_ia.get("recomendaciones", [])
        )
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando mensaje"
        )

@app.get("/api/chatbot/conversacion/{conversacion_id}")
async def obtener_conversacion(
    conversacion_id: int,
    token: str = Depends(verify_token)
):
    """Obtener mensajes de una conversación específica"""
    try:
        mensajes = await db_manager.obtener_mensajes_conversacion(conversacion_id)
        
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

# Para desarrollo local
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# Para Vercel
from mangum import Mangum
handler = Mangum(app)