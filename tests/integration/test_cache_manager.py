"""
🧪 Tests del CacheManager - Redis Caching
=========================================

Tests del sistema de caching con Redis para asegurar
funcionamiento correcto.

Best practices según:
- Redis Labs Testing Guide
- Test-Driven Development (TDD)
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from rexus.utils.cache_manager import (
    CacheManager,
    CacheConfig,
    CacheKeyBuilder,
    cache_result,
    cache_invalidate
)


class TestCacheKeyBuilder:
    """Tests del constructor de keys de caché"""

    def test_build_simple(self):
        """Test de key simple"""
        key = CacheKeyBuilder.build('productos', 'all')
        assert key == 'productos:all'

    def test_build_con_args(self):
        """Test de key con argumentos posicionales"""
        key = CacheKeyBuilder.build('productos', 'categoria', 'vidrios')
        assert key == 'productos:categoria:vidrios'

    def test_build_con_kwargs(self):
        """Test de key con argumentos con nombre"""
        key = CacheKeyBuilder.build('productos', page=1, per_page=50)
        assert key == 'productos:page:1:per_page:50'

    def test_build_mixto(self):
        """Test de key con args y kwargs mezclados"""
        key = CacheKeyBuilder.build(
            'obras',
            'detalles',
            obra_id=123,
            estado='activo'
        )
        assert 'obras:detalles:obra_id:123:estado:activo' == key

    def test_hash_key(self):
        """Test de hash de key para keys largas"""
        original = "productos:muy_larga:descripcion:con:mucho:detalle"
        hashed = CacheKeyBuilder.hash_key(original)

        # Hash debe ser MD5 (32 caracteres hexadecimales)
        assert len(hashed) == 32
        assert all(c in '0123456789abcdef' for c in hashed)
        assert hashed != original


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis no disponible")
class TestCacheManager:
    """Tests del CacheManager"""

    @pytest.fixture
    def cache_manager(self):
        """CacheManager para tests"""
        return CacheManager(enabled=True)

    @pytest.fixture
    def mock_redis(self):
        """Mock de Redis client"""
        with patch('rexus.utils.cache_manager.redis') as mock_redis_module:
            mock_redis_client = MagicMock()
            mock_redis_client.ping.return_value = True
            mock_redis_module.Redis.return_value = mock_redis_client
            yield mock_redis_client

    def test_singleton_pattern(self):
        """Test que CacheManager es singleton"""
        manager1 = CacheManager()
        manager2 = CacheManager()

        assert manager1 is manager2  # Misma instancia
        assert CacheManager._instance is not None

    def test_get_key_no_existente(self, cache_manager):
        """Test obtener key que no existe"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()
        cache_manager.redis_client.get.return_value = None

        resultado = cache_manager.get('key_inexistente')

        assert resultado is None
        cache_manager.redis_client.get.assert_called_once_with('key_inexistente')

    def test_get_key_existente(self, cache_manager):
        """Test obtener key que existe"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        # Mock de valor JSON
        valor_json = json.dumps({'id': 1, 'nombre': 'Test'})
        cache_manager.redis_client.get.return_value = valor_json

        resultado = cache_manager.get('key_existente')

        assert resultado == {'id': 1, 'nombre': 'Test'}
        assert cache_manager.stats['hits'] == 1

    def test_set_con_ttl(self, cache_manager):
        """Test guardar con TTL"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        resultado = cache_manager.set(
            'productos:all',
            {'productos': []},
            ttl=300
        )

        assert resultado is True
        cache_manager.redis_client.setex.assert_called_once()

    def test_set_sin_ttl(self, cache_manager):
        """Test guardar sin TTL (permanente)"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        resultado = cache_manager.set(
            'configuracion:global',
            {'modo': 'produccion'}
        )

        assert resultado is True
        cache_manager.redis_client.set.assert_called_once()

    def test_set_con_tipo_dato(self, cache_manager):
        """Test guardar usando tipo_dato preconfigurado"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        resultado = cache_manager.set(
            'estadisticas:inventario',
            {'total': 100},
            tipo_dato='estadisticas'  # Usa TTL preconfigurado de 5 min
        )

        assert resultado is True
        # Verificar que se usó el TTL correcto (300 segundos = 5 minutos)
        assert cache_manager.redis_client.setex.call_args[0][1] == 300

    def test_delete_key(self, cache_manager):
        """Test eliminar key"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        resultado = cache_manager.delete('productos:123')

        assert resultado is True
        cache_manager.redis_client.delete.assert_called_once_with('productos:123')

    def test_delete_pattern(self, cache_manager):
        """Test eliminar por patrón"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        # Mock de keys que coinciden
        cache_manager.redis_client.keys.return_value = [
            'productos:1',
            'productos:2',
            'productos:3'
        ]
        cache_manager.redis_client.delete.return_value = 3

        resultado = cache_manager.delete_pattern('productos:*')

        assert resultado == 3
        cache_manager.redis_client.keys.assert_called_once_with('productos:*')

    def test_exists(self, cache_manager):
        """Test verificar si key existe"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        # Key existe
        cache_manager.redis_client.exists.return_value = 1
        assert cache_manager.exists('productos:all') is True

        # Key no existe
        cache_manager.redis_client.exists.return_value = 0
        assert cache_manager.exists('productos:no_existe') is False

    def test_clear_all(self, cache_manager):
        """Test limpiar TODO el caché"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        resultado = cache_manager.clear_all()

        assert resultado is True
        cache_manager.redis_client.flushdb.assert_called_once()

    def test_get_stats(self, cache_manager):
        """Test obtener estadísticas"""
        cache_manager.stats['hits'] = 100
        cache_manager.stats['misses'] = 20
        cache_manager.stats['errors'] = 2

        stats = cache_manager.get_stats()

        assert stats['hits'] == 100
        assert stats['misses'] == 20
        assert stats['errors'] == 2
        assert stats['total_requests'] == 120
        assert 'hit_rate' in stats
        assert stats['hit_rate'] == '83.33%'

    def test_graceful_degradation(self):
        """Test degradación graceful cuando Redis falla"""
        # CacheManager con Redis no disponible
        manager = CacheManager(enabled=True)

        with patch('rexus.utils.cache_manager.REDIS_AVAILABLE', False):
            manager._initialized = False
            manager.__init__(enabled=True)

            # Debe estar deshabilitado
            assert manager.enabled is False
            assert manager.redis_client is None

    def test_cache_desabilitado(self):
        """Test comportamiento cuando caché está deshabilitado"""
        manager = CacheManager(enabled=False)

        # Get debe retornar default
        assert manager.get('key', 'default') == 'default'

        # Set debe retornar False
        assert manager.set('key', 'valor') is False

        # Delete debe retornar False
        assert manager.delete('key') is False


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis no disponible")
class TestCacheDecorator:
    """Tests del decorador @cache_result"""

    @pytest.fixture
    def cache_manager(self):
        """CacheManager para tests"""
        return CacheManager(enabled=True)

    def test_decorador_simple(self, cache_manager):
        """Test decorador sin parámetros"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        @cache_result(tipo_dato='productos')
        def obtener_productos():
            return [{'id': 1}, {'id': 2}]

        # Primera llamada: caché miss
        cache_manager.redis_client.get.return_value = None
        resultado1 = obtener_productos()

        assert resultado1 == [{'id': 1}, {'id': 2}]
        assert cache_manager.stats['misses'] == 1

    def test_decorador_con_parametros(self, cache_manager):
        """Test decorador con parámetros"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        @cache_result(tipo_dato='obras')
        def obtener_obra(obra_id: int):
            return {'id': obra_id, 'nombre': f'Obra {obra_id}'}

        # Primera llamada
        cache_manager.redis_client.get.return_value = None
        resultado1 = obtener_obra(123)

        assert resultado1 == {'id': 123, 'nombre': 'Obra 123'}

    def test_decorador_hit(self, cache_manager):
        """Test decorador cuando hay caché hit"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        @cache_result(tipo_dato='productos')
        def obtener_productos():
            return [{'id': 1}]

        # Setup: Valor en caché
        valor_cache = json.dumps([{'id': 1}])
        cache_manager.redis_client.get.return_value = valor_cache

        # Segunda llamada: caché hit
        resultado = obtener_productos()

        assert resultado == [{'id': 1}]
        assert cache_manager.stats['hits'] == 1


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis no disponible")
class TestCacheInvalidation:
    """Tests de invalidación de caché"""

    @pytest.fixture
    def cache_manager(self):
        """CacheManager para tests"""
        return CacheManager(enabled=True)

    def test_invalidate_tipo(self, cache_manager):
        """Test invalidación por tipo de dato"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        # Mock de keys
        cache_manager.redis_client.keys.return_value = [
            'estadisticas:inventario',
            'estadisticas:obras',
            'estadisticas:ventas'
        ]
        cache_manager.redis_client.delete.return_value = 3

        resultado = cache_manager.invalidate_tipo('estadisticas')

        assert resultado == 3
        cache_manager.redis_client.keys.assert_called_once_with('estadisticas:*')

    def test_invalidate_key_especifica(self, cache_manager):
        """Test invalidación de key específica"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        cache_manager.redis_client.delete.return_value = 1

        cache_invalidate('productos', id=123)

        # Verificar que se borró la key específica
        cache_manager.redis_client.delete.assert_called_once()

    def test_invalidate_patron(self, cache_manager):
        """Test invalidación por patrón manual"""
        cache_manager.enabled = True
        cache_manager.redis_client = MagicMock()

        cache_manager.redis_client.keys.return_value = [
            'productos:categoria:A',
            'productos:categoria:B'
        ]
        cache_manager.redis_client.delete.return_value = 2

        cache_manager.delete_pattern('productos:categoria:*')

        assert cache_manager.redis_client.keys.call_count == 1


class TestCacheConfig:
    """Tests de configuración de caché"""

    def test_ttls_preconfigurados(self):
        """Test que TTLs estén correctamente configurados"""
        assert CacheConfig.TTL_CORTO == 60           # 1 minuto
        assert CacheConfig.TTL_MEDIO == 300          # 5 minutos
        assert CacheConfig.TTL_LARGO == 1800         # 30 minutos
        assert CacheConfig.TTL_MUY_LARGO == 3600     # 1 hora

    def test_cache_config_por_tipo(self):
        """Test TTLs específicos por tipo de dato"""
        assert CacheConfig.CACHE_CONFIG['estadisticas'] == 300      # 5 min
        assert CacheConfig.CACHE_CONFIG['productos'] == 1800        # 30 min
        assert CacheConfig.CACHE_CONFIG['obras'] == 300            # 5 min
        assert CacheConfig.CACHE_CONFIG['usuarios'] == 60           # 1 min
        assert CacheConfig.CACHE_CONFIG['permisos'] == 60          # 1 min
        assert CacheConfig.CACHE_CONFIG['configuracion'] == 3600  # 1 hora

    def test_prefijos(self):
        """Test prefijos de keys"""
        assert CacheConfig.PREFIX_ESTADISTICAS == 'estadisticas'
        assert CacheConfig.PREFIX_PRODUCTOS == 'productos'
        assert CacheConfig.PREFIX_OBRAS == 'obras'
        assert CacheConfig.PREFIX_USUARIOS == 'usuarios'
        assert CacheConfig.PREFIX_PERMISOS == 'permisos'


class TestCacheIntegration:
    """Tests de integración del sistema de caché"""

    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis no disponible")
    def test_ciclo_completo_cache(self):
        """
        Test del ciclo completo de caché:
        1. Miss: Va a BD
        2. Guarda en caché
        3. Hit: Obtiene de caché
        4. Invalidación
        5. Miss nuevamente: Va a BD
        """
        # Este test requiere Redis real, se ejecuta solo si Redis está disponible
        pytest.skip("Requiere Redis corriendo - usar docker-compose up redis")
