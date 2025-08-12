-- Script para verificar tablas de herrajes
-- Verifica la existencia de las tablas herrajes y herrajes_obra

-- Verificar tabla herrajes
SELECT 
    'herrajes' as tabla,
    CASE 
        WHEN EXISTS (SELECT * FROM sysobjects WHERE name='herrajes' AND xtype='U') 
        THEN 'EXISTE' 
        ELSE 'NO EXISTE' 
    END as estado;

-- Verificar tabla herrajes_obra
SELECT 
    'herrajes_obra' as tabla,
    CASE 
        WHEN EXISTS (SELECT * FROM sysobjects WHERE name='herrajes_obra' AND xtype='U') 
        THEN 'EXISTE' 
        ELSE 'NO EXISTE' 
    END as estado;

-- Listar todas las tablas que contienen 'herrajes' en el nombre
SELECT 
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME LIKE '%herrajes%'
ORDER BY TABLE_NAME;
