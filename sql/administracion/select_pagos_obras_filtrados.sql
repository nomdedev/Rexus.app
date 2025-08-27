-- select_pagos_obras_filtrados.sql
-- Query base para obtener pagos de obras (filtros se agregan dinámicamente)
-- Sin parámetros base

SELECT po.id, po.obra_id, po.concepto, po.categoria, po.monto,
       po.fecha_pago, po.proveedor_id, po.empleado_id, po.recibo_id,
       po.metodo_pago, po.numero_comprobante, po.estado, po.observaciones,
       po.fecha_creacion, po.usuario_creacion
FROM pagos_obras po