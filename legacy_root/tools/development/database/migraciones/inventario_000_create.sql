-- Script de creación de base de datos y tablas para inventario
IF DB_ID('inventario') IS NULL
BEGIN
    CREATE DATABASE inventario;
END
GO
USE inventario;
GO
IF OBJECT_ID('inventario', 'U') IS NULL
BEGIN
    CREATE TABLE inventario (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50) NOT NULL,
        descripcion NVARCHAR(255) NULL,
        cantidad INT DEFAULT 0,
        fecha_ultima_actualizacion DATETIME DEFAULT GETDATE()
    );
END
GO
