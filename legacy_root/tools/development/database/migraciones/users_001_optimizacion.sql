-- Migración 001: Optimización de tabla users
-- Agrega índice y normaliza campos críticos

IF NOT EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_email_users')
BEGIN
    CREATE INDEX idx_email_users ON users(email);
END

-- Normalizar campo 'nombre' a NVARCHAR(100)
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'nombre' AND DATA_TYPE <> 'nvarchar')
BEGIN
    ALTER TABLE users ALTER COLUMN nombre NVARCHAR(100);
END

-- Vista rápida de usuarios activos
IF OBJECT_ID('usuarios_activos', 'V') IS NULL
BEGIN
    EXEC('CREATE VIEW usuarios_activos AS SELECT usuario, email, rol, estado FROM users WHERE estado = ''activo''');
END

-- Fin de migración
GO
