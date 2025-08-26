-- Script para crear un nuevo producto en inventario
-- Parámetros: :codigo, :nombre, :descripcion, :categoria, :unidad_medida, :precio_unitario, :stock_minimo, :proveedor
-- Retorna: ID del producto creado

INSERT INTO inventario_perfiles (
    codigo,
    nombre,
    descripcion,
    categoria,
    unidad_medida,
    precio_unitario,
    stock_actual,
    stock_minimo,
    proveedor,
    activo,
    fecha_creacion
)
VALUES (
    :codigo,
    :nombre,
    :descripcion,
    :categoria,
    :unidad_medida,
    :precio_unitario,
    0, -- Stock inicial en 0
    ISNULL(:stock_minimo, 10),
    :proveedor,
    1,
    GETDATE()
);

SELECT SCOPE_IDENTITY() as nuevo_producto_id;