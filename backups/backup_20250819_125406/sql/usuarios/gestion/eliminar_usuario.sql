UPDATE usuarios
SET activo = 0,
    fecha_modificacion = CURRENT_TIMESTAMP
WHERE id = %(user_id)s;