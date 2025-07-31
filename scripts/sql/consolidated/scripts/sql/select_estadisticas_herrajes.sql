-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: select_estadisticas_herrajes.sql
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

SELECT COUNT(*) as total_herrajes FROM productos WHERE estado = 'ACTIVO';
SELECT COUNT(DISTINCT proveedor) as proveedores_activos FROM productos WHERE estado = 'ACTIVO';
SELECT SUM(precio_unitario) as valor_total_inventario FROM productos WHERE estado = 'ACTIVO';
SELECT proveedor, COUNT(*) as cantidad FROM productos WHERE estado = 'ACTIVO' GROUP BY proveedor ORDER BY cantidad DESC;
