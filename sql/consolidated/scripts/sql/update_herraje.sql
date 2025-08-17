-- =====================================================
-- SCRIPT CONSOLIDADO - Rexus.app v2.0.0
-- =====================================================
-- Script original: update_herraje.sql
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

-- Script seguro para actualizar un herraje
-- Uso: Ejecutar desde backend con parámetros seguros

UPDATE productos SET
    descripcion = @descripcion,
    tipo = @tipo,
    proveedor = @proveedor,
    precio_unitario = @precio_unitario,
    unidad_medida = @unidad_medida,
    categoria = @categoria,
    estado = @estado,
    stock_minimo = @stock_minimo,
    stock_actual = @stock_actual,
    observaciones = @observaciones,
    especificaciones = @especificaciones,
    marca = @marca,
    modelo = @modelo,
    color = @color,
    material = @material,
    dimensiones = @dimensiones,
    peso = @peso,
    fecha_actualizacion = GETDATE()
WHERE id = @id; AND categoria = \'HERRAJE\'
