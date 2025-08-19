UPDATE users SET
    ultimo_login = GETDATE(),
    fecha_actualizacion = GETDATE()
WHERE id = ?;