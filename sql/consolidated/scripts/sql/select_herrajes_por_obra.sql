-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: select_herrajes_por_obra.sql
-- Actualizado: 2025-07-30 19:21:23
-- 
-- CAMBIOS REALIZADOS:
-- - Tablas actualizadas a estructura consolidada
-- - Columnas mapeadas a nuevos nombres
-- - Filtros de categoría agregados donde corresponde
-- 
-- TABLAS CONSOLIDADAS UTILIZADAS:
-- - productos (reemplaza inventario_perfiles, herrajes, vidrios, materiales)
-- - movimientos_inventario (reemplaza movimientos_stock, historial_*)
-- - pedidos_consolidado (reemplaza pedidos, pedidos_herrajes, pedidos_vidrios)
-- - productos_obra (reemplaza *_obra tables)
-- =====================================================

-- Script seguro para obtener productos por obra
-- Uso: Ejecutar desde backend con parámetro obra_id seguro

SELECT
    h.id, h.codigo, h.descripcion, h.proveedor, h.precio_unitario,
    h.unidad_medida, ho.cantidad_requerida, ho.cantidad_pedida,
    ho.fecha_asignacion, ho.observaciones as obs_obra
FROM productos h
INNER JOIN productos_obra ho ON h.id = ho.herraje_id
WHERE ho.obra_id = ?
ORDER BY h.codigo;
