-- Obtener valoración total del inventario
-- Parámetros: filtros dinámicos según condiciones WHERE
-- Retorna: total_productos, total_unidades, valor_total

SELECT
    COUNT(*) as total_productos,
    SUM(stock_actual) as total_unidades,
    SUM(stock_actual * precio_unitario) as valor_total
FROM inventario
WHERE activo = 1
  AND (:categoria IS NULL OR categoria = :categoria)
  AND (:filtro_nombre IS NULL OR nombre LIKE :filtro_nombre)
  AND (:stock_minimo IS NULL OR stock_actual >= :stock_minimo);