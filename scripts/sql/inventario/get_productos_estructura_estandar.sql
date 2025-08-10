-- 🔒 Obtener productos con estructura estándar desde inventario_perfiles
-- Reemplaza f-string vulnerable por consulta parametrizada
SELECT 
    id, 
    codigo, 
    descripcion, 
    tipo as categoria, 
    acabado as subcategoria, 
    stock_actual, 
    stock_minimo, 
    0 as stock_maximo, 
    importe as precio_unitario, 
    importe as precio_promedio, 
    ubicacion, 
    proveedor, 
    unidad as unidad_medida, 
    'ACTIVO' as estado, 
    GETDATE() as fecha_creacion, 
    GETDATE() as fecha_modificacion, 
    '' as observaciones, 
    qr as codigo_qr,
    stock_actual as stock_disponible, 
    0 as stock_reservado
FROM inventario_perfiles
WHERE (@search IS NULL 
    OR codigo LIKE '%' + @search + '%' 
    OR descripcion LIKE '%' + @search + '%'
    OR tipo LIKE '%' + @search + '%')
    AND (@categoria IS NULL OR tipo = @categoria)
    AND (@activo IS NULL OR 1 = @activo)
ORDER BY codigo;
