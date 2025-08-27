-- Obtener estadísticas detalladas por categoría
-- Parámetros: filtros dinámicos según condiciones WHERE
-- Retorna: categoria, productos, unidades, valor por categoría

SELECT
    categoria,
    COUNT(*) as productos,
    SUM(stock_actual) as unidades,
    SUM(stock_actual * precio_unitario) as valor
FROM inventario
WHERE activo = 1
  AND (:categoria IS NULL OR categoria = :categoria)
  AND (:filtro_nombre IS NULL OR nombre LIKE :filtro_nombre)
  AND (:stock_minimo IS NULL OR stock_actual >= :stock_minimo)
GROUP BY categoria
ORDER BY valor DESC;