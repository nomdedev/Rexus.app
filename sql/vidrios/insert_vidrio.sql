INSERT INTO vidrios 
(tipo, especificaciones, espesor, proveedor, precio_m2, 
 color, propiedades, dimensiones_disponibles, estado,
 dimensiones, fecha_creacion, fecha_modificacion)
VALUES (@tipo, @especificaciones, @espesor, @proveedor, @precio_m2, 
        @color, @propiedades, @dimensiones_disponibles, @estado,
        @dimensiones, GETDATE(), GETDATE())