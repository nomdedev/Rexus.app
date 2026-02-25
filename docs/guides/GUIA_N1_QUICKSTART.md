"""
📚 GUÍA PRÁCTICA - Corrección de Queries N+1
==========================================

Guía paso a paso para identificar y corregir el problema N+1 con ejemplos
reales del proyecto Rexus.app.

Autor: Rexus.app Team
Basado en: SQL Server Performance Best Practices

## 🚨 ¿QUÉ ES EL PROBLEMA N+1?

El problema N+1 ocurre cuando ejecutas 1 query principal + N queries adicionales
en un loop, en lugar de usar un JOIN.

### ❌ EJEMPLO DEL PROBLEMA

```python
# ❌ N+1 PROBLEMA - 101 queries para 100 obras
def obtener_obras_con_detalles_bad(self):
    """
    ❌ MAL: Ejecuta 1 query por cada obra
    """
    # Query 1: Obtener todas las obras
    cursor.execute("SELECT * FROM obras")
    obras = cursor.fetchall()  # 100 obras

    resultados = []
    for obra in obras:  # ← CICLO OVER 100 ITERACIONES
        obra_dict = dict(zip(columnas, obra))

        # Query N: Detalles de cada obra (1 query por obra)
        cursor.execute(
            "SELECT * FROM obra_detalles WHERE obra_id = ?",
            (obra['id'],)
        )
        detalles = cursor.fetchall()
        obra_dict['detalles'] = detalles

        resultados.append(obra_dict)

    # Total: 1 + 100 = 101 queries 😱
    return resultados
```

**Problemas:**
- **101 queries** para 100 obras
- **Latencia:** ~100ms × 101 = ~10 segundos
- **Uso de BD:** 100% más alto
- **Escalabilidad:** Empeora con más datos

### ✅ SOLUCIÓN CON JOIN

```python
# ✅ BUENO: Solo 1 query para todo
def obtener_obras_con_detalles_good(self):
    """
    ✅ BIEN: Usa JOIN - 1 sola query
    """
    # Query única con JOIN
    query = """
        SELECT
            o.id as obra_id,
            o.codigo,
            o.nombre as obra_nombre,
            o.estado,
            od.id as detalle_id,
            od.material_id,
            od.cantidad
        FROM obras o
        LEFT JOIN obra_detalles od ON o.id = od.obra_id
        ORDER BY o.codigo, od.id
    """

    cursor.execute(query)
    filas = cursor.fetchall()  # 100 filas × 7 columnas

    # Procesar en Python (en memoria)
    obras_dict = {}
    for fila in filas:
        obra_id = fila[0]

        if obra_id not in obras_dict:
            obras_dict[obra_id] = {
                'id': fila[0],
                'codigo': fila[1],
                'nombre': fila[2],
                'estado': fila[3],
                'detalles': []
            }

        # Agregar detalles
        if fila[4] is not None:  #detalle_id
            obras_dict[obra_id]['detalles'].append({
                'id': fila[4],
                'material_id': fila[5],
                'cantidad': fila[6]
            })

    # Total: 1 query 😎
    return list(obras_dict.values())
```

**Beneficios:**
- **1 sola query** (en lugar de 101)
- **Latencia:** ~100-200ms (en lugar de ~10s)
- **Mejora:** **50-100x más rápido**
- **Escalabilidad:** Funciona igual con 100,000 obras

---

## 🔍 CÓMO IDENTIFICAR N+1 EN TU CÓDIGO

### **Step 1: Busca patrones como estos:**

```python
# ❌ PATRÓN 1: Loop con execute adentro
for item in lista:
    cursor.execute("SELECT ... WHERE id = ?", (item['id'],))

# ❌ PATRÓN 2: Método que llama a otro método que hace query
for obra in obras:
    detalles = self.obtener_detalles_obra(obra['id'])  # Hace query interna
```

### **Step 2: Verificar con logs**

Agrega logging antes y después:

```python
logger.info(f"ANTES: Query a BD")

for item in lista:
    cursor.execute(...)  # ← Esto en loop es sospechoso

logger.info(f"DESPUÉS: Query ejecutada")  # ← Si aparece N veces, es N+1
```

---

## 📋 EJEMPLOS REALES CORREGIDOS

### **EJEMPLO 1: Herrajes por Obra**

**❌ ANTES (N+1):**
```python
# rexus/modules/03_herrajes/model.py:147-165
def obtener_herrajes_por_obra(self, obra_id: int):
    cursor = self.db_connection.cursor()

    # ✅ 1 query para obtener la obra
    query = """
        SELECT h.*, ho.cantidad_requerida, ho.cantidad_instalada
        FROM herrajes h
        INNER JOIN herrajes_obra ho ON h.id = ho.herraje_id
        WHERE ho.obra_id = ?
        ORDER BY h.codigo
    """

    cursor.execute(query, (obra_id,))
    resultados = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    herrajes_obra = [dict(zip(columnas, row)) for row in resultados]

    # ✅ ESTE BIEN: Ya usa JOIN 👍
    return herrajes_obra
```

**✅ CORRECTO:** Este método YA usa JOIN, no tiene N+1.

---

### **EJEMPLO 2: Productos con Categorías**

**Caso hipotético (para demostración):**

```python
# ❌ N+1 PROBLEM
def obtener_productos_con_categorias_bad(self):
    # Query 1: Obtener productos
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    resultados = []
    for prod in productos:
        prod_dict = dict(zip(columnas, prod))

        # Query N: Obtener categoría de cada producto ← N+1
        cursor.execute(
            "SELECT nombre FROM categorias WHERE id = ?",
            (prod['categoria_id'],)
        )
        categoria = cursor.fetchone()
        prod_dict['categoria'] = categoria[0]

        resultados.append(prod_dict)

    return resultados

# ✅ SOLUCIÓN CON JOIN
def obtener_productos_con_categorias_good(self):
    query = """
        SELECT
            p.*,
            c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY p.codigo
    """

    cursor.execute(query)
    filas = cursor.fetchall()
    resultados = [dict(zip(columnas, fila)) for fila in filas]

    return resultados
```

---

## 🎯 PLAN DE CORRECCIÓN

### **Prioridad ALTA:**

1. **Crear SQL optimizados** para joins complejos
2. **Agregar índices** a las columnas de JOIN
3. **Documentar** las queries optimizadas

---

## 📝 EJEMPLO PRÁCTICO PARA TU PROYECTO

Voy a crear SQL optimizado para un caso común:

```sql
-- ❌ SQL HARDCODEADO (evitar)
-- En lugar de hacer loops, usa esta query:

-- ✅ QUERY OPTIMIZADA: Obras con detalles completos
-- Obtiene todas las obras con sus detalles en 1 sola query
-- File: sql/01_obras/obtener_obras_con_detalles_completos.sql

SELECT
    o.id AS obra_id,
    o.codigo AS obra_codigo,
    o.nombre AS obra_nombre,
    o.descripcion AS obra_descripcion,
    o.estado AS obra_estado,
    o.fecha_inicio,
    o.fecha_fin_estimada,
    o.presupuesto,

    -- Detalles de materiales
    od.id AS detalle_id,
    od.material_id,
    od.cantidad_requerida,
    od.cantidad_instalada,
    od.precio_unitario,
    (od.cantidad_requerida * od.precio_unitario) AS costo_material,

    -- Información del material (join adicional)
    m.codigo AS material_codigo,
    m.nombre AS material_nombre,
    m.unidad_medida,
    m.stock_actual

FROM obras o
LEFT JOIN obra_detalles od ON o.id = od.obra_id
LEFT JOIN materiales m ON od.material_id = m.id
WHERE o.activo = 1
ORDER BY o.codigo, od.id;
```

---

## 🔧 CÓMO APLICAR EN TU CÓDIGO

### **Paso 1: Crear archivo SQL**

```bash
# Crear SQL externo optimizado
# File: sql/01_obras/obtener_obras_con_detalles_completos.sql
```

### **Paso 2: Usar el SQL optimizado**

```python
# En rexus/modules/01_obras/model.py

def obtener_obras_con_detalles_optimizado(self):
    """✅ Obtiene obras con detalles - 1 query optimizada"""

    # Usar SQL externo con JOIN
    sql_file = 'sql/01_obras/obtener_obras_con_detalles_completos.sql'
    query = self.sql_manager.get_query('obras', 'obtener_obras_con_detalles_completos')

    cursor = self.db_connection.cursor()
    cursor.execute(query)
    filas = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    # Agrupar por obra (procesamiento en memoria)
    obras_agrupadas = {}
    for fila in filas:
        obra_id = fila[0]

        if obra_id not in obras_agrupadas:
            obras_agrupadas[obra_id] = {
                'id': fila[0],
                'codigo': fila[1],
                'nombre': fila[2],
                'descripcion': fila[3],
                'estado': fila[4],
                'detalles': []
            }

        # Agregar detalle si existe
        if fila[5] is not None:  # detalle_id
            obras_agrupadas[obra_id]['detalles'].append({
                'id': fila[5],
                'material_id': fila[6],
                'cantidad_requerida': fila[7],
                'cantidad_instalada': fila[8],
                'costo_material': fila[10],
                'material_codigo': fila[11],
                'material_nombre': fila[12]
            })

    return list(obras_agrupadas.values())
```

---

## 📊 MÉTRICAS DE MEJORA

### **Antes (N+1):**
- Queries: 1 + N
- Para 100 obras: **101 queries**
- Tiempo: ~10 segundos
- Uso de BD: **100%**

### **Después (JOIN):**
- Queries: **1**
- Para 100 obras: **1 query**
- Tiempo: **~200ms**
- Uso de BD: **10%** del original

**MEJORA: 50-100x más rápido** 🚀
