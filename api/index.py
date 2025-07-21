# api/index.py - Archivo principal para Vercel
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la aplicación
from app import app

# Este archivo es requerido por Vercel para funciones serverless
# Vercel buscará automáticamente este archivo en la carpeta /api/