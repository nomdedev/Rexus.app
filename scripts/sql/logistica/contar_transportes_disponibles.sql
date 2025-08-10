-- scripts/sql/logistica/contar_transportes_disponibles.sql
-- Cuenta todos los transportes activos y disponibles en el sistema
-- Sin parámetros

SELECT COUNT(*) as transportes_disponibles
FROM [transportes] 
WHERE activo = 1 AND disponible = 1;
