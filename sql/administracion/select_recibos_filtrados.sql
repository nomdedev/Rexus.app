-- select_recibos_filtrados.sql
-- Query base para obtener recibos (filtros se agregan dinámicamente)
-- Sin parámetros base

SELECT r.id, r.numero_recibo, r.fecha_emision, r.tipo_recibo,
       r.concepto, r.beneficiario, r.obra_id, r.proveedor_id,
       r.empleado_id, r.monto, r.moneda, r.metodo_pago,
       r.numero_comprobante, r.estado, r.impreso, r.archivo_pdf,
       r.observaciones, r.fecha_creacion, r.usuario_creacion
FROM recibos r