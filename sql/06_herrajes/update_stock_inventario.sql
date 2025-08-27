-- Actualizar stock de herraje en inventario
-- Parámetros: :stock_actual, :herraje_id
-- Retorna: filas afectadas

UPDATE herrajes_inventario
SET stock_actual = :stock_actual
WHERE herraje_id = :herraje_id;