-- Actualizar contraseña de usuario
-- Parámetros: password_hash, user_id

UPDATE usuarios
SET password = ?, updated_at = GETDATE()
WHERE id = ? AND activo = 1