INSERT INTO [vidrios]
(codigo, descripcion, tipo, espesor, proveedor, precio_m2,
 color, tratamiento, dimensiones_disponibles, estado, observaciones, fecha_actualizacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE());