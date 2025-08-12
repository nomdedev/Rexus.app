SELECT d.nombre, COUNT(e.id) as cantidad
FROM empleados e
LEFT JOIN departamentos d ON e.departamento_id = d.id
WHERE e.activo = 1
GROUP BY d.nombre