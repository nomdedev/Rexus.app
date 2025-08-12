-- Actualizar último acceso exitoso y resetear intentos fallidos
-- Archivo: actualizar_acceso_exitoso.sql

UPDATE usuarios 
SET intentos_fallidos = 0, 
    ultimo_acceso = GETDATE() 
WHERE LOWER(username) = ?;
