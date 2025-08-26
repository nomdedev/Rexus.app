# -*- coding: utf-8 -*-
"""
Reportes Manager - Generación de reportes y estadísticas del inventario
Refactorizado de InventarioModel para mejor mantenibilidad

Responsabilidades:
- Generación de reportes de inventario
- Estadísticas de movimientos y stock
- Análisis de tendencias y patrones
- Reportes de productos críticos
- Exportación de datos en diferentes formatos
- Dashboards y métricas KPI
"""

import logging
import csv
import json
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

# Imports del sistema de cache
try:
from rexus.utils.report_cache_integration import (
cache_inventory_report,
get_report_cache_manager,
get_performance_monitor
)
CACHE_AVAILABLE = True
except ImportError:
CACHE_AVAILABLE = False
import logging
logger = logging.getLogger(__name__)
logger.warning("No se pudo importar la integración de cache de reportes.")

# Dummy decorator to avoid NameError if cache_inventory_report is not available
def cache_inventory_report(*args, **kwargs):
        def decorator(func):
        return func
return decorator

# Dummy get_performance_monitor to avoid NameError
def get_performance_monitor():
        # Returns an object with a log_report_execution method
class DummyMonitor:
        @staticmethod
def log_report_execution(*args, **kwargs):
                # Método vacío porque en el entorno sin integración de cache
# no es necesario registrar la ejecución de reportes.
pass
return DummyMonitor()

# Dummy get_report_cache_manager to avoid NameError
def get_report_cache_manager():
        # Returns an object with the same interface as the real ReportCacheManager
return type("ReportCacheManager", (), {
"invalidate_report_type": staticmethod(lambda *args, **kwargs: 0),
"invalidate_module_cache": staticmethod(lambda *args, **kwargs: 0)
})()

# Configurar logging
logger = logging.getLogger(__name__)


class ReportesManager:
"""Gestor de reportes y estadísticas para el módulo de inventario."""

def __init__(self, db_connection=None):
        """Inicializa el gestor de reportes.

Args:
        db_connection: Conexión a la base de datos
"""
self.db_connection = db_connection
self.tabla_inventario = "inventario"
self.tabla_movimientos = "movimientos_inventario"
self.tabla_categorias = "categorias"

@cache_inventory_report('stock', ttl=1800) if CACHE_AVAILABLE else lambda f: f
def generar_reporte_stock(self, filtros: Optional[Dict] = None) -> Dict[str, Any]:
        """Genera reporte completo de stock actual.

Args:
        filtros: Filtros opcionales para el reporte

Returns:
        Dict con productos y resumen del reporte
"""
start_time = time.time() if CACHE_AVAILABLE else None

try:
        if not self.db_connection:
                return {
'success': False,
'error': 'Sin conexión a base de datos'
}

cursor = self.db_connection.cursor()

# Query base
query = """
SELECT 
i.id,
i.codigo,
i.descripcion,
i.categoria,
i.stock,
i.precio_unitario,
i.stock_minimo,
i.stock_maximo,
i.activo,
(i.stock * i.precio_unitario) as valor_total
FROM inventario i
WHERE i.activo = 1
"""

params = []

# Aplicar filtros
if filtros:
                if filtros.get('categoria'):
                query += " AND i.categoria = ?"
params.append(filtros['categoria'])

if filtros.get('stock_minimo') is not None:
                query += " AND i.stock >= ?"
params.append(filtros['stock_minimo'])

if filtros.get('solo_bajo_minimo'):
                query += " AND i.stock < i.stock_minimo"

query += " ORDER BY i.codigo"

cursor.execute(query, params)
productos = []

for row in cursor.fetchall():
                producto = {
'id': row[0],
'codigo': row[1],
'descripcion': row[2],
'categoria': row[3],
'stock': row[4],
'precio_unitario': float(row[5]) if row[5] else 0.0,
'stock_minimo': row[6] or 0,
'stock_maximo': row[7] or 0,
'activo': bool(row[8]),
'valor_total': float(row[9]) if row[9] else 0.0
}
productos.append(producto)

