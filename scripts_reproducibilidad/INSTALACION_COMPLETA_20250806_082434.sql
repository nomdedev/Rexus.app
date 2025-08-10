-- =============================================
-- SCRIPT MAESTRO DE INSTALACIÓN - REXUS.APP
-- =============================================
-- Generado: 2025-08-06 08:24:34
-- Versión: 2.0.0
-- Propósito: Instalación completa del sistema

-- PASO 1: Crear bases de datos principales

-- Base de datos: inventario
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'inventario')
BEGIN
    CREATE DATABASE [inventario]
    PRINT 'Base de datos inventario creada exitosamente'
END
ELSE
BEGIN
    PRINT 'Base de datos inventario ya existe'
END
GO

-- Base de datos: users
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'users')
BEGIN
    CREATE DATABASE [users]
    PRINT 'Base de datos users creada exitosamente'
END
ELSE
BEGIN
    PRINT 'Base de datos users ya existe'
END
GO

-- Base de datos: auditoria
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'auditoria')
BEGIN
    CREATE DATABASE [auditoria]
    PRINT 'Base de datos auditoria creada exitosamente'
END
ELSE
BEGIN
    PRINT 'Base de datos auditoria ya existe'
END
GO

-- PASO 2: Ejecutar scripts específicos
-- Ejecute los siguientes scripts en orden:
-- 1. tools/development/database/MPS_SQL_COMPLETO_SIN_PREFIJOS.sql ✅ DISPONIBLE
-- 2. tools/development/database/crear_tablas_adicionales.sql ✅ DISPONIBLE
-- 3. scripts/sql/legacy_backup/database/create_tables.sql ✅ DISPONIBLE

-- PASO 3: Verificar instalación
-- Ejecute el validador: python auditor_completo_sql.py

-- =============================================
-- FIN DEL SCRIPT MAESTRO
-- =============================================
