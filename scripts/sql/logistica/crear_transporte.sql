-- scripts/sql/logistica/crear_transporte.sql
-- Crea un nuevo registro de transporte
INSERT INTO [transportes]
(codigo, tipo, proveedor, capacidad_kg, capacidad_m3, costo_km,
 disponible, observaciones, activo, fecha_creacion, fecha_modificacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE())