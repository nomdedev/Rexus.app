-- Insertar nuevo vidrio
INSERT INTO vidrios
(tipo, especificaciones, espesor, proveedor, precio_m2,
 color, propiedades, estado, dimensiones, fecha_creacion,
 usuario_creacion, activo)
VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVO', ?, GETDATE(), ?, 1);
