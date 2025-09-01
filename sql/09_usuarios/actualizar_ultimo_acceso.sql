UPDATE [usuarios]
SET
    intentos_fallidos = 0,
    ultimo_acceso = GETDATE(),
    fecha_modificacion = GETDATE()
WHERE id = ?;