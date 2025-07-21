# models/__init__.py
"""
Módulo de modelos de IA para el sistema conversacional educativo.
Contiene los componentes principales para procesamiento de lenguaje natural,
generación de consultas SQL y formateo de respuestas.
"""

from .conversation_ai import ConversationAI
from .query_generator import QueryGenerator
from .response_formatter import ResponseFormatter

__all__ = [
    'ConversationAI',
    'QueryGenerator', 
    'ResponseFormatter'
]

__version__ = '1.0.0'
__author__ = 'Sistema IA Educativo'

# ==============================================================================

# database/__init__.py
"""
Módulo de base de datos para el sistema de IA conversacional.
Proporciona conexión, análisis de esquema y ejecución de consultas para MySQL.
"""

from .connection import DatabaseConnection
from .schema_analyzer import SchemaAnalyzer
from .query_executor import QueryExecutor

__all__ = [
    'DatabaseConnection',
    'SchemaAnalyzer',
    'QueryExecutor'
]

__version__ = '1.0.0'

# Configuración por defecto para la base de datos
DEFAULT_CONFIG = {
    'host': 'bluebyte.space',
    'port': 3306,
    'database': 'bluebyte_dtai_web',
    'charset': 'utf8mb4',
    'autocommit': True
}

# ==============================================================================

# utils/__init__.py
"""
Utilidades para procesamiento de texto y clasificación de intenciones.
Contiene herramientas de NLP específicas para el dominio educativo.
"""

from .text_processor import TextProcessor
from .intent_classifier import IntentClassifier

__all__ = [
    'TextProcessor',
    'IntentClassifier'
]

__version__ = '1.0.0'

# Configuración de procesamiento de texto
TEXT_CONFIG = {
    'remove_accents': True,
    'lowercase': True,
    'remove_punctuation': False,  # Mantener puntuación básica
    'min_word_length': 2,
    'max_word_length': 50
}

# Configuración de clasificación
CLASSIFICATION_CONFIG = {
    'confidence_threshold': 0.6,
    'max_suggestions': 5,
    'fallback_intent': 'consulta_general'
}

# ==============================================================================

# training/__init__.py
"""
Módulo de entrenamiento para modelos de IA conversacional.
Incluye datos de entrenamiento, métricas y funciones de evaluación.
"""

from .training_data import (
    TRAINING_DATA,
    get_all_training_data,
    get_training_data_by_intent,
    validate_training_data,
    DOMAIN_ENTITIES
)
from .train_model import AIModelTrainer

__all__ = [
    'TRAINING_DATA',
    'get_all_training_data',
    'get_training_data_by_intent', 
    'validate_training_data',
    'DOMAIN_ENTITIES',
    'AIModelTrainer'
]

__version__ = '1.0.0'

# Configuración de entrenamiento
TRAINING_CONFIG = {
    'test_size': 0.2,
    'validation_size': 0.1,
    'random_state': 42,
    'cv_folds': 5,
    'min_samples_per_intent': 3,
    'max_features': 5000,
    'ngram_range': (1, 2)
}

# Métricas importantes para evaluación
IMPORTANT_METRICS = [
    'accuracy',
    'precision',
    'recall',
    'f1_score',
    'confusion_matrix',
    'classification_report'
]

# ==============================================================================

# ai-backend/__init__.py (archivo principal)
"""
Sistema de Inteligencia Artificial Conversacional para Gestión Educativa

Este sistema proporciona una interfaz de lenguaje natural para consultar
y analizar datos académicos, con capacidades de:

- Procesamiento de lenguaje natural en español
- Generación automática de consultas SQL
- Análisis de esquema de base de datos
- Respuestas contextuales por rol de usuario
- Sistema de recomendaciones inteligentes

Versión: 1.0.0
Autor: Sistema IA Educativo
Fecha: 2024
"""

import logging
import os
from datetime import datetime

# Configurar logging global
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_system.log') if os.path.exists('.') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

# Información del sistema
__version__ = '1.0.0'
__author__ = 'Sistema IA Educativo'
__email__ = 'soporte@sistemaai.edu'
__status__ = 'Production'

# Configuración global
SYSTEM_CONFIG = {
    'version': __version__,
    'name': 'IA Conversacional Educativa',
    'description': 'Sistema de IA para consultas académicas en lenguaje natural',
    'supported_languages': ['es'],
    'supported_roles': ['alumno', 'profesor', 'directivo'],
    'database_engine': 'MySQL',
    'ml_frameworks': ['scikit-learn', 'pandas', 'numpy'],
    'deployment_platforms': ['Vercel', 'Railway', 'Heroku'],
    'max_query_length': 500,
    'max_response_length': 2000,
    'cache_ttl_minutes': 5,
    'rate_limit_per_minute': 60
}

# Roles y permisos
USER_ROLES = {
    'alumno': {
        'description': 'Estudiante del sistema educativo',
        'permissions': [
            'ver_calificaciones_propias',
            'consultar_horario_propio',
            'solicitar_ayuda',
            'ver_noticias_publicas'
        ],
        'restricted_data': ['datos_otros_alumnos', 'informacion_personal_terceros']
    },
    'profesor': {
        'description': 'Personal docente',
        'permissions': [
            'ver_grupos_asignados',
            'consultar_alumnos_grupos',
            'crear_reportes_riesgo',
            'ver_estadisticas_grupos',
            'gestionar_calificaciones_grupos'
        ],
        'restricted_data': ['datos_financieros', 'informacion_directivos']
    },
    'directivo': {
        'description': 'Personal administrativo y directivo',
        'permissions': [
            'ver_estadisticas_generales',
            'consultar_todos_reportes',
            'gestionar_solicitudes_ayuda',
            'ver_analytics_sistema',
            'acceder_datos_agregados'
        ],
        'restricted_data': ['datos_personales_detallados']
    }
}

# Tipos de consultas soportadas
SUPPORTED_QUERIES = {
    'academicas': [
        'calificaciones',
        'promedios',
        'asignaturas',
        'horarios',
        'grupos'
    ],
    'administrativas': [
        'reportes_riesgo',
        'solicitudes_ayuda',
        'estadisticas',
        'usuarios'
    ],
    'comunicacion': [
        'noticias',
        'foros',
        'encuestas'
    ]
}

# Límites y restricciones
SYSTEM_LIMITS = {
    'max_concurrent_users': 100,
    'max_query_complexity': 'MEDIA',
    'max_result_rows': 1000,
    'cache_max_size_mb': 50,
    'session_timeout_minutes': 30
}

def get_system_info():
    """Obtener información completa del sistema"""
    return {
        'system': SYSTEM_CONFIG,
        'roles': USER_ROLES,
        'queries': SUPPORTED_QUERIES,
        'limits': SYSTEM_LIMITS,
        'startup_time': datetime.now().isoformat(),
        'status': 'active'
    }

def validate_system_requirements():
    """Validar que el sistema tenga todos los requisitos"""
    required_modules = [
        'flask', 'mysql.connector', 'pandas', 'sklearn',
        'numpy', 'nltk', 'flask_cors'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Módulos faltantes: {missing_modules}")
        return False
    
    logger.info("Todos los requisitos del sistema están satisfechos")
    return True

# Mensaje de inicio
logger.info(f"Sistema {SYSTEM_CONFIG['name']} v{__version__} iniciado")
logger.info(f"Soporte para roles: {list(USER_ROLES.keys())}")
logger.info(f"Tipos de consulta: {list(SUPPORTED_QUERIES.keys())}")

# Validar requisitos al importar
if not validate_system_requirements():
    logger.warning("Sistema iniciado con dependencias faltantes")

# Exports principales
__all__ = [
    'SYSTEM_CONFIG',
    'USER_ROLES', 
    'SUPPORTED_QUERIES',
    'SYSTEM_LIMITS',
    'get_system_info',
    'validate_system_requirements'
]