-- 🔒 Suma total de presupuesto de obras activas
-- Reemplaza SQL embebido por consulta parametrizada
SELECT SUM(presupuesto_total) as total_presupuesto
FROM obras 
WHERE activo = 1;
