-- Crear herraje completo con todos los campos
-- Parámetros: :codigo, :nombre, :descripcion, :categoria, :proveedor, :precio_unitario, :stock_actual, :stock_minimo, :unidad_medida, :activo
-- Retorna: ID del herraje creado

INSERT INTO herrajes (
    codigo, nombre, descripcion, categoria, proveedor,
    precio_unitario, stock_actual, stock_minimo, unidad_medida, activo
) VALUES (:codigo, :nombre, :descripcion, :categoria, :proveedor,
          :precio_unitario, :stock_actual, :stock_minimo, :unidad_medida, :activo);