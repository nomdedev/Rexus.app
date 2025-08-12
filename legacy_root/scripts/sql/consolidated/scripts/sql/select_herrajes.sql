-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: select_herrajes.sql
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

-- Script seguro para obtener productos con filtros parametrizados
-- Uso: Debe ejecutarse desde el backend con parámetros seguros

SELECT
    id, codigo, descripcion, proveedor, precio_unitario,
    unidad_medida, subcategoria, estado, observaciones,
    fecha_actualizacion
FROM productos
WHERE categoria = 'HERRAJE' AND activo = 1
    -- Filtros opcionales
    -- AND proveedor LIKE ?
    -- AND codigo LIKE ?
    -- AND descripcion LIKE ?
ORDER BY codigo;
