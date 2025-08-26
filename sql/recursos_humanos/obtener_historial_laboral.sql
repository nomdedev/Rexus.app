-- Obtener historial laboral de empleados
SELECT h.id,
       h.empleado_id,
       CONCAT(e.nombre, ' ', e.apellido) as empleado,
       h.tipo, 
       h.descripcion, 
       h.fecha, 
       h.valor_anterior,
       h.valor_nuevo, 
       h.usuario_creacion
FROM historial_laboral h
JOIN empleados e ON h.empleado_id = e.id
WHERE {{WHERE_CONDITIONS}}
ORDER BY h.fecha DESC
