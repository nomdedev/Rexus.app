-- Consulta segura para obtener información de vidrio antes de eliminación
-- Reemplaza f-string en eliminar_vidrio()
-- Parámetros: vidrio_id (int)

SELECT codigo, descripcion 
FROM [vidrios] 
WHERE id = ?;