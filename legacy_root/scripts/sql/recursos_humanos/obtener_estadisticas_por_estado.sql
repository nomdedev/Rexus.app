SELECT estado, COUNT(*) as cantidad
FROM empleados
WHERE activo = 1
GROUP BY estado