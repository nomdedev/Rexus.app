-- Contar herrajes con stock bajo (igual o menor al mínimo)
-- Parámetros: Ninguno
-- Retorna: COUNT(*) de herrajes con stock bajo

SELECT COUNT(*) FROM herrajes
WHERE activo = 1
  AND stock_actual <= stock_minimo;
