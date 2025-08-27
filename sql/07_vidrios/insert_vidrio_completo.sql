-- Inserta un nuevo vidrio en la tabla vidrios
INSERT INTO vidrios (
    tipo, grosor, ancho, alto, color, precio_unitario, 
    stock_actual, stock_minimo, activo, fecha_creacion
) VALUES (
    @tipo, @grosor, @ancho, @alto, @color, @precio_unitario, 
    @stock_actual, @stock_minimo, 1, @fecha_creacion
)
