"""
Procesador de Lenguaje Natural
Motor principal de comprensión de texto
"""

import re
import json
import os
from typing import Dict, List, Any, Tuple, Optional
import logging
from difflib import SequenceMatcher
import unicodedata

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Procesador de lenguaje natural optimizado para consultas académicas"""
    
    def __init__(self):
        self.intents_data = self._load_intents()
        self.stopwords = self._get_spanish_stopwords()
        self.synonyms = self._load_synonyms()
        
    def _load_intents(self) -> Dict:
        """Cargar intenciones desde archivo JSON"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            intents_path = os.path.join(current_dir, '..', 'data', 'intents.json')
            
            with open(intents_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando intents: {e}")
            return {"intents": {}, "entities": {}}
    
    def _get_spanish_stopwords(self) -> set:
        """Palabras vacías en español"""
        return {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son',
            'con', 'para', 'al', 'del', 'los', 'las', 'una', 'hay', 'está', 'pero', 'sus', 'me', 'yo', 'mi', 'tu', 'si',
            'como', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel', 'aquella', 'aquellos', 'aquellas'
        }
    
    def _load_synonyms(self) -> Dict[str, List[str]]:
        """Diccionario de sinónimos para mejorar comprensión"""
        return {
            'estudiantes': ['alumnos', 'estudiante', 'alumno', 'educandos'],
            'profesores': ['docentes', 'maestros', 'académicos', 'instructores'],
            'calificaciones': ['notas', 'puntuaciones', 'evaluaciones', 'scores'],
            'promedio': ['media', 'promedio general', 'rendimiento'],
            'carreras': ['programas', 'licenciaturas', 'especialidades'],
            'cuántos': ['cantidad', 'número', 'total', 'qué cantidad'],
            'riesgo': ['problemas', 'dificultades', 'en peligro', 'complicaciones'],
            'estadísticas': ['datos', 'números', 'información', 'métricas']
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalizar texto para mejor procesamiento"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover acentos
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        
        # Limpiar caracteres especiales pero mantener espacios y números
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extraer entidades nombradas del texto"""
        entities = {
            'carreras': [],
            'cuatrimestres': [],
            'tipos_riesgo': [],
            'niveles_riesgo': [],
            'numeros': [],
            'nombres': []
        }
        
        normalized_text = self.normalize_text(text)
        
        # Extraer carreras
        for carrera in self.intents_data.get('entities', {}).get('carreras', []):
            carrera_norm = self.normalize_text(carrera)
            if carrera_norm in normalized_text or any(word in normalized_text for word in carrera_norm.split()):
                entities['carreras'].append(carrera)
        
        # Extraer cuatrimestres
        for cuatri in self.intents_data.get('entities', {}).get('cuatrimestres', []):
            if self.normalize_text(cuatri) in normalized_text:
                entities['cuatrimestres'].append(cuatri)
        
        # Extraer números
        numbers = re.findall(r'\d+', text)
        entities['numeros'] = [int(n) for n in numbers]
        
        # Extraer nombres propios (palabras que empiezan con mayúscula)
        names = re.findall(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b', text)
        entities['nombres'] = names
        
        return entities
    
    def calculate_intent_similarity(self, text: str, intent_data: Dict) -> float:
        """Calcular similitud entre texto e intención"""
        normalized_text = self.normalize_text(text)
        words = [w for w in normalized_text.split() if w not in self.stopwords]
        
        # Puntuación por keywords
        keyword_score = 0
        total_keywords = len(intent_data.get('keywords', []))
        
        for keyword in intent_data.get('keywords', []):
            keyword_norm = self.normalize_text(keyword)
            if keyword_norm in normalized_text:
                keyword_score += 1
            # Verificar sinónimos
            for synonym_group in self.synonyms.values():
                if keyword in synonym_group and any(syn in normalized_text for syn in synonym_group):
                    keyword_score += 0.8
        
        keyword_score = keyword_score / max(total_keywords, 1)
        
        # Puntuación por patrones
        pattern_score = 0
        patterns = intent_data.get('patterns', [])
        
        for pattern in patterns:
            pattern_norm = self.normalize_text(pattern.replace('{carrera}', '').replace('{nombre}', ''))
            similarity = SequenceMatcher(None, normalized_text, pattern_norm).ratio()
            pattern_score = max(pattern_score, similarity)
        
        # Puntuación combinada
        total_score = (keyword_score * 0.6) + (pattern_score * 0.4)
        
        return total_score
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Clasificar intención del mensaje"""
        best_intent = "general"
        best_score = 0.0
        
        for intent_name, intent_data in self.intents_data.get('intents', {}).items():
            score = self.calculate_intent_similarity(text, intent_data)
            
            if score > best_score:
                best_score = score
                best_intent = intent_name
        
        # Umbral mínimo de confianza
        if best_score < 0.3:
            best_intent = "general"
            best_score = 0.5
        
        return {
            'intent': best_intent,
            'confidence': best_score,
            'entities': self.extract_entities(text)
        }
    
    def extract_search_terms(self, text: str) -> List[str]:
        """Extraer términos de búsqueda del texto"""
        normalized_text = self.normalize_text(text)
        words = [w for w in normalized_text.split() if w not in self.stopwords and len(w) > 2]
        
        # Filtrar palabras comunes de consulta
        query_words = {'cuantos', 'como', 'donde', 'cuando', 'porque', 'cual', 'que', 'dame', 'muestra', 'busca'}
        words = [w for w in words if w not in query_words]
        
        return words
    
    def detect_question_type(self, text: str) -> str:
        """Detectar el tipo de pregunta"""
        normalized_text = self.normalize_text(text)
        
        if any(word in normalized_text for word in ['cuantos', 'cantidad', 'numero', 'total']):
            return 'count'
        elif any(word in normalized_text for word in ['quien', 'quienes', 'cual', 'cuales']):
            return 'identify'
        elif any(word in normalized_text for word in ['como', 'de que manera']):
            return 'how'
        elif any(word in normalized_text for word in ['donde', 'en que']):
            return 'where'
        elif any(word in normalized_text for word in ['cuando', 'que fecha']):
            return 'when'
        elif any(word in normalized_text for word in ['porque', 'por que razon']):
            return 'why'
        else:
            return 'general'
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """Análisis completo del mensaje"""
        intent_result = self.classify_intent(message)
        
        return {
            'original_text': message,
            'normalized_text': self.normalize_text(message),
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'entities': intent_result['entities'],
            'search_terms': self.extract_search_terms(message),
            'question_type': self.detect_question_type(message),
            'has_entities': any(intent_result['entities'].values())
        }