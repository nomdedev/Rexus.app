UPDATE vidrios
SET activo = 0,
    fecha_modificacion = GETDATE()
WHERE id = %(vidrio_id)s;