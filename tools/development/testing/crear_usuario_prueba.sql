
-- Script para crear usuario de prueba
-- Ejecutar manualmente en SQL Server Management Studio

USE MPS_INVENTARIO;

-- Crear usuario de prueba si no existe
IF NOT EXISTS (SELECT 1 FROM usuarios WHERE username = 'test_user')
BEGIN
    INSERT INTO usuarios (username, password, nombre, email, rol, activo, fecha_creacion)
    VALUES (
        'test_user',
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', -- Hash de 'test123'
        'Usuario de Prueba',
        'test@empresa.com',
        'admin',
        1,
        GETDATE()
    );
    PRINT '✅ Usuario de prueba creado: test_user / test123';
END
ELSE
BEGIN
    PRINT '⚠️ Usuario test_user ya existe';
END

-- Verificar usuarios activos
SELECT username, nombre, rol, activo FROM usuarios WHERE activo = 1;
