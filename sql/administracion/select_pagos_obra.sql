-- Obtener pagos de obra con filtros
SELECT 
    po.id,
    po.fecha_pago,
    po.monto,
    po.descripcion,
    po.obra_id,
    po.numero_recibo,
    e.nombre + ' ' + e.apellido AS empleado
FROM [{tabla_pagos_obras}] po
LEFT JOIN [{tabla_empleados}] e ON po.empleado_id = e.id
WHERE 1=1
