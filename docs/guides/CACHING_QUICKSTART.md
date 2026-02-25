# ⚡ IMPLEMENTACIÓN RÁPIDA DE CACHING CON REDIS

## 🚀 Instalación Rápida (5 minutos)

### **Paso 1: Iniciar Redis con Docker**

```bash
# Iniciar Redis en background
docker-compose -f docker-compose.dev.yml up -d redis

# Verificar que está corriendo
docker-compose -f docker-compose.dev.yml ps

# Ver logs de Redis
docker-compose -f docker-compose.dev.yml logs -f redis
```

### **Paso 2: Instalar Dependencias**

```bash
# Instalar cliente de Redis
pip install redis hiredis
```

### **Paso 3: Verificar Funcionamiento**

```bash
# Test de conexión
python -c "from rexus.utils.cache_manager import CacheManager; cm = CacheManager(); print(cm.get_info())"
```

**Output esperado:**
```python
{
  'status': 'connected',
  'used_memory': '1.5M',
  'connected_clients': 1,
  'total_keys': 0,
  'uptime_seconds': 120
}
```

---

## 📖 Aplicar Caching a Modelos Existentes

### **Opción A: Usar Decorador (RECOMENDADO)**

Agrega una línea a tus métodos existentes:

```python
# Antes (sin caché)
def obtener_estadisticas(self):
    cursor = self.db.cursor()
    cursor.execute("SELECT COUNT(*) FROM productos")
    return cursor.fetchone()[0]

# Después (con caché) ⚡ 100-1000x más rápido
from rexus.utils.cache_manager import cache_result, CacheConfig

@cache_result(tipo_dato='estadisticas', ttl=CacheConfig.TTL_MEDIO)
def obtener_estadisticas(self):
    cursor = self.db.cursor()
    cursor.execute("SELECT COUNT(*) FROM productos")
    return cursor.fetchone()[0]
```

**Métodos que deberían tener caché:**

1. ✅ `obtener_estadisticas()` → TTL: 5 minutos
2. ✅ `obtener_todos()` → TTL: 30 minutos
3. ✅ `buscar_por_categoria()` → TTL: 30 minutos
4. ✅ `obtener_por_id()` → TTL: 10 minutos
5. ❌ `crear_producto()` → NO cachear (invalida en su lugar)
6. ❌ `actualizar_producto()` → NO cachear (invalida en su lugar)

### **Opción B: Cache Manual (Más Control)**

```python
from rexus.utils.cache_manager import CacheManager, cache_invalidate

class MiModelo:
    def __init__(self, db_connection):
        self.db = db_connection
        self.cache = CacheManager.get_instance()

    def obtener_con_cache_manual(self, id):
        # 1. Intentar caché
        cache_key = f"productos:{id}"
        cached = self.cache.get(cache_key)

        if cached is not None:
            return cached  # ⚡ Del caché (1000x más rápido)

        # 2. Si no está, ir a BD
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (id,))
        resultado = self._row_to_dict(cursor.fetchone())

        # 3. Guardar en caché
        self.cache.set(cache_key, resultado, ttl=1800)  # 30 min

        return resultado

    def actualizar(self, id, datos):
        # 1. Actualizar en BD
        self.db.execute("UPDATE productos SET ...")

        # 2. Invalidar caché
        self.cache.delete(f"productos:{id}")
        cache_invalidate('productos')  # Invalidar todos si es necesario
```

---

## 🎯 Los 3 Métodos que MÁS Necesitan Caching

### **1. Estadísticas (⚡⚡⚡ MÁXIMO IMPACTO)**

```python
@cache_result(tipo_dato='estadisticas', ttl=300)  # 5 minutos
def obtener_estadisticas_inventario(self) -> Dict:
    """⚡ Se llama en CADA dashboard, CADA refresh de página"""
    # Tu código actual...
```

**Impacto:** **100-1000x más rápido** después de primera llamada

### **2. Productos Todos**

