-- scripts/sql/logistica/contar_transportes_activos.sql
-- Cuenta todos los transportes activos en el sistema
-- Sin parámetros

SELECT COUNT(*) as total_transportes
FROM [transportes] 
WHERE activo = 1;
