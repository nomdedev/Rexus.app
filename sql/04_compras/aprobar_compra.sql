UPDATE compras
SET estado = 'APROBADA',
    observaciones = ISNULL(observaciones, '') + ' [APROBADA POR: ' + ? + ']'
WHERE id = ?