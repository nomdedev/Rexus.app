-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: update_stock_herraje.sql
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

UPDATE productos SET
    stock_actual = @nuevo_stock,
    fecha_actualizacion = GETDATE()
WHERE id = @herraje_id;

UPDATE productos SET
    stock_actual = @nuevo_stock,
    fecha_ultima_entrada = CASE WHEN @tipo_movimiento IN ('ENTRADA', 'AJUSTE') THEN GETDATE() ELSE fecha_ultima_entrada END,
    fecha_ultima_salida = CASE WHEN @tipo_movimiento = 'SALIDA' THEN GETDATE() ELSE fecha_ultima_salida END
WHERE herraje_id = @herraje_id;
