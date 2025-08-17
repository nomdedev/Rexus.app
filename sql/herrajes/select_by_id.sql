-- Consulta segura para obtener un herraje por ID
-- Utiliza la tabla consolidada 'productos' filtrada por categoría 'HERRAJE'
-- El parámetro ID se debe pasar usando prepared statements

SELECT 
    id, codigo, descripcion, categoria, subcategoria, tipo,
    stock_actual, stock_minimo, stock_maximo, stock_reservado, stock_disponible,
    precio_unitario, precio_promedio, costo_unitario, unidad_medida,
    ubicacion, color, material, marca, modelo, acabado,
    proveedor, codigo_proveedor, tiempo_entrega_dias,
    observaciones, codigo_qr, imagen_url, propiedades_especiales,
    estado, activo, fecha_creacion, fecha_actualizacion
FROM productos 
WHERE id = ? AND categoria = 'HERRAJE' AND activo = 1;