"""
Configuración del sistema - Versión corregida
"""

import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configuraciones del sistema"""
    
    # Base de datos
    DB_HOST: str = "bluebyte.space"
    DB_USER: str = "bluebyte_angel"
    DB_PASSWORD: str = "orbitalsoft"
    DB_NAME: str = "bluebyte_dtai_web"
    DB_PORT: int = 3306
    
    # IA y ML
    MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    MAX_RESPONSE_LENGTH: int = 500
    CONVERSATION_MEMORY_SIZE: int = 10
    
    # Seguridad
    SECRET_KEY: str = "tu_clave_secreta_super_segura_aqui_cambiala"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Entorno
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# Configuración de logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}