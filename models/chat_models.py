"""
Modelos de datos para el ChatBot
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConversacionCreate(BaseModel):
    """Modelo para crear nueva conversación"""
    titulo: str = "Nueva conversación"

class ConversacionResponse(BaseModel):
    """Respuesta al crear conversación"""
    conversacionId: int
    mensaje: str

class MensajeRequest(BaseModel):
    """Request para enviar mensaje"""
    conversacionId: int
    mensaje: str

class MensajeResponse(BaseModel):
    """Respuesta del chatbot"""
    respuesta: str
    datos_contexto: Dict[str, Any] = {}
    recomendaciones: List[str] = []

class IntentClassification(BaseModel):
    """Clasificación de intención del mensaje"""
    intent: str
    confidence: float
    entities: Dict[str, Any] = {}

class QueryResult(BaseModel):
    """Resultado de consulta SQL"""
    data: List[Dict[str, Any]]
    total_rows: int
    query_type: str