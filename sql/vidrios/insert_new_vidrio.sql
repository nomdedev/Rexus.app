-- Insertar nuevo vidrio
INSERT INTO vidrios
(tipo, especificaciones, espesor, proveedor, precio_m2, color, 
 propiedades, activo, dimensiones, fecha_creacion, usuario_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, GETDATE(), ?);
