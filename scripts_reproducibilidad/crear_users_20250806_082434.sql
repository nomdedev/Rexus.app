-- ============================================
-- SCRIPT DE CREACIÓN: USERS
-- ============================================
-- Generado automáticamente el: 2025-08-06 08:24:34
-- Total de tablas: 9

-- Crear base de datos si no existe
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'users')
BEGIN
    CREATE DATABASE [users]
END
GO

USE [users]
GO

-- Verificar que las tablas existan

-- Verificar tabla: logs_seguridad
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'logs_seguridad')
BEGIN
    PRINT 'ADVERTENCIA: Tabla logs_seguridad no existe - requiere definición manual'
END

-- Verificar tabla: logs_usuarios
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'logs_usuarios')
BEGIN
    PRINT 'ADVERTENCIA: Tabla logs_usuarios no existe - requiere definición manual'
END

-- Verificar tabla: notificaciones
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'notificaciones')
BEGIN
    PRINT 'ADVERTENCIA: Tabla notificaciones no existe - requiere definición manual'
END

-- Verificar tabla: permisos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'permisos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla permisos no existe - requiere definición manual'
END

-- Verificar tabla: permisos_modulos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'permisos_modulos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla permisos_modulos no existe - requiere definición manual'
END

-- Verificar tabla: rol_permisos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'rol_permisos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla rol_permisos no existe - requiere definición manual'
END

-- Verificar tabla: roles
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'roles')
BEGIN
    PRINT 'ADVERTENCIA: Tabla roles no existe - requiere definición manual'
END

-- Verificar tabla: sesiones
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'sesiones')
BEGIN
    PRINT 'ADVERTENCIA: Tabla sesiones no existe - requiere definición manual'
END

-- Verificar tabla: usuarios
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'usuarios')
BEGIN
    PRINT 'ADVERTENCIA: Tabla usuarios no existe - requiere definición manual'
END

-- ============================================
-- FIN DEL SCRIPT DE VERIFICACIÓN
-- ============================================
-- Para completar este script, necesitas:
-- 1. Exportar la estructura real de cada tabla
-- 2. Incluir las definiciones CREATE TABLE
-- 3. Agregar datos iniciales si es necesario
