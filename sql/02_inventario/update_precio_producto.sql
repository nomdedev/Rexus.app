-- Actualizar precio de un producto en inventario
-- Parámetros: :precio_nuevo, :usuario, :producto_id

UPDATE inventario
SET precio_unitario = :precio_nuevo,
    fecha_modificacion = GETDATE(),
    usuario_modificacion = :usuario
WHERE id = :producto_id;