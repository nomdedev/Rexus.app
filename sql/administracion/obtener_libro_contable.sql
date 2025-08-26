SELECT lc.id, lc.numero_asiento, lc.fecha_asiento, lc.tipo_asiento,
lc.concepto, lc.referencia, lc.obra_id, lc.proveedor_id,
lc.empleado_id, lc.departamento_id, d.nombre as departamento,
lc.cuenta_contable, lc.debe, lc.haber, lc.saldo, lc.estado,
lc.observaciones, lc.fecha_creacion, lc.usuario_creacion
FROM libro_contable lc
LEFT JOIN departamentos d ON lc.departamento_id = d.id
WHERE 1=1
ORDER BY lc.fecha_asiento DESC, lc.numero_asiento
