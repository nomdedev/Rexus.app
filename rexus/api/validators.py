"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

API Validators - Validación exhaustiva y sanitización de datos de entrada
"""

import re
import html
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException, Query, Path, Body


class ValidationError(HTTPException):
    """Excepción personalizada para errores de validación."""
    
    def __init__(self, detail: str, field: str = None):
        super().__init__(status_code=422, detail={
            "error": "validation_error",
            "message": detail,
            "field": field,
            "timestamp": datetime.now().isoformat()
        })


class InputSanitizer:
    """Sanitizador de entrada para prevenir ataques."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255, allow_html: bool = False) -> str:
        """
        Sanitiza una cadena de texto.
        
        Args:
            value: Valor a sanitizar
            max_length: Longitud máxima permitida
            allow_html: Si permitir HTML básico
            
        Returns:
            Cadena sanitizada
        """
        if not isinstance(value, str):
            raise ValidationError("El valor debe ser una cadena de texto", "type")
        
        # Limitar longitud
        if len(value) > max_length:
            raise ValidationError(f"El texto excede la longitud máxima de {max_length} caracteres", "length")
        
        # Limpiar espacios
        value = value.strip()
        
        if not allow_html:
            # Escapar HTML para prevenir XSS
            value = html.escape(value)
        
        # Remover caracteres de control
        value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value)
        
        return value
    
    @staticmethod
    def sanitize_sql_identifier(value: str) -> str:
        """
        Sanitiza un identificador SQL (nombre de tabla, columna, etc.).
        
        Args:
            value: Identificador a sanitizar
            
        Returns:
            Identificador sanitizado
        """
        if not isinstance(value, str):
            raise ValidationError("El identificador debe ser una cadena", "type")
        
        # Solo permitir caracteres alfanuméricos y guión bajo
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
            raise ValidationError("Identificador SQL inválido", "format")
        
        # Lista negra de palabras reservadas SQL
        sql_keywords = {
            'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter',
            'truncate', 'union', 'exec', 'execute', 'sp_', 'xp_'
        }
        
        if value.lower() in sql_keywords or value.lower().startswith(('sp_', 'xp_')):
            raise ValidationError("Identificador no permitido", "sql_injection")
        
        return value.lower()
    
    @staticmethod
    def validate_pagination(page: int, page_size: int) -> tuple:
        """
        Valida parámetros de paginación.
        
        Args:
            page: Número de página
            page_size: Tamaño de página
            
        Returns:
            Tupla (page, page_size) validada
        """
        # Validar página
        if page < 1:
            raise ValidationError("El número de página debe ser mayor a 0", "page")
        if page > 10000:  # Límite razonable
            raise ValidationError("Número de página demasiado alto", "page")
        
        # Validar tamaño de página
        if page_size < 1:
            raise ValidationError("El tamaño de página debe ser mayor a 0", "page_size")
        if page_size > 1000:  # Prevenir DoS
            raise ValidationError("Tamaño de página demasiado grande (máximo 1000)", "page_size")
        
        return page, page_size
    
    @staticmethod
    def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple:
        """
        Valida rango de fechas.
        
        Args:
            start_date: Fecha de inicio (ISO format)
            end_date: Fecha de fin (ISO format)
            
        Returns:
            Tupla (start_date, end_date) como objetos datetime
        """
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("Formato de fecha de inicio inválido (use ISO 8601)", "start_date")
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("Formato de fecha de fin inválido (use ISO 8601)", "end_date")
        
        # Validar lógica de rango
        if start_dt and end_dt:
            if start_dt > end_dt:
                raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin", "date_range")
            
            # Prevenir rangos muy amplios
            delta = end_dt - start_dt
            if delta.days > 3650:  # 10 años
                raise ValidationError("Rango de fechas demasiado amplio (máximo 10 años)", "date_range")
        
        return start_dt, end_dt


class SecureQuery:
    """Constructores de queries seguros."""
    
    @staticmethod
    def build_where_clause(filters: Dict[str, Any], allowed_fields: List[str]) -> tuple:
        """
        Construye cláusula WHERE de forma segura.
        
        Args:
            filters: Diccionario de filtros
            allowed_fields: Campos permitidos para filtrar
            
        Returns:
            Tupla (where_clause, params)
        """
        conditions = []
        params = []
        
        for field, value in filters.items():
            if field not in allowed_fields:
                raise ValidationError(f"Campo de filtro no permitido: {field}", "filter")
            
            # Sanitizar nombre del campo
            safe_field = InputSanitizer.sanitize_sql_identifier(field)
            
            if value is not None:
                if isinstance(value, (list, tuple)):
                    # Filtro IN
                    placeholders = ','.join(['?' for _ in value])
                    conditions.append(f"{safe_field} IN ({placeholders})")
                    params.extend(value)
                elif isinstance(value, str) and '*' in value:
                    # Filtro LIKE
                    like_value = value.replace('*', '%')
                    conditions.append(f"{safe_field} LIKE ?")
                    params.append(like_value)
                else:
                    # Filtro de igualdad
                    conditions.append(f"{safe_field} = ?")
                    params.append(value)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        return where_clause, params


# Validadores Pydantic para modelos de entrada

