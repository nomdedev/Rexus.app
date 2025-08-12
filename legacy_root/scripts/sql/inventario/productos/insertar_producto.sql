-- Insertar nuevo producto
-- Archivo: insertar_producto.sql
-- Módulo: Inventario/Productos
-- Descripción: Crea un nuevo producto con validación

INSERT INTO [inventario] (
    codigo,
    descripcion,
    categoria,
    unidad_medida,
    precio_compra,
    precio_venta,
    stock_actual,
    stock_minimo,
    ubicacion,
    observaciones,
    qr_data,
    usuario_creador,
    fecha_creacion,
    fecha_modificacion,
    activo
) VALUES (
    @codigo,
    @descripcion,
    @categoria,
    @unidad_medida,
    @precio_compra,
    @precio_venta,
    @stock_actual,
    @stock_minimo,
    @ubicacion,
    @observaciones,
    @qr_data,
    @usuario_creador,
    GETDATE(),
    GETDATE(),
    1
);

-- Ejemplo de uso en Python:
-- cursor.execute(query, params_dict)
-- cursor.execute("SELECT @@IDENTITY")
