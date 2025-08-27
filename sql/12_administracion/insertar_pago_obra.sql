INSERT INTO pagos_obras
(obra_id, concepto, categoria, monto, fecha_pago, proveedor_id,
empleado_id, metodo_pago, numero_comprobante, observaciones,
usuario_creacion, usuario_actualizacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
