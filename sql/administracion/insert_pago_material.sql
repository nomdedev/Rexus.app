-- insert_pago_material.sql
-- Inserta un pago de material
-- Parámetros: ? (material_id), ? (proveedor_id), ? (concepto), ? (categoria), ? (monto), ? (fecha_pago), ? (metodo_pago), ? (numero_comprobante), ? (observaciones), ? (usuario_creacion), ? (usuario_actualizacion)

INSERT INTO pagos_materiales
(material_id, proveedor_id, concepto, categoria, monto, fecha_pago,
 metodo_pago, numero_comprobante, observaciones, usuario_creacion, usuario_actualizacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)