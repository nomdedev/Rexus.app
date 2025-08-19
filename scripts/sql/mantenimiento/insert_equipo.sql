INSERT INTO [{tabla_equipos}]
(codigo, nombre, tipo, modelo, marca, numero_serie,
 fecha_adquisicion, fecha_instalacion, ubicacion, estado,
 valor_adquisicion, vida_util_anos, observaciones,
 activo, fecha_creacion, fecha_modificacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE())