-- Actualizar un herraje existente por código
-- Parámetros:
--   :nombre (requerido)
--   :descripcion (requerido)
--   :categoria (requerido)
--   :proveedor (requerido)
--   :precio_unitario (requerido)
--   :stock_actual (requerido)
--   :stock_minimo (requerido)
--   :unidad_medida (requerido)
--   :activo (requerido)
--   :codigo (requerido) - Código del herraje a actualizar
-- Retorna: Filas actualizadas

UPDATE herrajes SET
    nombre = :nombre,
    descripcion = :descripcion,
    categoria = :categoria,
    proveedor = :proveedor,
    precio_unitario = :precio_unitario,
    stock_actual = :stock_actual,
    stock_minimo = :stock_minimo,
    unidad_medida = :unidad_medida,
    activo = :activo,
    fecha_actualizacion = GETDATE()
WHERE codigo = :codigo;
