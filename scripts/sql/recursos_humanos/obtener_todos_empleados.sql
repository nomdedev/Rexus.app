SELECT 
    e.id, e.codigo, e.nombre, e.apellido, e.dni, e.telefono,
    e.email, e.direccion, e.fecha_nacimiento, e.fecha_ingreso,
    e.salario_base, e.cargo, e.estado, d.nombre as departamento,
    e.fecha_creacion, e.fecha_modificacion
FROM empleados e
LEFT JOIN departamentos d ON e.departamento_id = d.id
WHERE e.activo = 1
ORDER BY e.apellido, e.nombre