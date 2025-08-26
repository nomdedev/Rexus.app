-- Verificar si existe la tabla de auditoría
SELECT COUNT(*) as table_exists
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'dbo' 
    AND TABLE_NAME = 'auditoria_sistema';
