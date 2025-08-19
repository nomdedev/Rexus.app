-- Script para crear un nuevo herraje
-- Parámetros: :codigo, :nombre, :descripcion, :categoria, :proveedor, :precio_unitario, :stock_minimo, :unidad_medida, :especificaciones
-- Retorna: ID del herraje creado

INSERT INTO herrajes (
    codigo,
    nombre,
    descripcion,
    categoria,
    proveedor,
    precio_unitario,
    stock_actual,
    stock_minimo,
    unidad_medida,
    especificaciones,
    activo,
    fecha_creacion,
    estado
)
VALUES (
    :codigo,
    :nombre,
    :descripcion,
    :categoria,
    :proveedor,
    :precio_unitario,
    0, -- Stock inicial en 0
    ISNULL(:stock_minimo, 5),
    ISNULL(:unidad_medida, 'unidad'),
    :especificaciones,
    1,
    GETDATE(),
    'Activo'
);

SELECT SCOPE_IDENTITY() as nuevo_herraje_id;