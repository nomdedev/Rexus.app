-- scripts/sql/logistica/agregar_producto_entrega.sql
-- Agrega un producto a una entrega existente
INSERT INTO [detalle_entregas]
(entrega_id, producto, cantidad, peso_kg, volumen_m3, observaciones)
VALUES (?, ?, ?, ?, ?, ?)