# Calcular resumen
total_productos = len(productos)
valor_total = sum(p['valor_total'] for p in productos)
productos_bajo_minimo = len([p for p in productos if p['stock'] < p['stock_minimo']])
productos_sin_stock = len([p for p in productos if p['stock'] == 0])

resumen = {
'total_productos': total_productos,
'valor_total': valor_total,
'productos_bajo_minimo': productos_bajo_minimo,
'productos_sin_stock': productos_sin_stock,
'fecha_generacion': datetime.now().isoformat()
}

# Log de rendimiento si está disponible
if CACHE_AVAILABLE and start_time:
                execution_time = time.time() - start_time
monitor = get_performance_monitor()
monitor.log_report_execution(
'Reporte de Stock', execution_time, False, 
len(str(productos))
)

return {
'success': True,
'productos': productos,
'resumen': resumen
}

except Exception as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}

@cache_inventory_report('movimientos', ttl=900) if CACHE_AVAILABLE else lambda f: f
def generar_reporte_movimientos(
self, 
fecha_inicio: Optional[datetime] = None, 
fecha_fin: Optional[datetime] = None
) -> Dict[str, Any]:
        """Genera reporte de movimientos de inventario.

Args:
        fecha_inicio: Fecha de inicio del período
fecha_fin: Fecha de fin del período

Returns:
        Dict con movimientos y estadísticas
"""
start_time = time.time() if CACHE_AVAILABLE else None

try:
        if not self.db_connection:
                return {
'success': False,
'error': 'Sin conexión a base de datos'
}

# Validar fechas
if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
                return {
'success': False,
'error': 'Fecha de inicio no puede ser posterior a fecha de fin'
}

cursor = self.db_connection.cursor()

# Si no se especifican fechas, usar último mes
if not fecha_inicio:
                fecha_inicio = datetime.now() - timedelta(days=30)
if not fecha_fin:
                fecha_fin = datetime.now()

query = """
SELECT 
m.id,
m.producto_id,
i.codigo,
i.descripcion,
m.tipo,
m.cantidad,
m.fecha,
m.costo_unitario,
m.observaciones
FROM movimientos_inventario m
JOIN inventario i ON m.producto_id = i.id
WHERE m.fecha BETWEEN ? AND ?
ORDER BY m.fecha DESC
"""

cursor.execute(query, [fecha_inicio, fecha_fin])
movimientos = []

total_entradas = 0
total_salidas = 0

for row in cursor.fetchall():
                movimiento = {
'id': row[0],
'producto_id': row[1],
'codigo': row[2],
'descripcion': row[3],
'tipo': row[4],
'cantidad': row[5],
'fecha': row[6],
'costo_unitario': float(row[7]) if row[7] else 0.0,
'observaciones': row[8] or ''
}
movimientos.append(movimiento)

if movimiento['tipo'] == 'ENTRADA':
                total_entradas += movimiento['cantidad']
elif movimiento['tipo'] == 'SALIDA':
                total_salidas += movimiento['cantidad']

estadisticas = {
'total_movimientos': len(movimientos),
'total_entradas': total_entradas,
'total_salidas': total_salidas,
'fecha_inicio': fecha_inicio.isoformat(),
'fecha_fin': fecha_fin.isoformat()
}

return {
'success': True,
'movimientos': movimientos,
'estadisticas': estadisticas
}

except Exception as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}

def generar_analisis_abc_simple(self) -> Dict[str, Any]:
        """Genera análisis ABC simple de productos por valor y demanda.

Returns:
        Dict con clasificación ABC
"""
try:
        if not self.db_connection:
                return {
'success': False,
'error': 'Sin conexión a base de datos'
}

cursor = self.db_connection.cursor()

# Obtener productos con valor y demanda
query = """
SELECT 
i.codigo,
i.descripcion,
i.stock,
i.precio_unitario,
(i.stock * i.precio_unitario) as valor_total,
COALESCE(SUM(CASE WHEN m.tipo = 'SALIDA' THEN m.cantidad ELSE 0 END), 0) as demanda_anual
FROM inventario i
LEFT JOIN movimientos_inventario m ON i.id = m.producto_id 
AND m.fecha >= date('now', '-1 year')
WHERE i.activo = 1
GROUP BY i.id, i.codigo, i.descripcion, i.stock, i.precio_unitario
ORDER BY valor_total DESC, demanda_anual DESC
"""

cursor.execute(query)
productos = []

for row in cursor.fetchall():
                producto = {
'codigo': row[0],
'descripcion': row[1],
'stock': row[2],
'precio_unitario': float(row[3]) if row[3] else 0.0,
'valor_total': float(row[4]) if row[4] else 0.0,
'demanda_anual': row[5] or 0
}
productos.append(producto)

# Clasificación ABC (80-15-5)
total_productos = len(productos)
if total_productos == 0:
                return {
'success': True,
'clasificacion': {
'productos_a': [],
'productos_b': [],
'productos_c': []
}
}

# Calcular puntos de corte
corte_a = int(total_productos * 0.8)  # 80%
corte_b = int(total_productos * 0.95)  # 80% + 15% = 95%

clasificacion = {
'productos_a': productos[:corte_a],
'productos_b': productos[corte_a:corte_b],
'productos_c': productos[corte_b:]
}

return {
'success': True,
'clasificacion': clasificacion,
'resumen': {
'total_productos': total_productos,
'productos_a_count': len(clasificacion['productos_a']),
'productos_b_count': len(clasificacion['productos_b']),
'productos_c_count': len(clasificacion['productos_c'])
}
}

except Exception as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}

def calcular_valoracion_inventario(self) -> Dict[str, Any]:
        """Calcula valoración total del inventario.

Returns:
        Dict con valoración detallada
"""
try:
        if not self.db_connection:
                return {
'success': False,
'error': 'Sin conexión a base de datos'
}

cursor = self.db_connection.cursor()

# Valoración por categoría
query = """
SELECT 
i.categoria,
COUNT(*) as cantidad_productos,
SUM(i.stock * i.precio_unitario) as valor_categoria,
AVG(i.precio_unitario) as precio_promedio
FROM inventario i
WHERE i.activo = 1 AND i.stock > 0
GROUP BY i.categoria
ORDER BY valor_categoria DESC
"""

cursor.execute(query)
valor_por_categoria = []
valor_total = 0

for row in cursor.fetchall():
                categoria = {
'categoria': row[0] or 'Sin Categoría',
'cantidad_productos': row[1],
'valor_categoria': float(row[2]) if row[2] else 0.0,
'precio_promedio': float(row[3]) if row[3] else 0.0
}
valor_por_categoria.append(categoria)
valor_total += categoria['valor_categoria']

# Productos sin stock
cursor.execute("""
SELECT COUNT(*) 
FROM inventario 
WHERE activo = 1 AND stock = 0
""")
productos_sin_stock = cursor.fetchone()[0] or 0

return {
'success': True,
'valor_total': valor_total,
'valor_por_categoria': valor_por_categoria,
'productos_sin_stock': productos_sin_stock,
'fecha_valoracion': datetime.now().isoformat()
}

except Exception as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}

def generar_kpis_dashboard(self) -> Dict[str, Any]:
        """Genera KPIs principales para dashboard.

Returns:
        Dict con métricas clave
"""
try:
        if not self.db_connection:
                return {
'success': False,
'error': 'Sin conexión a base de datos'
}

cursor = self.db_connection.cursor()
kpis = {}

# Total productos activos
cursor.execute("SELECT COUNT(*) FROM inventario WHERE activo = 1")
kpis['total_productos'] = cursor.fetchone()[0] or 0

# Productos bajo stock mínimo
cursor.execute("""
SELECT COUNT(*) FROM inventario 
WHERE activo = 1 AND stock < stock_minimo
""")
kpis['productos_bajo_minimo'] = cursor.fetchone()[0] or 0

# Valor total inventario
cursor.execute("""
SELECT SUM(stock * precio_unitario) 
FROM inventario 
WHERE activo = 1
""")
valor_result = cursor.fetchone()[0]
kpis['valor_total_inventario'] = float(valor_result) if valor_result else 0.0

# Movimientos del mes actual
primer_dia_mes = datetime.now().replace(day=1)
cursor.execute("""
SELECT COUNT(*) FROM movimientos_inventario 
WHERE fecha >= ?
""", [primer_dia_mes])
kpis['movimientos_mes_actual'] = cursor.fetchone()[0] or 0

return {
'success': True,
**kpis
}

except Exception as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}

def exportar_reporte_csv(self, datos: List[Dict], archivo_destino: str) -> Dict[str, Any]:
        """Exporta datos a archivo CSV.

Args:
        datos: Lista de diccionarios con datos
archivo_destino: Ruta del archivo destino

Returns:
        Dict con resultado de la exportación
"""
try:
        if not datos:
                return {
'success': False,
'error': 'No hay datos para exportar'
}

with open(archivo_destino, 'w', newline='', encoding='utf-8') as csvfile:
                if datos:
                fieldnames = datos[0].keys()
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

writer.writeheader()
for row in datos:
                        writer.writerow(row)

return {
'success': True,
'archivo': archivo_destino,
'registros_exportados': len(datos)
}

except (FileNotFoundError, PermissionError) as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}
except Exception as e:
        return {
'success': False,
'error': f"Error inesperado: {str(e)}"
}

def exportar_reporte_json(self, datos: Dict, archivo_destino: str) -> Dict[str, Any]:
        """Exporta datos a archivo JSON.

Args:
        datos: Diccionario con datos
archivo_destino: Ruta del archivo destino

Returns:
        Dict con resultado de la exportación
"""
try:
        with open(archivo_destino, 'w', encoding='utf-8') as jsonfile:
                json.dump(datos, jsonfile, indent=2, ensure_ascii=False, default=str)

return {
'success': True,
'archivo': archivo_destino
}

except (FileNotFoundError, PermissionError) as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}
except Exception as e:
        return {
'success': False,
'error': f"Error inesperado: {str(e)}"
}

@cache_inventory_report('productos_sin_movimientos', ttl=3600) if CACHE_AVAILABLE else lambda f: f
def generar_reporte_productos_sin_movimientos(self, dias: int = 30) -> Dict[str, Any]:
        """Genera reporte de productos sin movimientos en período.

Args:
        dias: Número de días hacia atrás para verificar

Returns:
        Dict con productos sin movimientos
"""
start_time = time.time() if CACHE_AVAILABLE else None

try:
        if not self.db_connection:
                return {
'success': False,
'error': 'Sin conexión a base de datos'
}

cursor = self.db_connection.cursor()
fecha_limite = datetime.now() - timedelta(days=dias)

query = """
SELECT 
i.id,
i.codigo,
i.descripcion,
i.stock,
MAX(m.fecha) as ultimo_movimiento
FROM inventario i
LEFT JOIN movimientos_inventario m ON i.id = m.producto_id
WHERE i.activo = 1
GROUP BY i.id, i.codigo, i.descripcion, i.stock
HAVING (ultimo_movimiento IS NULL OR ultimo_movimiento < ?)
ORDER BY i.codigo
"""

cursor.execute(query, [fecha_limite])
productos = []

for row in cursor.fetchall():
                producto = {
'id': row[0],
'codigo': row[1],
'descripcion': row[2],
'stock': row[3],
'ultimo_movimiento': row[4]
}
productos.append(producto)

return {
'success': True,
'productos': productos,
'parametros': {
'dias_analisis': dias,
'fecha_limite': fecha_limite.isoformat()
}
}

except Exception as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}

def calcular_tendencias_stock(self, producto_id: int) -> Dict[str, Any]:
        """Calcula tendencias de stock para un producto.

Args:
        producto_id: ID del producto

Returns:
        Dict con análisis de tendencias
"""
try:
        if not self.db_connection:
                return {
'success': False,
'error': 'Sin conexión a base de datos'
}

cursor = self.db_connection.cursor()

# Obtener historial de stock (simulado con movimientos)
query = """
SELECT 
DATE(m.fecha) as fecha,
AVG(
CASE WHEN m.tipo = 'ENTRADA' THEN m.cantidad 
WHEN m.tipo = 'SALIDA' THEN -m.cantidad 
ELSE 0 END
) as cambio_promedio
FROM movimientos_inventario m
WHERE m.producto_id = ?
AND m.fecha >= date('now', '-3 months')
GROUP BY DATE(m.fecha)
ORDER BY fecha
"""

cursor.execute(query, [producto_id])
datos_historicos = []

for row in cursor.fetchall():
                datos_historicos.append({
'fecha': row[0],
'cambio_promedio': float(row[1]) if row[1] else 0.0
})

if len(datos_historicos) < 2:
                return {
'success': True,
'tendencia': 0,
'proyeccion': 'Datos insuficientes',
'confidence': 'low'
}

# Calcular tendencia simple (diferencia promedio)
cambios = [d['cambio_promedio'] for d in datos_historicos]
tendencia = sum(cambios) / len(cambios) if cambios else 0

# Proyección básica
if tendencia > 0:
                proyeccion = 'Crecimiento'
elif tendencia < 0:
                proyeccion = 'Decrecimiento'
else:
                proyeccion = 'Estable'

return {
'success': True,
'tendencia': tendencia,
'proyeccion': proyeccion,
'datos_historicos': datos_historicos,
'confidence': 'medium' if len(datos_historicos) > 10 else 'low'
}

except Exception as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}

# Nuevas funciones con cache inteligente
@cache_inventory_report('analisis_abc', ttl=7200) if CACHE_AVAILABLE else lambda f: f
def generar_analisis_abc(self, tipo_analisis: str = 'valor') -> Dict[str, Any]:
        """Genera análisis ABC de productos por valor o cantidad.

Args:
        tipo_analisis: 'valor' o 'cantidad' o 'rotacion'

Returns:
        Dict con clasificación ABC de productos
"""
start_time = time.time() if CACHE_AVAILABLE else None

try:
        if not self.db_connection:
                return {
'success': False,
'error': 'Sin conexión a base de datos'
}

cursor = self.db_connection.cursor()

# Query base según tipo de análisis
if tipo_analisis == 'valor':
                query = """
SELECT 
i.id,
i.codigo,
i.descripcion,
i.stock,
i.precio_unitario,
(i.stock * i.precio_unitario) as valor_total,
COALESCE(
(SELECT SUM(ABS(m.cantidad)) 
FROM movimientos_inventario m 
WHERE m.producto_id = i.id 
AND m.fecha >= date('now', '-12 months')), 
0
) as movimientos_anuales
FROM inventario i
WHERE i.activo = 1
ORDER BY valor_total DESC
"""
campo_ordenamiento = 'valor_total'
elif tipo_analisis == 'cantidad':
                query = """
SELECT 
i.id,
i.codigo,
i.descripcion,
i.stock,
i.precio_unitario,
(i.stock * i.precio_unitario) as valor_total,
i.stock as cantidad_stock
FROM inventario i
WHERE i.activo = 1
ORDER BY cantidad_stock DESC
"""
campo_ordenamiento = 'cantidad_stock'
else:  # rotacion
query = """
SELECT 
i.id,
i.codigo,
i.descripcion,
i.stock,
i.precio_unitario,
(i.stock * i.precio_unitario) as valor_total,
COALESCE(
(SELECT SUM(ABS(m.cantidad)) 
FROM movimientos_inventario m 
WHERE m.producto_id = i.id 
AND m.fecha >= date('now', '-12 months')), 
0
) / CASE WHEN i.stock > 0 THEN i.stock ELSE 1 END as rotacion
FROM inventario i
WHERE i.activo = 1
ORDER BY rotacion DESC
"""
campo_ordenamiento = 'rotacion'

cursor.execute(query)
productos_raw = cursor.fetchall()

# Procesar productos
productos = []
for row in productos_raw:
                producto = {
'id': row[0],
'codigo': row[1],
'descripcion': row[2],
'stock': row[3],
'precio_unitario': float(row[4]) if row[4] else 0.0,
'valor_total': float(row[5]) if row[5] else 0.0,
'metrica_abc': float(row[6]) if row[6] else 0.0
}
productos.append(producto)

# Calcular acumulados y clasificar
total_metrica = sum(p['metrica_abc'] for p in productos)
acumulado = 0

for i, producto in enumerate(productos):
                acumulado += producto['metrica_abc']
porcentaje_acumulado = (acumulado / total_metrica * 100) if total_metrica > 0 else 0

# Clasificación ABC
if porcentaje_acumulado <= 80:
                categoria = 'A'
elif porcentaje_acumulado <= 95:
                categoria = 'B'
else:
                categoria = 'C'

producto['categoria_abc'] = categoria
producto['porcentaje_acumulado'] = round(porcentaje_acumulado, 2)
producto['ranking'] = i + 1

# Resumen por categorías
categorias_resumen = {
'A': {'productos': 0, 'valor_total': 0.0, 'porcentaje_productos': 0.0},
'B': {'productos': 0, 'valor_total': 0.0, 'porcentaje_productos': 0.0},
'C': {'productos': 0, 'valor_total': 0.0, 'porcentaje_productos': 0.0}
}

for producto in productos:
                categoria = producto['categoria_abc']
categorias_resumen[categoria]['productos'] += 1
categorias_resumen[categoria]['valor_total'] += producto['metrica_abc']

total_productos = len(productos)
for categoria in categorias_resumen:
                if total_productos > 0:
                categorias_resumen[categoria]['porcentaje_productos'] = round(
(categorias_resumen[categoria]['productos'] / total_productos) * 100, 2
)

# Log de rendimiento
if CACHE_AVAILABLE and start_time:
                execution_time = time.time() - start_time
monitor = get_performance_monitor()
monitor.log_report_execution(
f'Análisis ABC - {tipo_analisis}', execution_time, False,
len(str(productos))
)

return {
'success': True,
'tipo_analisis': tipo_analisis,
'productos': productos,
'resumen_categorias': categorias_resumen,
'total_productos': total_productos,
'fecha_generacion': datetime.now().isoformat()
}

except Exception as e:
        return {
'success': False,
'error': f"Error interno: {str(e)}"
}

def invalidar_cache_reportes(self, tipo_reporte: Optional[str] = None):
        """Invalidar cache de reportes específicos o todos.

Args:
        tipo_reporte: Tipo específico a invalidar o None para todos
"""
if not CACHE_AVAILABLE:
        return

try:
        manager = get_report_cache_manager()

if tipo_reporte:
                invalidated = manager.invalidate_report_type(f'inventario_{tipo_reporte}')
else:
                invalidated = manager.invalidate_module_cache('inventario')

logger.info(f"Cache invalidado: {invalidated} entradas")

except Exception as e:
        logger.error(f"Error al invalidar cache: {str(e)}")

def _generar_recomendaciones_cache(self, stats: Dict) -> List[str]:
        """Generar recomendaciones basadas en estadísticas de cache."""
recomendaciones = []

hit_ratio = stats.get('hit_ratio', 0)
memory_usage = stats.get('memory_usage_percent', 0)

if hit_ratio < 0.5:
        recomendaciones.append("Hit ratio bajo (<50%). Considera aumentar TTL de reportes frecuentes.")

if memory_usage > 80:
        recomendaciones.append("Uso de memoria alto (>80%). Considera reducir tamaño máximo de cache.")

if stats.get('evictions', 0) > stats.get('writes', 0) * 0.1:
        recomendaciones.append("Muchas evictions. Considera aumentar memoria disponible para cache.")

if hit_ratio > 0.8:
        recomendaciones.append("Excelente rendimiento de cache. Sistema optimizado.")

return recomendaciones