-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: insert_pedido_obra.sql
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

-- Script seguro para crear pedido de productos para una obra
-- Uso: Ejecutar desde backend con parámetros seguros

INSERT INTO pedidos_consolidado (
    obra_id, proveedor, fecha_pedido, estado, total_estimado
) VALUES (
    @obra_id, @proveedor, GETDATE(), 'PENDIENTE', @total_estimado
);
