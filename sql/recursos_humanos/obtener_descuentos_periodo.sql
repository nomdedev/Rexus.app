-- Obtener total de descuentos para un empleado en un período
SELECT SUM(monto) FROM bonos_descuentos 
WHERE empleado_id = ? AND mes_aplicacion = ? AND anio_aplicacion = ?
AND tipo = 'DESCUENTO' AND estado = 'APLICADO'
