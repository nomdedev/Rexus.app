-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: select_herraje_por_id.sql
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

-- Script seguro para obtener un herraje por ID
-- Uso: Ejecutar desde backend con parámetro seguro

SELECT h.*, i.stock_actual, i.stock_reservado, i.ubicacion, i.fecha_ultima_entrada, i.fecha_ultima_salida
FROM productos h
LEFT JOIN productos i ON h.id = i.herraje_id
WHERE h.id = @id AND h.estado = 'ACTIVO'; AND categoria = \'HERRAJE\'
