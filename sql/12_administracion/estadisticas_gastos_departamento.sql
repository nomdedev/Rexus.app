SELECT
COUNT(*) as total_gastos,
SUM(haber) as total_monto
FROM libro_contable
WHERE departamento_id = ? AND estado = 'ACTIVO';
