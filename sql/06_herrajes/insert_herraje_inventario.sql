-- Insertar stock de herraje en inventario
-- Parámetros: :herraje_id, :stock_actual
-- Retorna: ID del registro insertado

INSERT INTO herrajes_inventario (herraje_id, stock_actual)
VALUES (:herraje_id, :stock_actual);