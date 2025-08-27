-- insert_producto.sql
-- Inserta un nuevo producto en la tabla productos unificada
-- Parámetros: todos los campos del producto (28 parámetros)

INSERT INTO productos (
    codigo, nombre, descripcion, tipo_producto, categoria, subcategoria,
    precio_compra, precio_venta, margen_ganancia, stock, stock_minimo, stock_maximo,
    unidad_medida, proveedor_id, proveedor_codigo, codigo_barras,
    especificaciones_tecnicas, tipo_herraje, acabado, material,
    densidad, peso_unitario, estado, requiere_inspeccion,
    ubicacion_almacen, pasillo, estante, usuario_creacion, fecha_creacion
) VALUES (
    ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, GETDATE()
)