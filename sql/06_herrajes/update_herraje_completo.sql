-- Actualizar herraje completo con fecha de actualización automática
-- Parámetros: :nombre, :descripcion, :categoria, :proveedor, :precio_unitario, :stock_actual, :stock_minimo, :unidad_medida, :activo, :codigo
-- Retorna: filas afectadas

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