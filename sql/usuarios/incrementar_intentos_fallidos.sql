-- Incrementar intentos fallidos de usuario
-- Archivo: incrementar_intentos_fallidos.sql
-- Módulo: Usuarios
-- Descripción: Incrementa contador de intentos fallidos y bloquea si es necesario

UPDATE [usuarios] 
SET 
    intentos_fallidos = intentos_fallidos + 1,
    bloqueado_hasta = CASE 
        WHEN intentos_fallidos + 1 >= @max_intentos 
        THEN DATEADD(MINUTE, @minutos_bloqueo, GETDATE())
        ELSE bloqueado_hasta 
    END,
    fecha_modificacion = GETDATE()
WHERE LOWER(usuario) = LOWER(@username) AND activo = 1;

-- Ejemplo de uso en Python:
-- params = {
--     'username': username,
--     'max_intentos': 5,
--     'minutos_bloqueo': 30
-- }
-- cursor.execute(query, params)
