-- Script de creación de base de datos y tabla para auditoria
IF DB_ID('auditoria') IS NULL
BEGIN
    CREATE DATABASE auditoria;
END
GO
USE auditoria;
GO
IF OBJECT_ID('auditoria', 'U') IS NULL
BEGIN
    CREATE TABLE auditoria (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario NVARCHAR(50) NOT NULL,
        evento NVARCHAR(150) NOT NULL,
        fecha_evento DATETIME DEFAULT GETDATE()
    );
END
GO
