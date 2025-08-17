-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: buscar_herrajes.sql
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

SELECT id, codigo, descripcion, proveedor, precio_unitario, unidad_medida, subcategoria, estado
FROM productos
WHERE (codigo LIKE @termino OR descripcion LIKE @termino OR proveedor LIKE @termino)
  AND categoria = 'HERRAJE'
  AND estado = 'ACTIVO'
ORDER BY codigo;
