UPDATE [{tabla_equipos}]
SET nombre = ?, tipo = ?, modelo = ?, marca = ?, numero_serie = ?,
    fecha_adquisicion = ?, fecha_instalacion = ?, ubicacion = ?,
    estado = ?, valor_adquisicion = ?, vida_util_anos = ?,
    observaciones = ?, fecha_modificacion = GETDATE()
WHERE id = ?