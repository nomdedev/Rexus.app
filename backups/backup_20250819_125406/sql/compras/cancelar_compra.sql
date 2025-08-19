UPDATE compras
SET estado = 'CANCELADA',
    observaciones = ISNULL(observaciones, '') + ' [CANCELADA: ' + ? + ']'
WHERE id = ?