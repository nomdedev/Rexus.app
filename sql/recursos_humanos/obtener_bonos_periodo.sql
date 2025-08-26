-- Obtener total de bonos para un empleado en un período
SELECT SUM(monto) FROM bonos_descuentos 
WHERE empleado_id = ? AND mes_aplicacion = ? AND anio_aplicacion = ?
AND tipo = 'BONO' AND estado = 'APLICADO'
