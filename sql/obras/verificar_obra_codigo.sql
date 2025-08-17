-- 🔒 Verificar existencia de obra por código
-- Reemplaza SQL embebido por consulta parametrizada
SELECT codigo 
FROM obras 
WHERE id = @obra_id 
    AND activo = 1;
