-- Script para verificar esquema de base de datos
-- Servidor: ITACHI\SQLEXPRESS
-- Usuario: sa

-- Verificar tablas en base de datos 'users'
USE users;
GO

-- 1. Listar todas las tablas del sistema
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_SCHEMA, TABLE_NAME;

-- 2. Verificar tablas específicas que encontramos en las consultas embebidas
SELECT 
    'USUARIOS' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'usuarios') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado
UNION ALL
SELECT 
    'SESIONES_USUARIO' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'sesiones_usuario') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado
UNION ALL
SELECT 
    'AUDITORIA_EVENTOS' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'auditoria_eventos') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado;

-- 3. Verificar estructura de tabla usuarios
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'usuarios'
ORDER BY ORDINAL_POSITION;
