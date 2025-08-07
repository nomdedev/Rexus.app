-- Insertar nueva obra con estructura real de la base de datos
-- Usa los nombres de columnas que existen en la tabla

INSERT INTO obras
(codigo, nombre, descripcion, cliente, direccion, telefono,
 fecha_inicio, fecha_fin_estimada, presupuesto_total,
 estado, etapa_actual, responsable, observaciones, 
 activo, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE())