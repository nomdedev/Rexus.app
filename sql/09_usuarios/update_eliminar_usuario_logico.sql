-- Eliminar usuario (soft delete)
-- Parámetros: :usuario_id
-- Retorna: filas afectadas

UPDATE usuarios
SET activo = 0, 
    updated_at = GETDATE()
WHERE id = :usuario_id;