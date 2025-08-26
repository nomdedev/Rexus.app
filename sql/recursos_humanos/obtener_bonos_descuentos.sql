-- Obtener bonos y descuentos de empleados
SELECT b.id,
       b.empleado_id,
       CONCAT(e.nombre, ' ', e.apellido) as empleado,
       b.tipo, 
       b.concepto, 
       b.monto, 
       b.fecha_aplicacion,
       b.mes_aplicacion, 
       b.anio_aplicacion, 
       b.estado, 
       b.observaciones
FROM bonos_descuentos b
JOIN empleados e ON b.empleado_id = e.id
WHERE {{WHERE_CONDITIONS}}
ORDER BY b.fecha_aplicacion DESC
