-- Obtiene el stock actual, mínimo y máximo de un producto por ID
SELECT stock_actual, stock_minimo, stock_maximo FROM productos WHERE id = ?