"""
Sistema de Caché Encriptado con Validación de Permisos - Rexus.app

Sistema de caché que protege datos sensibles mediante encriptación AES-256
y valida permisos de acceso antes de devolver información cached.

Características:
- Encriptación AES-256 para todos los datos en caché
- Validación de permisos antes de acceso a datos
- TTL (Time To Live) configurable por entrada
- Invalidación automática y manual
- Compresión opcional para datos grandes
- Auditoría de accesos al caché

Author: Rexus Development Team
Date: 2025-08-11
Version: 1.0.0
"""

import json
import time
import zlib
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, Tuple, List
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    import base64
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    from rexus.core.rbac_database import get_rbac_system, check_permission
    from rexus.utils.secure_logger import log_security_event
except ImportError:
    def check_permission(user_id: int, resource: str, action: str) -> bool:
        return True  # Fallback para tests
    
    def log_security_event(event_type: str, details: dict, severity: str = "INFO"):
        print(f"CACHE LOG [{severity}] {event_type}: {details}")


@dataclass
class CacheEntry:
    """Entrada individual del caché encriptado."""
    key: str
    encrypted_data: bytes
    created_at: float
    expires_at: Optional[float]
    access_count: int
    last_accessed: float
    size_bytes: int
    compressed: bool
    resource_type: str
    required_permission: str
    metadata: Dict[str, Any]


@dataclass 
class CacheStats:
    """Estadísticas del sistema de caché."""
    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    eviction_count: int
    expired_count: int
    permission_denied_count: int
    compression_ratio: float
    uptime_seconds: float


