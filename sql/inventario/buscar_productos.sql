-- Búsqueda avanzada de productos
-- Parámetros: :termino_busqueda, :categoria, :proveedor, :activo
-- Retorna: Productos que coinciden con la búsqueda

SELECT 
    ip.id,
    ip.codigo,
    ip.nombre,
    ip.descripcion,
    ip.categoria,
    ip.proveedor,
    ip.precio_unitario,
    ip.stock_actual,
    ip.stock_minimo,
    ip.unidad_medida,
    CASE 
        WHEN ip.nombre LIKE '%' + :termino_busqueda + '%' THEN 1
        WHEN ip.codigo LIKE '%' + :termino_busqueda + '%' THEN 2
        WHEN ip.descripcion LIKE '%' + :termino_busqueda + '%' THEN 3
        ELSE 4
    END as relevancia
FROM inventario_perfiles ip
WHERE ip.activo = ISNULL(:activo, 1)
  AND (
    ip.nombre LIKE '%' + :termino_busqueda + '%' OR
    ip.codigo LIKE '%' + :termino_busqueda + '%' OR
    ip.descripcion LIKE '%' + :termino_busqueda + '%'
  )
  AND (:categoria IS NULL OR ip.categoria = :categoria)
  AND (:proveedor IS NULL OR ip.proveedor LIKE '%' + :proveedor + '%')
ORDER BY relevancia, ip.nombre;