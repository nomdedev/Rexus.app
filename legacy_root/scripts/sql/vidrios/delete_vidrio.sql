-- Consulta segura para eliminar vidrio completamente
-- Reemplaza f-string en eliminar_vidrio()
-- Parámetros: vidrio_id (int)

DELETE FROM [vidrios] 
WHERE id = ?;