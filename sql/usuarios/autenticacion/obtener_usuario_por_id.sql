-- Obtener datos de usuario por ID para cambio de contraseña
-- Parámetros: user_id

SELECT username, password 
FROM usuarios 
WHERE id = ? AND activo = 1