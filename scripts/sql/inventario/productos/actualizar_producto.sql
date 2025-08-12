-- Actualizar producto existente
-- Archivo: actualizar_producto.sql
-- Módulo: Inventario/Productos
-- Descripción: Actualiza datos de producto (sin stock)

UPDATE [inventario]
SET 
    descripcion = @descripcion,
    categoria = @categoria,
    unidad_medida = @unidad_medida,
    precio_compra = @precio_compra,
    precio_venta = @precio_venta,
    stock_minimo = @stock_minimo,
    ubicacion = @ubicacion,
    observaciones = @observaciones,
    usuario_modificador = @usuario_modificador,
    fecha_modificacion = GETDATE()
WHERE id = @producto_id AND activo = 1;

-- Ejemplo de uso en Python:
-- cursor.execute(query, params_dict)
-- affected_rows = cursor.rowcount
