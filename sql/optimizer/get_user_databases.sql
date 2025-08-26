-- Obtener lista de bases de datos de usuario (excluyendo sistema)
SELECT name 
FROM sys.databases 
WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')
  AND state = 0
