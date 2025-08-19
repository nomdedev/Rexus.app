INSERT INTO inventario_perfiles
(codigo, descripcion, tipo, precio_unitario, stock_actual, stock_minimo, ubicacion, activo, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())