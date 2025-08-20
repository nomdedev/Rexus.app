-- Eliminar usuario de forma lógica (SQLite)
-- Parámetros: :usuario_id
-- Retorna: Actualiza el estado del usuario a inactivo

UPDATE usuarios
SET 
    activo = 0, 
    estado = 'INACTIVO', 
    fecha_modificacion = datetime('now')
WHERE id = :usuario_id;