-- Consulta segura para contar asignaciones de vidrio a obras
-- Reemplaza f-string en eliminar_vidrio()
-- Parámetros: vidrio_id (int)

SELECT COUNT(*) 
FROM [vidrios_obra] 
WHERE vidrio_id = ?;