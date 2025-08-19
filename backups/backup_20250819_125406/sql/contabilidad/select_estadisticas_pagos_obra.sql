SELECT COUNT(*), SUM(monto)
FROM pagos_obra
WHERE estado = 'PAGADO'