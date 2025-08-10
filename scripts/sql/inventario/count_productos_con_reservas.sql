-- 🔒 Conteo de productos con reservas activas
-- Reemplaza concatenación vulnerable por consulta parametrizada
SELECT COUNT(DISTINCT producto_id) as productos_con_reservas
FROM reserva_materiales
WHERE estado = 'ACTIVA';
