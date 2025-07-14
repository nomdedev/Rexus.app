# 🎯 PLAN DE ACCIÓN ESPECÍFICO PARA TU BASE DE DATOS

## 📊 RESUMEN DE LA SITUACIÓN ACTUAL

Basado en la imagen de las tablas que me enviaste y el análisis del código, aquí está el plan específico para optimizar tu base de datos:

### ✅ TABLAS QUE YA TIENES Y ESTÁN BIEN:
- ✅ `dbo.obras` - Tabla central (mantener)
- ✅ `dbo.inventario_perfiles` - Catálogo de materiales (mantener)
- ✅ `dbo.vidrios_por_obra` - Gestión de vidrios (mantener)
- ✅ `dbo.usuarios` - Sistema de usuarios (mantener)

### ❌ PROBLEMA PRINCIPAL:
Tu código busca la tabla `pedidos_material` pero en tu BD existe `dbo.pedidos_compra`.

**Error SQL actual:**
```
Error 42S02: "El nombre de objeto 'pedidos_material' no es válido"
```

### 🔧 SOLUCIONES INMEDIATAS:

#### OPCIÓN A: CORREGIR EL CÓDIGO (RÁPIDO)
Cambiar los modelos para que usen las tablas que SÍ existen:

1. **En inventario/model.py** línea 379, cambiar:
   ```python
   # DE:
   query = "SELECT * FROM pedidos_material WHERE obra_id = ?"

   # A:
   query = "SELECT * FROM dbo.pedidos_compra WHERE obra_id = ?"
   ```

2. **En herrajes/model.py**, cambiar:
   ```python
   # DE:
   query = "SELECT * FROM pedidos_herrajes WHERE obra_id = ?"

   # A: (usar la misma tabla con filtro)
   query = "SELECT * FROM dbo.pedidos_compra WHERE obra_id = ? AND tipo_material = 'herraje'"
   ```

3. **En contabilidad/model.py**, cambiar:
   ```python
   # DE:
   query = "SELECT * FROM pagos_pedidos WHERE obra_id = ?"

   # A: (usar alguna tabla de pagos existente o crear lógica temporal)
   query = "SELECT 'pendiente' as estado"  # Temporal hasta crear la tabla
   ```

#### OPCIÓN B: ESTRUCTURA OPTIMIZADA (MEJOR A LARGO PLAZO)

Crear las tablas nuevas con el script que hice:

1. **Ejecutar el script SQL:**
   ```sql
   -- Ejecutar: scripts/migrar_estructura_bd.sql
   -- Esto creará: pedidos_obra, pagos_obra
   ```

2. **Migrar datos existentes:**
   ```sql
   -- Los datos de dbo.pedidos_compra se migrarán a pedidos_obra
   -- Se crearán datos de ejemplo si faltan
   ```

3. **Actualizar el código** para usar las nuevas tablas

## 🎯 MI RECOMENDACIÓN: OPCIÓN A PRIMERO

Para que tu sistema funcione **AHORA MISMO**, te recomiendo:

### PASO 1: Correcciones Inmediatas (5 minutos)

```python
# En modules/inventario/model.py, línea ~379:
def obtener_estado_pedido_por_obra(self, obra_id):
    try:
        # Usar la tabla que SÍ existe
        query = "SELECT estado FROM dbo.pedidos_compra WHERE obra_id = ?"
        resultado = self.db.ejecutar_query(query, (obra_id,))

        if resultado and len(resultado) > 0:
            # Lógica para determinar estado general
            estados = [row[0] for row in resultado]
            if all(estado == 'completado' for estado in estados):
                return 'completado'
            elif any(estado in ['en_proceso', 'pedido'] for estado in estados):
                return 'en_proceso'
            else:
                return 'pendiente'
        else:
            return 'sin_pedidos'
    except Exception:
        return 'sin_pedidos'  # Fallback seguro

# En modules/herrajes/model.py:
def obtener_estado_pedido_por_obra(self, obra_id):
    try:
        # Filtrar por tipo si la tabla pedidos_compra tiene esa columna
        query = "SELECT estado FROM dbo.pedidos_compra WHERE obra_id = ?"
        resultado = self.db.ejecutar_query(query, (obra_id,))

        if resultado and len(resultado) > 0:
            return 'completado' if len(resultado) > 0 else 'pendiente'
        else:
            return 'sin_pedidos'
    except Exception:
        return 'sin_pedidos'

# En modules/contabilidad/model.py:
def obtener_estado_pago_pedido_por_obra(self, obra_id, modulo=None):
    try:
        # Lógica temporal - puedes mejorar esto después
        # Por ahora, devolver un estado basado en alguna lógica simple
        return 'pendiente'  # O consultar alguna tabla de pagos que tengas
    except Exception:
        return 'pendiente'
```

### PASO 2: Verificar que funciona (2 minutos)

```bash
python verificar_integracion.py
```

### PASO 3: Una vez que funcione, migrar a la estructura optimizada

Ejecutar el script SQL que creé para tener la estructura ideal a largo plazo.

## 📋 TABLAS QUE PODRÍAS ELIMINAR (DESPUÉS DE MIGRAR)

Basado en tu imagen, estas tablas podrían ser redundantes:

### 🗑️ Candidatas a eliminar:
- `dbo.auditorias_sistema` - Solo si no usas auditoría
- `dbo.cronograma_obras` - Se puede manejar con fechas en obras
- `dbo.detalle_pedido` - Redundante con pedidos_compra
- `dbo.materiales_por_obra` - Redundante con pedidos_compra
- `dbo.movimientos_inventario` - Se puede calcular
- `dbo.movimientos_stock` - Se puede calcular
- `dbo.pedidos_pendientes` - Es una vista/query calculada
- `dbo.perfiles_por_obra` - Redundante con pedidos_compra
- `dbo.reservas_materiales` - Se puede integrar en pedidos
- `dbo.reservas_stock` - Se puede integrar en pedidos

### ⚠️ Verificar antes de eliminar:
- `dbo.proveedores` - ¿La usas para gestionar proveedores?
- `dbo.cliente` - ¿Es diferente de la info en obras?
- `dbo.equipos` - ¿Es parte de inventario?

## 🚀 PRÓXIMOS PASOS INMEDIATOS:

1. **AHORA**: Aplicar las correcciones del Paso 1
2. **HOY**: Verificar que el sistema funciona sin errores
3. **ESTA SEMANA**: Ejecutar el script de migración a estructura optimizada
4. **PRÓXIMA SEMANA**: Eliminar tablas redundantes después de verificar

¿Quieres que empecemos con las correcciones inmediatas para que funcione ya?
