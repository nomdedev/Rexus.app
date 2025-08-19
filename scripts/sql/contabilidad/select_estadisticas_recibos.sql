SELECT COUNT(*), SUM(monto)
FROM recibos
WHERE estado = 'EMITIDO'