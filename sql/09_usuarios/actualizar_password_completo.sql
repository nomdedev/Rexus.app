-- Actualizar contraseña de usuario y resetear intentos fallidos (SQLite)
-- Parámetros: :password_hash, :usuario_id
-- Retorna: Actualiza la contraseña y resetea el bloqueo

UPDATE usuarios
SET 
    password_hash = :password_hash, 
    intentos_fallidos = 0, 
    bloqueado_hasta = NULL,
    fecha_modificacion = datetime('now')
WHERE id = :usuario_id;