-- Obtener stock total de herrajes activos
-- Parámetros: Ninguno
-- Retorna: Suma de stock_actual (o 0 si es NULL)

SELECT COALESCE(SUM(stock_actual), 0) FROM herrajes WHERE activo = 1;
