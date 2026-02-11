-- Crear un nuevo herraje
-- Parámetros:
--   :codigo (requerido)
--   :nombre (requerido)
--   :descripcion (requerido)
--   :categoria (requerido)
--   :proveedor (requerido)
--   :precio_unitario (requerido)
--   :stock_actual (requerido)
--   :stock_minimo (requerido)
--   :unidad_medida (requerido)
--   :activo (requerido)
-- Retorna: Nuevo registro creado

INSERT INTO herrajes (
    codigo, nombre, descripcion, categoria, proveedor,
    precio_unitario, stock_actual, stock_minimo, unidad_medida, activo
) VALUES (
    :codigo, :nombre, :descripcion, :categoria, :proveedor,
    :precio_unitario, :stock_actual, :stock_minimo, :unidad_medida, :activo
);
