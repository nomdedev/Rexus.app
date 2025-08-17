-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: insert_herraje.sql
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

-- Script seguro para insertar un herraje
-- Uso: Ejecutar desde backend con parámetros seguros

INSERT INTO productos (
    codigo, descripcion, tipo, proveedor, precio_unitario, unidad_medida,
    categoria, estado, stock_minimo, stock_actual, observaciones,
    especificaciones, marca, modelo, color, material, dimensiones, peso
) VALUES (
    @codigo, @descripcion, @tipo, @proveedor, @precio_unitario, @unidad_medida,
    @categoria, @estado, @stock_minimo, @stock_actual, @observaciones,
    @especificaciones, @marca, @modelo, @color, @material, @dimensiones, @peso
);
