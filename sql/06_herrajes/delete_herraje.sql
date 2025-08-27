UPDATE herrajes SET
    activo = 0,
    estado = 'INACTIVO',
    fecha_actualizacion = GETDATE()
WHERE id = @id;