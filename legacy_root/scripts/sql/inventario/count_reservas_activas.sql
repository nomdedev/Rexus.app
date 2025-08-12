-- 🔒 Conteo de reservas activas
-- Reemplaza concatenación vulnerable por consulta parametrizada
SELECT COUNT(*) as total_reservas_activas
FROM reserva_materiales 
WHERE estado = 'ACTIVA';
