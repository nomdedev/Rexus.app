SELECT COUNT(*) as total_empleados, SUM(salario) as total_salarios
FROM empleados
WHERE departamento_id = ? AND estado = 'ACTIVO';
