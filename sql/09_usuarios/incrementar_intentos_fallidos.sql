UPDATE [usuarios]
SET
    intentos_fallidos = intentos_fallidos + 1,
    bloqueado_hasta = CASE
        WHEN intentos_fallidos + 1 >= 5
        THEN DATEADD(MINUTE, 30, GETDATE())
        ELSE bloqueado_hasta
    END,
    fecha_modificacion = GETDATE()
WHERE id = ?;