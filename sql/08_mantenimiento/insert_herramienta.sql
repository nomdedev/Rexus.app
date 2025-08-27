INSERT INTO [{tabla_herramientas}]
(codigo, nombre, tipo, marca, modelo, numero_serie,
 fecha_adquisicion, ubicacion, estado, valor_adquisicion,
 vida_util_anos, observaciones, activo, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE())