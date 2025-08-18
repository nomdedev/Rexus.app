-- Contar intentos de login fallidos recientes
-- Parámetros: username, fecha_limite

SELECT COUNT(*) FROM intentos_login
WHERE username = ? AND exitoso = 0 AND fecha_intento > ?