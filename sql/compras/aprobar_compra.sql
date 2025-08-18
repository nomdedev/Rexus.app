-- Aprobar compra con usuario
UPDATE compras
SET estado = 'APROBADA',
    observaciones = CONCAT(ISNULL(observaciones, ''), ' [APROBADA POR: ', ?, ']')
WHERE id = ?