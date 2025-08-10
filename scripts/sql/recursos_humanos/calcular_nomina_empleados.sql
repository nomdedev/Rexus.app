SELECT e.id, e.nombre, e.apellido, e.salario_base, e.cargo,
       d.nombre as departamento
FROM empleados e
LEFT JOIN departamentos d ON e.departamento_id = d.id
WHERE e.activo = 1 AND e.estado = 'ACTIVO'