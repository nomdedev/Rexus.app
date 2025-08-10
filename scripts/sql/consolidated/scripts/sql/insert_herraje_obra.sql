-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: insert_herraje_obra.sql
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

INSERT INTO productos_obra (herraje_id, obra_id, cantidad_requerida, fecha_asignacion, observaciones)
VALUES (@herraje_id, @obra_id, @cantidad_requerida, GETDATE(), @observaciones);
