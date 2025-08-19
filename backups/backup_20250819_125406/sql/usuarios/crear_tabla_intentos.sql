IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='intentos_login' AND xtype='U')
CREATE TABLE intentos_login (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    fecha_intento DATETIME DEFAULT GETDATE(),
    exitoso BIT NOT NULL,
    ip_address NVARCHAR(45) NULL
)