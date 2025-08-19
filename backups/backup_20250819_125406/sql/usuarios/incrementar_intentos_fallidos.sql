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