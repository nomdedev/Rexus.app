-- Script para verificar esquema de base de datos INVENTARIO
-- Servidor: ITACHI\SQLEXPRESS
-- Usuario: sa

-- Verificar tablas en base de datos 'inventario'
USE inventario;
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
    'PRODUCTOS' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'productos') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado
UNION ALL
SELECT 
    'INVENTARIO' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado
UNION ALL
SELECT 
    'HERRAJES' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'herrajes') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado
UNION ALL
SELECT 
    'ORDENES_COMPRA_DETALLES' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ordenes_compra_detalles') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado
UNION ALL
SELECT 
    'SERVICIOS_TRANSPORTE' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'servicios_transporte') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado
UNION ALL
SELECT 
    'OBRAS' as tabla,
    CASE WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'obras') 
         THEN 'EXISTE' 
         ELSE 'NO EXISTE' 
    END as estado;

-- 3. Verificar estructura de tabla productos (si existe)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'productos')
BEGIN
    SELECT 
        'PRODUCTOS - ESTRUCTURA' as info,
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'productos'
    ORDER BY ORDINAL_POSITION;
END
ELSE
BEGIN
    SELECT 'TABLA PRODUCTOS NO EXISTE' as info;
END

-- 4. Verificar estructura de tabla inventario (si existe)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario')
BEGIN
    SELECT 
        'INVENTARIO - ESTRUCTURA' as info,
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'inventario'
    ORDER BY ORDINAL_POSITION;
END
ELSE
BEGIN
    SELECT 'TABLA INVENTARIO NO EXISTE' as info;
END
