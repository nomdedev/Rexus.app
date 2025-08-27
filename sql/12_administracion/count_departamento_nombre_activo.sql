-- Contar departamentos por nombre que estén activos
-- Parámetros: :nombre

SELECT COUNT(*) as total
FROM departamentos 
WHERE nombre = :nombre 
  AND estado = 'ACTIVO';