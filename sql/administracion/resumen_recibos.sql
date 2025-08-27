SELECT
COUNT(*) as total_recibos,
SUM(monto) as total_monto,
SUM(CASE WHEN impreso = 1 THEN 1 ELSE 0 END) as recibos_impresos
FROM recibos
WHERE estado = 'EMITIDO';
