-- Script seguro para actualizar un herraje
-- Uso: Ejecutar desde backend con parámetros seguros

UPDATE herrajes SET
    descripcion = @descripcion,
    tipo = @tipo,
    proveedor = @proveedor,
    precio_unitario = @precio_unitario,
    unidad_medida = @unidad_medida,
    categoria = @categoria,
    estado = @estado,
    stock_minimo = @stock_minimo,
    stock_actual = @stock_actual,
    observaciones = @observaciones,
    especificaciones = @especificaciones,
    marca = @marca,
    modelo = @modelo,
    color = @color,
    material = @material,
    dimensiones = @dimensiones,
    peso = @peso,
    fecha_actualizacion = GETDATE()
WHERE id = @id;
