-- Inserción segura de nuevo vidrio
-- Reemplaza f-string en crear_vidrio()
-- Parámetros: codigo, descripcion, tipo, espesor, proveedor, precio_m2, color, tratamiento, dimensiones_disponibles, estado, observaciones

INSERT INTO [vidrios]
(codigo, descripcion, tipo, espesor, proveedor, precio_m2, 
 color, tratamiento, dimensiones_disponibles, estado, observaciones, fecha_actualizacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE());