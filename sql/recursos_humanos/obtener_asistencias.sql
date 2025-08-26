SELECT a.id,
a.empleado_id,
CONCAT(e.nombre, ' ', e.apellido) as empleado,
a.fecha, a.hora_entrada, a.hora_salida, a.horas_trabajadas,
a.horas_extra, a.tipo, a.observaciones
FROM asistencias a
JOIN empleados e ON a.empleado_id = e.id
WHERE 1=1
ORDER BY a.fecha DESC, a.hora_entrada
