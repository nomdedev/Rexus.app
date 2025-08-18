-- Cancelar compra con motivo
UPDATE compras
SET estado = 'CANCELADA',
    observaciones = CONCAT(ISNULL(observaciones, ''), ' [CANCELADA: ', ?, ']')
WHERE id = ?