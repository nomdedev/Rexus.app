-- Cuenta el total de vidrios activos
SELECT COUNT(*) as total
FROM vidrios v
WHERE v.activo = 1;
