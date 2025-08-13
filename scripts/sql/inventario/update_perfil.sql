-- Actualizar perfil de inventario
UPDATE inventario_perfiles 
SET descripcion = ?, 
    tipo = ?, 
    precio_unitario = ?, 
    stock_actual = ?, 
    stock_minimo = ?, 
    ubicacion = ?,
    fecha_modificacion = GETDATE()
WHERE id = ?