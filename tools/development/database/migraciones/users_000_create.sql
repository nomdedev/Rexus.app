-- Script de creación de base de datos y tabla para users
IF DB_ID('users') IS NULL
BEGIN
    CREATE DATABASE users;
END
GO
USE users;
GO
IF OBJECT_ID('users', 'U') IS NULL
BEGIN
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario NVARCHAR(50) NOT NULL,
        email NVARCHAR(100) NOT NULL,
        nombre NVARCHAR(100) NULL,
        rol NVARCHAR(20) NOT NULL,
        estado NVARCHAR(20) DEFAULT 'activo'
    );
END
GO
