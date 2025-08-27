-- update_pago_material.sql
-- Actualiza un pago de material
-- Parámetros: ? (monto_pagado), ? (saldo_pendiente), ? (estado_pago), ? (fecha_pago), ? (usuario_actualizacion), ? (pago_id)

UPDATE pagos_materiales
SET monto_pagado = ?, saldo_pendiente = ?, estado_pago = ?,
    fecha_pago = ?, fecha_actualizacion = GETDATE(),
    usuario_actualizacion = ?
WHERE id = ?