UPDATE usuarios
SET password = ?, updated_at = GETDATE()
WHERE id = ? AND activo = 1