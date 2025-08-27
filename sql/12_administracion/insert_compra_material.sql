-- Registrar compra de material
INSERT INTO [{tabla_pagos_materiales}] 
(fecha_compra, material, cantidad, precio_unitario, total, proveedor, empleado_id, obra_id) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
