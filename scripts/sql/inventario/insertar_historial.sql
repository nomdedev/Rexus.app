-- Inserta un registro en el historial de operaciones
INSERT INTO historial (accion, usuario, fecha, detalles) VALUES (?, ?, GETDATE(), ?)