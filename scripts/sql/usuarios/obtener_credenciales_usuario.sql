-- Obtener username y password de un usuario activo
SELECT username, password FROM usuarios WHERE id = ? AND activo = 1