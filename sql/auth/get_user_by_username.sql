-- Obtener datos de usuario por nombre
SELECT id, usuario, password_hash, salt, rol, activo
FROM usuarios 
WHERE usuario = ? AND activo = 1