```python
@cache_result(tipo_dato='productos', ttl=1800)  # 30 minutos
def obtener_todos(self, filtros=None) -> List:
    """⚡ Se llama en CADA listado de productos"""
    # Tu código actual...
```

**Impacto:** **100-500x más rápido**

### **3. Búsquedas**

```python
@cache_result(tipo_dato='productos', ttl=600)  # 10 minutos
def buscar_productos(self, termino: str) -> List:
    """⚡ Buscador se usa MUCHO"""
    # Tu código actual...
```

**Impacto:** **50-200x más rápido** para búsquedas repetidas

---

## 🗑️ Invalidación de Caché

### **Cuándo Invalidar:**

```python
# ✅ Crear nuevo producto
cache_invalidate('productos')

# ✅ Actualizar producto existente
cache_invalidate('productos')

# ✅ Eliminar producto
cache_invalidate('productos')

# ✅ Actualizar stock (cambia estadísticas)
cache_invalidate('estadisticas')

# ❌ NO invalidar al leer (no tiene sentido)
productos = modelo.obtener_todos()  # No invalidar aquí
```

### **Invalidación Selectiva (Más Granular)**

```python
# Invalidar solo producto específico (mejor performance)
cache.delete(f'productos:{producto_id}')

# Invalidar solo categoría específica
cache.delete_pattern('productos:categoria:Vidrios')
```

---

## 📊 Monitorear Hit Rate

```python
# Obtener estadísticas del caché
cache = CacheManager.get_instance()
stats = cache.get_stats()

print(f"Hit Rate: {stats['hit_rate']}")  # Objetivo: >80%
print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Errores: {stats['errors']}")
```

**Hit Rate esperado:**
- **Nuevo:** 0% (todavía nada en caché)
- **1 hora:** 60-70%
- **1 día:** 80-90%
- **Estable:** 85-95%

---

## 🚨 Troubleshooting

### **Problema: "Redis connection refused"**

**Solución:**
```bash
# Verificar que Redis está corriendo
docker ps | grep redis

# Si no está corriendo, iniciarlo
docker-compose -f docker-compose.dev.yml up -d

# Ver logs
docker-compose -f docker-compose.dev.yml logs redis
```

### **Problema: "Datos viejos en caché"**

**Solución:**
```python
# Limpiar TODO el caché
cache = CacheManager.get_instance()
cache.clear_all()

# O invalidar tipo específico
cache_invalidate('productos')
```

### **Problema: "Caché consume mucha memoria"**

**Solución:**
```bash
# Ver uso de memoria
docker stats rexus-redis-dev

# Conectar a Redis CLI
docker exec -it rexus-redis-dev redis-cli

# Ver uso de memoria
INFO memory

# Limpiar si es necesario
FLUSHDB  # ⚠️ Cuidado, borra TODO
```

---

## 📈 Mejoras Esperadas

Con caching implementado, deberías ver:

- ⚡ **Dashboard:** 2-3 segundos → 0.2-0.3 segundos (**10x más rápido**)
- ⚡ **Listas de productos:** 1-2 segundos → 0.01-0.1 segundos (**100x más rápido**)
- ⚡ **Estadísticas:** 500ms → 5-10ms (**100x más rápido**)
- 📉 **Carga de BD:** -70% a -90% menos queries

---

## 🎁 Bonus: Precargar Caché al Iniciar

```python
# En tu app.py o main.py
def precargar_caches():
    """Precarga cachés críticos al iniciar la app"""
    from rexus.modules.inventario.model_cached import InventarioModelCached
    from rexus.modules.obras.model_cached import ObrasModelCached

    inventario = InventarioModelCached(db_connection)
    inventario.precalcular_caches_criticos()

    obras = ObrasModelCached(db_connection)
    obras.precalcular_caches_criticos()

    logger.info("✅ Cachés críticos precargados")

# Llamar al iniciar
precargar_caches()
```

---

**Tiempo total de implementación:** 30-60 minutos para el primer modelo
**Mejora de performance inmediata:** 10-100x más rápido

¿Listo para implementar? 🚀
