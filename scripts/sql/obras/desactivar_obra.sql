-- Desactiva (elimina lógicamente) una obra
UPDATE obras SET activo = 0, fecha_eliminacion = GETDATE() WHERE id = ?