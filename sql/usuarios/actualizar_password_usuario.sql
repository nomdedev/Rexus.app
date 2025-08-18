-- Actualizar contraseña y resetear intentos fallidos
UPDATE usuarios
SET password_hash = ?, intentos_fallidos = 0, bloqueado_hasta = NULL
WHERE id = ?