-- Actualizar último login de usuario
UPDATE usuarios 
SET ultima_conexion = CURRENT_TIMESTAMP
WHERE id = ?
