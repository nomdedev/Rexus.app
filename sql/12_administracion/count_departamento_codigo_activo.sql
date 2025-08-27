-- Contar departamentos por código que estén activos
-- Parámetros: :codigo

SELECT COUNT(*) as total
FROM departamentos 
WHERE codigo = :codigo 
  AND estado = 'ACTIVO';