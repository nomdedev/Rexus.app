-- Consulta segura para marcar vidrio como inactivo
-- Reemplaza f-string en eliminar_vidrio()
-- Parámetros: vidrio_id (int)

UPDATE [vidrios]
SET estado = 'INACTIVO', fecha_actualizacion = GETDATE()
WHERE id = ?;