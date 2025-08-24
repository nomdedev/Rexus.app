-- Registrar pago de obra
INSERT INTO [{tabla_pagos_obras}] 
(fecha_pago, monto, descripcion, obra_id, empleado_id, numero_recibo) 
VALUES (?, ?, ?, ?, ?, ?)
