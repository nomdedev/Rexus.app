-- select_saldo_pago_material.sql
-- Obtiene el saldo de un pago de material
-- Parámetros: ? (pago_id)

SELECT total, monto_pagado, saldo_pendiente
FROM pagos_materiales
WHERE id = ?