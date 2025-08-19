SELECT
    'herrajes' as tabla,
    CASE
        WHEN EXISTS (SELECT * FROM sysobjects WHERE name='herrajes' AND xtype='U')
        THEN 'EXISTE'
        ELSE 'NO EXISTE'
    END as estado;
SELECT
    'herrajes_obra' as tabla,
    CASE
        WHEN EXISTS (SELECT * FROM sysobjects WHERE name='herrajes_obra' AND xtype='U')
        THEN 'EXISTE'
        ELSE 'NO EXISTE'
    END as estado;
SELECT
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE '%herrajes%'
ORDER BY TABLE_NAME;