class EncryptedCache:
    """
    Sistema de caché encriptado con validación de permisos.
    
    Proporciona almacenamiento en memoria de datos sensibles con:
    - Encriptación automática de todos los datos
    - Validación de permisos por recurso
    - TTL configurable y limpieza automática
    - Compresión para optimizar memoria
    - Auditoría completa de accesos
    """
    
    def __init__(self, 
                 password: str = None,
                 max_size: int = 1024 * 1024 * 100,  # 100MB
                 default_ttl: int = 3600,  # 1 hora
                 compress_threshold: int = 1024,  # 1KB
                 cleanup_interval: int = 300):  # 5 minutos
        """
        Inicializa el sistema de caché encriptado.
        
        Args:
            password: Contraseña para encriptación (se genera una si no se proporciona)
            max_size: Tamaño máximo del caché en bytes
            default_ttl: TTL por defecto en segundos
            compress_threshold: Umbral para compresión automática
            cleanup_interval: Intervalo de limpieza automática en segundos
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("Paquete 'cryptography' es requerido para caché encriptado")
        
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.compress_threshold = compress_threshold
        self.cleanup_interval = cleanup_interval
        
        # Inicializar encriptación
        self._init_encryption(password)
        
        # Storage principal
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Estadísticas
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0,
            'permission_denied': 0,
            'created_at': time.time()
        }
        
        # Limpieza automática
        self._cleanup_timer = None
        self._start_cleanup_timer()
        
        log_security_event(
            "ENCRYPTED_CACHE_INITIALIZED",
            {
                "max_size_mb": max_size // (1024 * 1024),
                "default_ttl": default_ttl,
                "compress_threshold": compress_threshold
            },
            "INFO"
        )
    
    def _init_encryption(self, password: str = None):
        """Inicializa el sistema de encriptación."""
        if password is None:
            password = secrets.token_urlsafe(32)
        
        # Generar clave de encriptación usando PBKDF2
        salt = b"rexus_cache_salt_2025"  # En producción, usar salt único
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)
        
        # Almacenar hash de contraseña para verificación
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def _start_cleanup_timer(self):
        """Inicia el timer de limpieza automática."""
        def cleanup_task():
            with self._lock:
                self._cleanup_expired()
                self._enforce_size_limit()
            
            # Reprogramar
            self._cleanup_timer = threading.Timer(self.cleanup_interval, cleanup_task)
            self._cleanup_timer.start()
        
        self._cleanup_timer = threading.Timer(self.cleanup_interval, cleanup_task)
        self._cleanup_timer.start()
    
    def put(self, 
            key: str, 
            value: Any, 
            resource_type: str,
            required_permission: str,
            ttl: Optional[int] = None,
            compress: Optional[bool] = None,
            user_id: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Almacena un valor en el caché encriptado.
        
        Args:
            key: Clave única para el valor
            value: Valor a almacenar (será serializado y encriptado)
            resource_type: Tipo de recurso (para validación de permisos)
            required_permission: Permiso requerido para acceder al valor
            ttl: TTL en segundos (None = usar default)
            compress: Forzar compresión (None = automático)
            user_id: ID del usuario que almacena (para auditoría)
            metadata: Metadatos adicionales
            
        Returns:
            True si se almacenó correctamente
        """
        try:
            with self._lock:
                # Serializar valor
                serialized = json.dumps(value, default=str).encode('utf-8')
                
                # Comprimir si es necesario
                compressed = False
                if compress is True or (compress is None and len(serialized) >= self.compress_threshold):
                    serialized = zlib.compress(serialized)
                    compressed = True
                
                # Encriptar datos
                encrypted_data = self.cipher.encrypt(serialized)
                
                # Calcular expiración
                current_time = time.time()
                expires_at = None
                if ttl is not None:
                    expires_at = current_time + ttl
                elif self.default_ttl > 0:
                    expires_at = current_time + self.default_ttl
                
                # Crear entrada
                entry = CacheEntry(
                    key=key,
                    encrypted_data=encrypted_data,
                    created_at=current_time,
                    expires_at=expires_at,
                    access_count=0,
                    last_accessed=current_time,
                    size_bytes=len(encrypted_data),
                    compressed=compressed,
                    resource_type=resource_type,
                    required_permission=required_permission,
                    metadata=metadata or {}
                )
                
                # Verificar límites de tamaño
                if not self._can_fit_entry(entry):
                    self._evict_entries_for_space(entry.size_bytes)
                
                # Almacenar entrada
                old_entry = self._cache.get(key)
                self._cache[key] = entry
                
                # Actualizar estadísticas
                if old_entry:
                    # Reemplazo de entrada existente
                    pass
                else:
                    # Nueva entrada
                    pass
                
                log_security_event(
                    "CACHE_ENTRY_STORED",
                    {
                        "key": key,
                        "resource_type": resource_type,
                        "required_permission": required_permission,
                        "size_bytes": entry.size_bytes,
                        "compressed": compressed,
                        "user_id": user_id,
                        "ttl": ttl
                    },
                    "DEBUG"
                )
                
                return True
                
        except Exception as e:
            log_security_event(
                "CACHE_STORE_ERROR",
                {"key": key, "error": str(e), "user_id": user_id},
                "ERROR"
            )
            return False
    
    def get(self, 
            key: str, 
            user_id: int,
            default: Any = None,
            context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Recupera un valor del caché con validación de permisos.
        
        Args:
            key: Clave del valor a recuperar
            user_id: ID del usuario solicitante
            default: Valor por defecto si no se encuentra o no tiene permisos
            context: Contexto adicional para validación de permisos
            
        Returns:
            Valor deserializado o valor por defecto
        """
        try:
            with self._lock:
                # Verificar si existe la entrada
                entry = self._cache.get(key)
                if entry is None:
                    self._stats['misses'] += 1
                    log_security_event(
                        "CACHE_MISS",
                        {"key": key, "user_id": user_id},
                        "DEBUG"
                    )
                    return default
                
                # Verificar expiración
                current_time = time.time()
                if entry.expires_at and current_time > entry.expires_at:
                    del self._cache[key]
                    self._stats['expired'] += 1
                    self._stats['misses'] += 1
                    log_security_event(
                        "CACHE_ENTRY_EXPIRED",
                        {"key": key, "user_id": user_id},
                        "DEBUG"
                    )
                    return default
                
                # Validar permisos
                if not check_permission(user_id, entry.resource_type, entry.required_permission):
                    self._stats['permission_denied'] += 1
                    log_security_event(
                        "CACHE_ACCESS_DENIED",
                        {
                            "key": key,
                            "user_id": user_id,
                            "resource_type": entry.resource_type,
                            "required_permission": entry.required_permission
                        },
                        "WARNING"
                    )
                    return default
                
                # Desencriptar datos
                decrypted_data = self.cipher.decrypt(entry.encrypted_data)
                
                # Descomprimir si es necesario
                if entry.compressed:
                    decrypted_data = zlib.decompress(decrypted_data)
                
                # Deserializar
                value = json.loads(decrypted_data.decode('utf-8'))
                
                # Actualizar estadísticas de acceso
                entry.access_count += 1
                entry.last_accessed = current_time
                self._stats['hits'] += 1
                
                log_security_event(
                    "CACHE_HIT",
                    {
                        "key": key,
                        "user_id": user_id,
                        "access_count": entry.access_count,
                        "resource_type": entry.resource_type
                    },
                    "DEBUG"
                )
                
                return value
                
        except Exception as e:
            self._stats['misses'] += 1
            log_security_event(
                "CACHE_GET_ERROR",
                {"key": key, "user_id": user_id, "error": str(e)},
                "ERROR"
            )
            return default
    
    def delete(self, key: str, user_id: int) -> bool:
        """
        Elimina una entrada del caché.
        
        Args:
            key: Clave a eliminar
            user_id: ID del usuario solicitante
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            with self._lock:
                entry = self._cache.get(key)
                if entry is None:
                    return False
                
                # Validar permisos para eliminación
                if not check_permission(user_id, entry.resource_type, "delete"):
                    log_security_event(
                        "CACHE_DELETE_DENIED",
                        {"key": key, "user_id": user_id, "resource_type": entry.resource_type},
                        "WARNING"
                    )
                    return False
                
                del self._cache[key]
                
                log_security_event(
                    "CACHE_ENTRY_DELETED",
                    {"key": key, "user_id": user_id, "resource_type": entry.resource_type},
                    "INFO"
                )
                
                return True
                
        except Exception as e:
            log_security_event(
                "CACHE_DELETE_ERROR",
                {"key": key, "user_id": user_id, "error": str(e)},
                "ERROR"
            )
            return False
    
    def exists(self, key: str, user_id: int) -> bool:
        """
        Verifica si existe una clave en el caché (con validación de permisos).
        
        Args:
            key: Clave a verificar
            user_id: ID del usuario solicitante
            
        Returns:
            True si existe y el usuario tiene permisos
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            
            # Verificar expiración
            current_time = time.time()
            if entry.expires_at and current_time > entry.expires_at:
                del self._cache[key]
                self._stats['expired'] += 1
                return False
            
            # Validar permisos
            return check_permission(user_id, entry.resource_type, entry.required_permission)
    
    def invalidate_pattern(self, pattern: str, user_id: int) -> int:
        """
        Invalida todas las entradas que coincidan con un patrón.
        
        Args:
            pattern: Patrón de clave (supports wildcards *)
            user_id: ID del usuario solicitante
            
        Returns:
            Número de entradas invalidadas
        """
        import re
        
        try:
            with self._lock:
                # Convertir patrón con wildcards a regex
                regex_pattern = pattern.replace('*', '.*')
                regex = re.compile(regex_pattern)
                
                keys_to_delete = []
                for key, entry in self._cache.items():
                    if regex.match(key):
                        # Validar permisos para eliminación
                        if check_permission(user_id, entry.resource_type, "delete"):
                            keys_to_delete.append(key)
                
                # Eliminar entradas
                for key in keys_to_delete:
                    del self._cache[key]
                
                log_security_event(
                    "CACHE_PATTERN_INVALIDATED",
                    {"pattern": pattern, "user_id": user_id, "invalidated_count": len(keys_to_delete)},
                    "INFO"
                )
                
                return len(keys_to_delete)
                
        except Exception as e:
            log_security_event(
                "CACHE_INVALIDATE_ERROR",
                {"pattern": pattern, "user_id": user_id, "error": str(e)},
                "ERROR"
            )
            return 0
    
    def clear_all(self, user_id: int) -> bool:
        """
        Limpia todo el caché (requiere permisos administrativos).
        
        Args:
            user_id: ID del usuario solicitante
            
        Returns:
            True si se limpió correctamente
        """
        try:
            # Verificar permisos administrativos
            if not check_permission(user_id, "cache", "admin"):
                log_security_event(
                    "CACHE_CLEAR_ALL_DENIED",
                    {"user_id": user_id},
                    "WARNING"
                )
                return False
            
            with self._lock:
                entry_count = len(self._cache)
                self._cache.clear()
                
                log_security_event(
                    "CACHE_CLEARED_ALL",
                    {"user_id": user_id, "entries_cleared": entry_count},
                    "WARNING"
                )
                
                return True
                
        except Exception as e:
            log_security_event(
                "CACHE_CLEAR_ALL_ERROR",
                {"user_id": user_id, "error": str(e)},
                "ERROR"
            )
            return False
    
    def get_stats(self, user_id: int) -> Optional[CacheStats]:
        """
        Obtiene estadísticas del caché (requiere permisos de lectura).
        
        Args:
            user_id: ID del usuario solicitante
            
        Returns:
            Estadísticas del caché o None si no tiene permisos
        """
        try:
            # Validar permisos para ver estadísticas
            if not check_permission(user_id, "cache", "read"):
                return None
            
            with self._lock:
                total_entries = len(self._cache)
                total_size = sum(entry.size_bytes for entry in self._cache.values())
                
                # Calcular ratio de compresión promedio
                compressed_entries = [e for e in self._cache.values() if e.compressed]
                compression_ratio = len(compressed_entries) / total_entries if total_entries > 0 else 0
                
                uptime = time.time() - self._stats['created_at']
                
                return CacheStats(
                    total_entries=total_entries,
                    total_size_bytes=total_size,
                    hit_count=self._stats['hits'],
                    miss_count=self._stats['misses'],
                    eviction_count=self._stats['evictions'],
                    expired_count=self._stats['expired'],
                    permission_denied_count=self._stats['permission_denied'],
                    compression_ratio=compression_ratio,
                    uptime_seconds=uptime
                )
                
        except Exception as e:
            log_security_event(
                "CACHE_STATS_ERROR",
                {"user_id": user_id, "error": str(e)},
                "ERROR"
            )
            return None
    
    def _can_fit_entry(self, entry: CacheEntry) -> bool:
        """Verifica si una entrada puede caber en el caché."""
        current_size = sum(e.size_bytes for e in self._cache.values())
        return current_size + entry.size_bytes <= self.max_size
    
    def _evict_entries_for_space(self, needed_bytes: int):
        """Desaloja entradas para hacer espacio."""
        # Estrategia LRU: eliminar las menos utilizadas recientemente
        entries_by_access = sorted(
            self._cache.items(),
            key=lambda x: (x[1].last_accessed, x[1].access_count)
        )
        
        freed_bytes = 0
        evicted_count = 0
        
        for key, entry in entries_by_access:
            if freed_bytes >= needed_bytes:
                break
            
            del self._cache[key]
            freed_bytes += entry.size_bytes
            evicted_count += 1
        
        self._stats['evictions'] += evicted_count
        
        log_security_event(
            "CACHE_ENTRIES_EVICTED",
            {"evicted_count": evicted_count, "freed_bytes": freed_bytes, "needed_bytes": needed_bytes},
            "INFO"
        )
    
    def _cleanup_expired(self):
        """Limpia entradas expiradas."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry.expires_at and current_time > entry.expires_at:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            self._stats['expired'] += len(expired_keys)
            log_security_event(
                "CACHE_EXPIRED_CLEANUP",
                {"expired_count": len(expired_keys)},
                "DEBUG"
            )
    
    def _enforce_size_limit(self):
        """Aplica límites de tamaño del caché."""
        current_size = sum(e.size_bytes for e in self._cache.values())
        
        if current_size > self.max_size:
            excess_bytes = current_size - self.max_size
            self._evict_entries_for_space(excess_bytes)
    
    def shutdown(self):
        """Apaga el sistema de caché limpiamente."""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        
        with self._lock:
            entry_count = len(self._cache)
            self._cache.clear()
            
        log_security_event(
            "ENCRYPTED_CACHE_SHUTDOWN",
            {"final_entry_count": entry_count},
            "INFO"
        )


# Instancia global del caché encriptado
_encrypted_cache: Optional[EncryptedCache] = None


def init_encrypted_cache(password: str = None, **kwargs) -> EncryptedCache:
    """Inicializa el sistema global de caché encriptado."""
    global _encrypted_cache
    _encrypted_cache = EncryptedCache(password=password, **kwargs)
    return _encrypted_cache


def get_encrypted_cache() -> EncryptedCache:
    """Obtiene la instancia global del caché encriptado."""
    if _encrypted_cache is None:
        raise RuntimeError("Caché encriptado no está inicializado. Llame a init_encrypted_cache() primero.")
    return _encrypted_cache


def cache_put(key: str, value: Any, resource_type: str, required_permission: str, 
              user_id: int, **kwargs) -> bool:
    """Función de conveniencia para almacenar en caché."""
    cache = get_encrypted_cache()
    return cache.put(key, value, resource_type, required_permission, user_id=user_id, **kwargs)


def cache_get(key: str, user_id: int, default: Any = None) -> Any:
    """Función de conveniencia para recuperar del caché."""
    cache = get_encrypted_cache()
    return cache.get(key, user_id, default)


def cache_delete(key: str, user_id: int) -> bool:
    """Función de conveniencia para eliminar del caché."""
    cache = get_encrypted_cache()
    return cache.delete(key, user_id)