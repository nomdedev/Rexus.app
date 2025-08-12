-- Resetear intentos fallidos de autenticación
-- Archivo: resetear_intentos_fallidos.sql

UPDATE usuarios 
SET intentos_fallidos = 0 
WHERE LOWER(username) = ?;
