-- Insertar nuevo perfil en inventario con código QR
INSERT INTO inventario_perfiles
(codigo, descripcion, tipo, acabado, stock_actual, stock_minimo,
 stock_maximo, importe, ubicacion, proveedor, unidad,
 activo, usuario_creacion, observaciones, qr)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)