-- ============================================
-- SCRIPT DE CREACIÓN: AUDITORIA
-- ============================================
-- Generado automáticamente el: 2025-08-06 08:24:34
-- Total de tablas: 5

-- Crear base de datos si no existe
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'auditoria')
BEGIN
    CREATE DATABASE [auditoria]
END
GO

USE [auditoria]
GO

-- Verificar que las tablas existan

-- Verificar tabla: auditoria
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'auditoria')
BEGIN
    PRINT 'ADVERTENCIA: Tabla auditoria no existe - requiere definición manual'
END

-- Verificar tabla: auditorias_sistema
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'auditorias_sistema')
BEGIN
    PRINT 'ADVERTENCIA: Tabla auditorias_sistema no existe - requiere definición manual'
END

-- Verificar tabla: errores_sistema
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'errores_sistema')
BEGIN
    PRINT 'ADVERTENCIA: Tabla errores_sistema no existe - requiere definición manual'
END

-- Verificar tabla: eventos_auditoria
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'eventos_auditoria')
BEGIN
    PRINT 'ADVERTENCIA: Tabla eventos_auditoria no existe - requiere definición manual'
END

-- Verificar tabla: log_accesos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'log_accesos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla log_accesos no existe - requiere definición manual'
END

-- ============================================
-- FIN DEL SCRIPT DE VERIFICACIÓN
-- ============================================
-- Para completar este script, necesitas:
-- 1. Exportar la estructura real de cada tabla
-- 2. Incluir las definiciones CREATE TABLE
-- 3. Agregar datos iniciales si es necesario
