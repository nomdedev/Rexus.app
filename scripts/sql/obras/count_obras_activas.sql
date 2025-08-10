-- 🔒 Conteo total de obras activas
-- Reemplaza SQL embebido por consulta parametrizada
SELECT COUNT(*) as total_obras
FROM obras 
WHERE activo = 1;
