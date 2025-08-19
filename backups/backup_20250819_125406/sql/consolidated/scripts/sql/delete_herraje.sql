UPDATE productos SET
    activo = 0,
    estado = 'INACTIVO',
    fecha_actualizacion = GETDATE()
WHERE id = @id; AND categoria = \'HERRAJE\'