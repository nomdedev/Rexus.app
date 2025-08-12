-- Actualización segura del último login del usuario
-- Utiliza la tabla 'users'
-- Los parámetros se deben pasar usando prepared statements

UPDATE users SET
    ultimo_login = GETDATE(),
    fecha_actualizacion = GETDATE()
WHERE id = ?;