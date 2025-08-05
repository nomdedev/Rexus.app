-- Script de migración para agregar columnas de seguridad avanzada
-- Rexus.app v2.0.0 - Funcionalidades de Seguridad de Usuarios
-- Ejecutar en Microsoft SQL Server

USE [rexus_db];
GO

-- Verificar si las columnas ya existen antes de agregarlas
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('usuarios') AND name = 'intentos_fallidos')
BEGIN
    ALTER TABLE usuarios ADD intentos_fallidos INT DEFAULT 0;
    PRINT '✅ Columna intentos_fallidos agregada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Columna intentos_fallidos ya existe';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('usuarios') AND name = 'ultimo_intento_fallido')
BEGIN
    ALTER TABLE usuarios ADD ultimo_intento_fallido DATETIME2;
    PRINT '✅ Columna ultimo_intento_fallido agregada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Columna ultimo_intento_fallido ya existe';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('usuarios') AND name = 'bloqueado_hasta')
BEGIN
    ALTER TABLE usuarios ADD bloqueado_hasta DATETIME2;
    PRINT '✅ Columna bloqueado_hasta agregada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Columna bloqueado_hasta ya existe';
END

-- Crear índice para mejorar performance en consultas de seguridad
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_usuarios_intentos_fallidos')
BEGIN
    CREATE INDEX IX_usuarios_intentos_fallidos ON usuarios (intentos_fallidos, ultimo_intento_fallido);
    PRINT '✅ Índice IX_usuarios_intentos_fallidos creado';
END
ELSE
BEGIN
    PRINT 'ℹ️  Índice IX_usuarios_intentos_fallidos ya existe';
END

-- Verificar estructura actual de la tabla
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'usuarios'
ORDER BY ORDINAL_POSITION;

PRINT '🔐 Migración de seguridad completada exitosamente';
GO
