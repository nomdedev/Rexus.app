"""
Tests para Sistema de Caché Encriptado - Rexus.app

Tests que validan el sistema de caché encriptado con validación de permisos,
incluyendo encriptación, compresión, TTL y auditoría de accesos.

Author: Rexus Testing Team
Date: 2025-08-11
Version: 1.0.0
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock

# Import the modules we're testing
try:
    from rexus.utils.encrypted_cache import (
        EncryptedCache,
        CacheEntry,
        CacheStats,
        init_encrypted_cache,
        get_encrypted_cache,
        cache_put,
        cache_get,
        cache_delete
    )
    ENCRYPTED_CACHE_AVAILABLE = True
except ImportError:
    ENCRYPTED_CACHE_AVAILABLE = False


@pytest.mark.skipif(not ENCRYPTED_CACHE_AVAILABLE, reason="Encrypted cache modules not available")
class TestEncryptedCache:
    """Tests para la clase EncryptedCache."""

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_initialization(self, mock_check_permission):
        """Test que valida la inicialización del caché encriptado."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(
            password="test_password_123",
            max_size=1024*1024,  # 1MB
            default_ttl=3600,
            compress_threshold=512
        )

        assert cache.max_size == 1024*1024
        assert cache.default_ttl == 3600
        assert cache.compress_threshold == 512
        assert cache.password_hash is not None
        assert cache.cipher is not None
        assert isinstance(cache._cache, dict)
        assert len(cache._cache) == 0

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_put_and_get_basic(self, mock_check_permission):
        """Test que valida almacenamiento y recuperación básica."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        # Almacenar valor
        test_data = {"message": "Hello, encrypted world!", "number": 42}
        success = cache.put(
            key="test_key",
            value=test_data,
            resource_type="test_resource",
            required_permission="read",
            user_id=1
        )

        assert success

        # Recuperar valor
        retrieved_data = cache.get("test_key", user_id=1)

        assert retrieved_data == test_data
        assert retrieved_data["message"] == "Hello, encrypted world!"
        assert retrieved_data["number"] == 42

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_get_with_default(self, mock_check_permission):
        """Test que valida recuperación con valor por defecto."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        # Intentar recuperar clave no existente
        default_value = "default_response"
        result = cache.get("nonexistent_key", user_id=1, default=default_value)

        assert result == default_value

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_permission_validation_success(self, mock_check_permission):
        """Test que valida validación exitosa de permisos."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        # Almacenar con permisos específicos
        cache.put(
            key="secure_data",
            value={"secret": "confidential"},
            resource_type="sensitive_resource",
            required_permission="admin",
            user_id=1
        )

        # Recuperar con permisos válidos
        result = cache.get("secure_data", user_id=1)

        assert result is not None
        assert result["secret"] == "confidential"
        mock_check_permission.assert_called_with(1, "sensitive_resource", "admin")

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_permission_validation_denied(self, mock_check_permission):
        """Test que valida denegación de permisos."""
        # Primera llamada permite almacenar, segunda deniega recuperar
        mock_check_permission.side_effect = [True, False]

        cache = EncryptedCache(password="test_password")

        # Almacenar datos
        cache.put(
            key="restricted_data",
            value={"sensitive": "information"},
            resource_type="classified",
            required_permission="top_secret",
            user_id=1
        )

        # Intentar recuperar sin permisos
        result = cache.get("restricted_data", user_id=2, default="access_denied")

        assert result == "access_denied"
        # Verificar que se intentó validar permisos
        assert mock_check_permission.call_count == 2

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_ttl_expiration(self, mock_check_permission):
        """Test que valida expiración por TTL."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        # Almacenar con TTL muy corto
        cache.put(
            key="short_lived",
            value={"expires": "soon"},
            resource_type="temporary",
            required_permission="read",
            ttl=1,  # 1 segundo
            user_id=1
        )

        # Inmediatamente debe estar disponible
        result = cache.get("short_lived", user_id=1)
        assert result is not None

        # Esperar expiración
        time.sleep(1.5)

        # Ahora debe estar expirado
        expired_result = cache.get("short_lived", user_id=1, default="expired")
        assert expired_result == "expired"

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_compression(self, mock_check_permission):
        """Test que valida compresión automática."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password", compress_threshold=100)

        # Crear datos grandes para forzar compresión
        large_data = {"text": "x" * 1000, "numbers": list(range(1000))}

        success = cache.put(
            key="large_data",
            value=large_data,
            resource_type="bulk_data",
            required_permission="read",
            user_id=1
        )

        assert success

        # Verificar que se puede recuperar correctamente
        retrieved_data = cache.get("large_data", user_id=1)
        assert retrieved_data == large_data
        assert retrieved_data["text"] == "x" * 1000
        assert len(retrieved_data["numbers"]) == 1000

        # Verificar que la entrada está marcada como comprimida
        with cache._lock:
            entry = cache._cache["large_data"]
            assert entry.compressed == True

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_forced_compression(self, mock_check_permission):
        """Test que valida compresión forzada."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password", compress_threshold=1000)

        # Datos pequeños con compresión forzada
        small_data = {"small": "data"}

        success = cache.put(
            key="force_compressed",
            value=small_data,
            resource_type="test",
            required_permission="read",
            compress=True,  # Forzar compresión
            user_id=1
        )

        assert success

        # Verificar recuperación correcta
        result = cache.get("force_compressed", user_id=1)
        assert result == small_data

        # Verificar que está comprimido
        with cache._lock:
            entry = cache._cache["force_compressed"]
            assert entry.compressed == True

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_delete_entry(self, mock_check_permission):
        """Test que valida eliminación de entradas."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        # Almacenar entrada
        cache.put("deletable",
{"data": "to_delete"},
            "test",
            "read",
            user_id=1)

        # Verificar que existe
        assert cache.exists("deletable", user_id=1)

        # Eliminar
        deleted = cache.delete("deletable", user_id=1)
        assert deleted

        # Verificar que ya no existe
        assert not cache.exists("deletable", user_id=1)
        result = cache.get("deletable", user_id=1, default="not_found")
        assert result == "not_found"

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_delete_permission_denied(self, mock_check_permission):
        """Test que valida denegación de eliminación por permisos."""
        # Permitir almacenar y leer, denegar eliminar
        def permission_side_effect(user_id, resource, action):
            return action != "delete"

        mock_check_permission.side_effect = permission_side_effect

        cache = EncryptedCache(password="test_password")

        # Almacenar entrada
        cache.put("protected",
{"data": "protected"},
            "secure",
            "read",
            user_id=1)

        # Intentar eliminar sin permisos
        deleted = cache.delete("protected", user_id=1)
        assert not deleted

        # Verificar que sigue existiendo
        assert cache.exists("protected", user_id=1)

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_invalidate_pattern(self, mock_check_permission):
        """Test que valida invalidación por patrón."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        # Almacenar múltiples entradas con patrón
        cache.put("user:1:profile",
{"name": "User 1"},
            "user",
            "read",
            user_id=1)
        cache.put("user:2:profile",
{"name": "User 2"},
            "user",
            "read",
            user_id=1)
        cache.put("user:3:settings",
{"theme": "dark"},
            "user",
            "read",
            user_id=1)
        cache.put("post:1:content",
{"title": "Post 1"},
            "post",
            "read",
            user_id=1)

        # Invalidar patrón de usuarios
        invalidated = cache.invalidate_pattern("user:*", user_id=1)

        assert invalidated == 3

        # Verificar que solo los usuarios se invalidaron
        assert cache.get("user:1:profile", user_id=1, default="gone") == "gone"
        assert cache.get("user:2:profile", user_id=1, default="gone") == "gone"
        assert cache.get("user:3:settings", user_id=1, default="gone") == "gone"
        assert cache.get("post:1:content", user_id=1) is not None

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_clear_all(self, mock_check_permission):
        """Test que valida limpieza completa del caché."""
        def permission_side_effect(user_id, resource, action):
            # Solo admin puede limpiar caché
            return user_id == 1 and resource == "cache" and action == "admin"

        mock_check_permission.side_effect = permission_side_effect

        cache = EncryptedCache(password="test_password")

        # Almacenar varias entradas
        cache.put("item1", {"data": 1}, "test", "read", user_id=1)
        cache.put("item2", {"data": 2}, "test", "read", user_id=1)
        cache.put("item3", {"data": 3}, "test", "read", user_id=1)

        # Usuario normal no puede limpiar
        cleared = cache.clear_all(user_id=2)
        assert not cleared

        # Admin puede limpiar
        cleared = cache.clear_all(user_id=1)
        assert cleared

        # Verificar que está vacío
        with cache._lock:
            assert len(cache._cache) == 0

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_get_stats(self, mock_check_permission):
        """Test que valida obtención de estadísticas."""
        def permission_side_effect(user_id, resource, action):
            # Solo usuarios con permisos de lectura pueden ver stats
            return resource == "cache" and action == "read" and user_id == 1

        mock_check_permission.side_effect = permission_side_effect

        cache = EncryptedCache(password="test_password")

        # Usuario sin permisos no puede ver stats
        stats = cache.get_stats(user_id=2)
        assert stats is None

        # Usuario con permisos puede ver stats
        stats = cache.get_stats(user_id=1)
        assert stats is not None
        assert isinstance(stats, CacheStats)
        assert stats.total_entries == 0
        assert stats.total_size_bytes == 0
        assert stats.hit_count == 0
        assert stats.miss_count == 0

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_stats_tracking(self, mock_check_permission):
        """Test que valida seguimiento de estadísticas."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        # Generar hits y misses
        cache.put("existing", {"data": "exists"}, "test", "read", user_id=1)

        # Hits
        cache.get("existing", user_id=1)  # Hit
        cache.get("existing", user_id=1)  # Hit

        # Misses
        cache.get("nonexistent1", user_id=1)  # Miss
        cache.get("nonexistent2", user_id=1)  # Miss
        cache.get("nonexistent3", user_id=1)  # Miss

        # Verificar estadísticas
        stats = cache.get_stats(user_id=1)
        assert stats.hit_count == 2
        assert stats.miss_count == 3
        assert stats.total_entries == 1

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_eviction_on_size_limit(self, mock_check_permission):
        """Test que valida desalojo por límite de tamaño."""
        mock_check_permission.return_value = True

        # Caché muy pequeño para forzar desalojos
        cache = EncryptedCache(password="test_password", max_size=1024)  # 1KB

        # Almacenar datos que excedan el límite
        large_data = "x" * 500  # 500 bytes cada uno

        cache.put("entry1", {"data": large_data}, "test", "read", user_id=1)
        cache.put("entry2", {"data": large_data}, "test", "read", user_id=1)

        # Debe haber 2 entradas
        with cache._lock:
            assert len(cache._cache) == 2

        # Agregar tercera entrada que debería forzar desalojo
        cache.put("entry3", {"data": large_data}, "test", "read", user_id=1)

        # Debe haberse desalojado alguna entrada
        with cache._lock:
            assert len(cache._cache) <= 2

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_access_count_tracking(self, mock_check_permission):
        """Test que valida seguimiento de conteo de accesos."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        cache.put("tracked",
{"data": "access_tracking"},
            "test",
            "read",
            user_id=1)

        # Accesos múltiples
        for _ in range(5):
            cache.get("tracked", user_id=1)

        # Verificar conteo de accesos
        with cache._lock:
            entry = cache._cache["tracked"]
            assert entry.access_count == 5

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_metadata_storage(self, mock_check_permission):
        """Test que valida almacenamiento de metadatos."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="test_password")

        metadata = {
            "creator": "test_user",
            "category": "test_data",
            "version": "1.0"
        }

        cache.put(
            "with_metadata",
            {"data": "has_metadata"},
            "test",
            "read",
            user_id=1,
            metadata=metadata
        )

        # Verificar que los metadatos se almacenaron
        with cache._lock:
            entry = cache._cache["with_metadata"]
            assert entry.metadata == metadata
            assert entry.metadata["creator"] == "test_user"
            assert entry.metadata["category"] == "test_data"

    def test_shutdown(self):
        """Test que valida apagado limpio del caché."""
        with patch('rexus.utils.encrypted_cache.check_permission', return_value=True):
            cache = EncryptedCache(password="test_password")

            # Almacenar algunas entradas
            cache.put("item1", {"data": 1}, "test", "read", user_id=1)
            cache.put("item2", {"data": 2}, "test", "read", user_id=1)

            # Verificar que hay entradas
            with cache._lock:
                assert len(cache._cache) == 2

            # Apagar
            cache.shutdown()

            # Verificar que se limpió
            with cache._lock:
                assert len(cache._cache) == 0


@pytest.mark.skipif(not ENCRYPTED_CACHE_AVAILABLE, reason="Encrypted cache modules not available")
class TestEncryptedCacheGlobalFunctions:
    """Tests para las funciones globales del caché encriptado."""

    def test_init_and_get_encrypted_cache(self):
        """Test que valida inicialización global del caché."""
        cache = init_encrypted_cache(password="global_test_password")

        assert cache is not None
        assert isinstance(cache, EncryptedCache)

        # Obtener instancia global
        global_cache = get_encrypted_cache()

        assert global_cache is cache

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_cache_put_global(self, mock_check_permission):
        """Test que valida función global de almacenamiento."""
        mock_check_permission.return_value = True

        init_encrypted_cache(password="global_test_password")

        success = cache_put(
            "global_key",
            {"global": "data"},
            "global_resource",
            "read",
            user_id=1
        )

        assert success

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_cache_get_global(self, mock_check_permission):
        """Test que valida función global de recuperación."""
        mock_check_permission.return_value = True

        init_encrypted_cache(password="global_test_password")

        # Almacenar usando función global
        cache_put("global_key",
{"global": "data"},
            "global_resource",
            "read",
            user_id=1)

        # Recuperar usando función global
        result = cache_get("global_key", user_id=1)

        assert result == {"global": "data"}

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_cache_delete_global(self, mock_check_permission):
        """Test que valida función global de eliminación."""
        mock_check_permission.return_value = True

        init_encrypted_cache(password="global_test_password")

        # Almacenar y eliminar usando funciones globales
        cache_put("to_delete",
{"will": "be_deleted"},
            "test",
            "read",
            user_id=1)

        deleted = cache_delete("to_delete", user_id=1)
        assert deleted

        # Verificar que se eliminó
        result = cache_get("to_delete", user_id=1, default="not_found")
        assert result == "not_found"


@pytest.mark.skipif(not ENCRYPTED_CACHE_AVAILABLE, reason="Encrypted cache modules not available")
class TestEncryptedCacheIntegration:
    """Tests de integración para el caché encriptado."""

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_full_cache_workflow(self, mock_check_permission):
        """Test que valida flujo completo del caché."""
        # Configurar permisos dinámicos
        def permission_logic(user_id, resource, action):
            # Admin tiene todos los permisos
            if user_id == 1:
                return True
            # Usuario normal solo lectura
            if user_id == 2 and action == "read":
                return True
            return False

        mock_check_permission.side_effect = permission_logic

        cache = EncryptedCache(password="integration_test")

        # 1. Admin almacena datos
        admin_data = {"sensitive": "admin_data", "level": "confidential"}
        success = cache.put(
            "admin:sensitive_data",
            admin_data,
            "admin_resource",
            "read",
            user_id=1
        )
        assert success

        # 2. Admin puede leer sus datos
        result = cache.get("admin:sensitive_data", user_id=1)
        assert result == admin_data

        # 3. Usuario normal puede leer (tiene permisos)
        result = cache.get("admin:sensitive_data", user_id=2)
        assert result == admin_data

        # 4. Usuario sin permisos no puede eliminar
        deleted = cache.delete("admin:sensitive_data", user_id=2)
        assert not deleted

        # 5. Admin puede eliminar
        deleted = cache.delete("admin:sensitive_data", user_id=1)
        assert deleted

        # 6. Dato ya no existe
        result = cache.get("admin:sensitive_data", user_id=1, default="gone")
        assert result == "gone"

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_encryption_integrity(self, mock_check_permission):
        """Test que valida integridad de la encriptación."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="encryption_test")

        # Datos sensibles
        sensitive_data = {
            "password": "super_secret_password",
            "api_key": "sk-1234567890abcdef",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC..."
        }

        # Almacenar
        cache.put("sensitive", sensitive_data, "secrets", "read", user_id=1)

        # Verificar que los datos están encriptados en memoria
        with cache._lock:
            entry = cache._cache["sensitive"]
            # Los datos encriptados no deben contener el texto original
            encrypted_bytes = entry.encrypted_data
            assert b"super_secret_password" not in encrypted_bytes
            assert b"sk-1234567890abcdef" not in encrypted_bytes

        # Pero deben recuperarse correctamente
        retrieved = cache.get("sensitive", user_id=1)
        assert retrieved == sensitive_data
        assert retrieved["password"] == "super_secret_password"

    @patch('rexus.utils.encrypted_cache.check_permission')
    def test_concurrent_access_simulation(self, mock_check_permission):
        """Test que simula acceso concurrente al caché."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="concurrent_test")

        # Simular múltiples usuarios accediendo concurrentemente
        import threading
        import time

        results = {}
        errors = []

        def user_operations(user_id):
            try:
                # Cada usuario almacena sus propios datos
                user_data = {"user_id": user_id, "timestamp": time.time()}
                cache.put(f"user:{user_id}:data",
user_data,
                    "user",
                    "read",
                    user_id=user_id)

                # Esperar un poco
                time.sleep(0.1)

                # Recuperar datos
                retrieved = cache.get(f"user:{user_id}:data", user_id=user_id)
                results[user_id] = retrieved

            except Exception as e:
                errors.append(f"User {user_id}: {str(e)}")

        # Crear múltiples threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=user_operations, args=(i,))
            threads.append(thread)
            thread.start()

        # Esperar que terminen
        for thread in threads:
            thread.join()

        # Verificar resultados
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5

        for user_id in range(5):
            assert user_id in results
            assert results[user_id]["user_id"] == user_id

    @patch('rexus.utils.encrypted_cache.check_permission')
    @patch('rexus.utils.encrypted_cache.log_security_event')
    def test_security_audit_integration(self, mock_log, mock_check_permission):
        """Test que valida integración con auditoría de seguridad."""
        mock_check_permission.return_value = True

        cache = EncryptedCache(password="audit_test")

        # Operaciones que deben generar logs
        cache.put("audited_data",
{"sensitive": True},
            "audit",
            "read",
            user_id=1)
        cache.get("audited_data", user_id=1)
        cache.delete("audited_data", user_id=1)

        # Verificar que se generaron eventos de auditoría
        mock_log.assert_called()

        # Verificar tipos de eventos
        call_args_list = mock_log.call_args_list
        event_types = [call[0][0] for call in call_args_list]

        assert "ENCRYPTED_CACHE_INITIALIZED" in event_types
        assert "CACHE_ENTRY_STORED" in event_types
        assert "CACHE_HIT" in event_types
        assert "CACHE_ENTRY_DELETED" in event_types


# Fixtures para tests de caché encriptado
@pytest.fixture
def encrypted_cache():
    """Fixture que proporciona instancia de caché encriptado para tests."""
    with patch('rexus.utils.encrypted_cache.check_permission', return_value=True):
        cache = EncryptedCache(password="test_fixture_password")
        yield cache
        cache.shutdown()


@pytest.fixture
def cache_test_data():
    """Fixture con datos de prueba para tests de caché."""
    return {
        'test_entries': [
            {
                'key': 'user:1:profile',
                'value': {'name': 'John Doe', 'email': 'john@example.com'},
                'resource': 'user_profiles',
                'permission': 'read'
            },
            {
                'key': 'config:app_settings',
                'value': {'theme': 'dark', 'notifications': True},
                'resource': 'configuration',
                'permission': 'read'
            },
            {
                'key': 'sensitive:api_keys',
                'value': {'stripe': 'sk_test_123', 'github': 'ghp_456'},
                'resource': 'secrets',
                'permission': 'admin'
            }
        ],
        'users': [
            {'id': 1, 'role': 'admin'},
            {'id': 2, 'role': 'user'},
            {'id': 3, 'role': 'guest'}
        ]
    }
