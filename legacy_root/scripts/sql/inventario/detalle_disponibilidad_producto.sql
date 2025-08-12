-- 🔒 Detalle de disponibilidad de producto específico
-- Reemplaza concatenación vulnerable por consulta parametrizada
SELECT 
    stock_actual, 
    stock_minimo, 
    precio_unitario
FROM inventario_perfiles
WHERE id = @producto_id;
