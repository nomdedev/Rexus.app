-- 🔒 Conteo de obras con reservas activas
-- Reemplaza concatenación vulnerable por consulta parametrizada
SELECT COUNT(DISTINCT obra_id) as obras_con_reservas
FROM reserva_materiales
WHERE estado = 'ACTIVA';