class PaginationModel(BaseModel):
    """Modelo para validación de paginación."""
    page: int = Field(default=1, ge=1, le=10000, description="Número de página")
    page_size: int = Field(default=50, ge=1, le=1000, description="Elementos por página")
    
    @validator('page', 'page_size')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("El valor debe ser positivo")
        return v


class FilterModel(BaseModel):
    """Modelo base para filtros."""
    search: Optional[str] = Field(None, max_length=255, description="Texto de búsqueda")
    categoria: Optional[str] = Field(None, max_length=100, description="Categoría")
    estado: Optional[str] = Field(None, max_length=50, description="Estado")
    fecha_inicio: Optional[str] = Field(None, description="Fecha inicio (ISO 8601)")
    fecha_fin: Optional[str] = Field(None, description="Fecha fin (ISO 8601)")
    
    @validator('search', 'categoria', 'estado')
    def sanitize_text_fields(cls, v):
        if v:
            return InputSanitizer.sanitize_string(v)
        return v
    
    @validator('fecha_inicio', 'fecha_fin')
    def validate_dates(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Formato de fecha inválido (use ISO 8601)")
        return v


class InventoryCreateModel(BaseModel):
    """Modelo para creación de inventario."""
    codigo: str = Field(..., max_length=50, description="Código del producto")
    nombre: str = Field(..., max_length=255, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Descripción")
    categoria: str = Field(..., max_length=100, description="Categoría")
    precio: Decimal = Field(..., ge=0, decimal_places=2, description="Precio")
    stock: int = Field(..., ge=0, description="Stock disponible")
    stock_minimo: int = Field(0, ge=0, description="Stock mínimo")
    
    @validator('codigo', 'nombre', 'categoria')
    def sanitize_required_fields(cls, v):
        return InputSanitizer.sanitize_string(v, allow_html=False)
    
    @validator('descripcion')
    def sanitize_description(cls, v):
        if v:
            return InputSanitizer.sanitize_string(v, max_length=1000, allow_html=False)
        return v
    
    @validator('precio')
    def validate_price(cls, v):
        if v > Decimal('999999999.99'):
            raise ValueError("Precio demasiado alto")
        return v


class UserCreateModel(BaseModel):
    """Modelo para creación de usuarios."""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: str = Field(..., max_length=255, description="Email")
    nombre: str = Field(..., max_length=100, description="Nombre")
    apellido: str = Field(..., max_length=100, description="Apellido")
    rol: str = Field(..., max_length=50, description="Rol del usuario")
    departamento: Optional[str] = Field(None, max_length=100, description="Departamento")
    
    @validator('username')
    def validate_username(cls, v):
        # Solo caracteres alfanuméricos y algunos especiales
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError("Username contiene caracteres no válidos")
        return v.lower()
    
    @validator('email')
    def validate_email(cls, v):
        # Validación básica de email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Formato de email inválido")
        return v.lower()
    
    @validator('nombre', 'apellido', 'departamento')
    def sanitize_text_fields(cls, v):
        if v:
            return InputSanitizer.sanitize_string(v, allow_html=False)
        return v
    
    @validator('rol')
    def validate_role(cls, v):
        allowed_roles = ['ADMIN', 'MANAGER', 'USER', 'VIEWER']
        if v.upper() not in allowed_roles:
            raise ValueError(f"Rol no válido. Permitidos: {allowed_roles}")
        return v.upper()


# Decoradores para validación de endpoints

def validate_pagination_params(page: int = Query(1, ge=1, le=10000), 
                             page_size: int = Query(50, ge=1, le=1000)):
    """Validador de parámetros de paginación."""
    return InputSanitizer.validate_pagination(page, page_size)


def validate_sql_identifier(identifier: str):
    """Validador de identificadores SQL."""
    return InputSanitizer.sanitize_sql_identifier(identifier)


def rate_limit_check(max_requests: int = 100, window_seconds: int = 3600):
    """
    Decorador para rate limiting básico.
    
    Args:
        max_requests: Máximo número de requests
        window_seconds: Ventana de tiempo en segundos
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Implementar rate limiting aquí
            # Por simplicidad, solo log por ahora
            from ..utils.secure_logger import log_info
            log_info(f"API call to {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Middleware de validación de entrada

class InputValidationMiddleware:
    """Middleware para validación global de entrada."""
    
    def __init__(self):
        self.max_payload_size = 10 * 1024 * 1024  # 10MB
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',               # XSS
            r'on\w+\s*=',                # Event handlers
            r'union\s+select',           # SQL Injection
            r'drop\s+table',            # SQL Injection
            r'exec\s*\(',               # Command injection
            r'eval\s*\(',               # Code injection
        ]
    
    def validate_request_size(self, content_length: int):
        """Valida el tamaño del request."""
        if content_length > self.max_payload_size:
            raise ValidationError("Request demasiado grande", "size")
    
    def scan_for_attacks(self, content: str):
        """Escanea contenido en busca de patrones de ataque."""
        content_lower = content.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                from ..utils.secure_logger import log_security_event
                log_security_event("SUSPICIOUS_INPUT", "HIGH", f"Pattern detected: {pattern[:50]}")
                raise ValidationError("Contenido sospechoso detectado", "security")


# Instancia global del middleware
input_validator = InputValidationMiddleware()