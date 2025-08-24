SELECT e.id, e.codigo, e.nombre, e.apellido, e.documento, e.email,
e.telefono, e.departamento_id, d.nombre as departamento,
e.cargo, e.salario, e.fecha_ingreso, e.estado
FROM [empleados] e
LEFT JOIN [departamentos] d ON e.departamento_id = d.id
WHERE e.estado = 'ACTIVO'
ORDER BY e.nombre, e.apellido
