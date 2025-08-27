-- Cambiar rol de usuario
-- Parámetros: :nuevo_rol, :usuario_id
-- Retorna: filas afectadas

UPDATE usuarios
SET rol = :nuevo_rol, 
    updated_at = GETDATE()
WHERE id = :usuario_id AND activo = 1;