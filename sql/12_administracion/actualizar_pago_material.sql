UPDATE pagos_materiales
SET monto_pagado = ?, saldo_pendiente = ?, estado_pago = ?,
fecha_pago = ?, fecha_actualizacion = GETDATE(),
usuario_actualizacion = ?
WHERE id = ?;
