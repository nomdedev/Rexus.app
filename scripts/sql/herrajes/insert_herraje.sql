-- Script seguro para insertar un herraje
-- Uso: Ejecutar desde backend con parámetros seguros

INSERT INTO herrajes (
    codigo, descripcion, tipo, proveedor, precio_unitario, unidad_medida,
    categoria, estado, stock_minimo, stock_actual, observaciones,
    especificaciones, marca, modelo, color, material, dimensiones, peso
) VALUES (
    @codigo, @descripcion, @tipo, @proveedor, @precio_unitario, @unidad_medida,
    @categoria, @estado, @stock_minimo, @stock_actual, @observaciones,
    @especificaciones, @marca, @modelo, @color, @material, @dimensiones, @peso
);
