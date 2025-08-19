UPDATE usuarios
SET intentos_fallidos = 0
WHERE LOWER(username) = ?;