-- Obtener libro contable con filtros
SELECT 
    lc.numero_asiento,
    lc.fecha_asiento,
    lc.descripcion,
    lc.cuenta,
    lc.debe,
    lc.haber,
    lc.saldo,
    e.nombre + ' ' + e.apellido AS empleado
FROM [{tabla_libro_contable}] lc
LEFT JOIN [{tabla_empleados}] e ON lc.empleado_id = e.id
WHERE 1=1
