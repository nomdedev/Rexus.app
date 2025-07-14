-- ==================================================================
-- SCRIPT PARA CREAR USUARIOS DE TESTING CON HASH CORRECTO
-- ==================================================================
-- Contraseña para todos los usuarios: test123
-- Hash SHA256: ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae
-- ==================================================================

USE MPS_INVENTARIO;
GO

-- ==================================================================
-- CREAR/ACTUALIZAR USUARIO ADMIN
-- ==================================================================

IF EXISTS (SELECT 1 FROM usuarios WHERE usuario = 'admin')
BEGIN
    UPDATE usuarios
    SET password_hash = 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae',
        rol = 'admin',
        estado = 'activo',
        nombre = 'Administrador',
        apellido = 'del Sistema',
        email = 'admin@empresa.com'
    WHERE usuario = 'admin';
    PRINT '✅ Usuario admin actualizado: admin / test123';
END
ELSE
BEGIN
    INSERT INTO usuarios (usuario, password_hash, nombre, apellido, email, rol, estado, fecha_creacion)
    VALUES (
        'admin',
        'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae',
        'Administrador',
        'del Sistema',
        'admin@empresa.com',
        'admin',
        'activo',
        GETDATE()
    );
    PRINT '✅ Usuario admin creado: admin / test123';
END
GO

-- ==================================================================
-- CREAR/ACTUALIZAR USUARIO DE PRUEBA
-- ==================================================================

IF EXISTS (SELECT 1 FROM usuarios WHERE usuario = 'test_user')
BEGIN
    UPDATE usuarios
    SET password_hash = 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae',
        rol = 'admin',
        estado = 'activo',
        nombre = 'Usuario',
        apellido = 'de Prueba',
        email = 'test@empresa.com'
    WHERE usuario = 'test_user';
    PRINT '✅ Usuario test_user actualizado: test_user / test123';
END
ELSE
BEGIN
    INSERT INTO usuarios (usuario, password_hash, nombre, apellido, email, rol, estado, fecha_creacion)
    VALUES (
        'test_user',
        'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae',
        'Usuario',
        'de Prueba',
        'test@empresa.com',
        'admin',
        'activo',
        GETDATE()
    );
    PRINT '✅ Usuario test_user creado: test_user / test123';
END
GO

-- ==================================================================
-- CREAR USUARIO OPERADOR (ROL NORMAL)
-- ==================================================================

IF EXISTS (SELECT 1 FROM usuarios WHERE usuario = 'operador')
BEGIN
    UPDATE usuarios
    SET password_hash = 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae',
        rol = 'usuario',
        estado = 'activo',
        nombre = 'Usuario',
        apellido = 'Operador',
        email = 'operador@empresa.com'
    WHERE usuario = 'operador';
    PRINT '✅ Usuario operador actualizado: operador / test123';
END
ELSE
BEGIN
    INSERT INTO usuarios (usuario, password_hash, nombre, apellido, email, rol, estado, fecha_creacion)
    VALUES (
        'operador',
        'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae',
        'Usuario',
        'Operador',
        'operador@empresa.com',
        'usuario',
        'activo',
        GETDATE()
    );
    PRINT '✅ Usuario operador creado: operador / test123';
END
GO

-- ==================================================================
-- VERIFICAR USUARIOS CREADOS
-- ==================================================================

PRINT '📋 USUARIOS ACTIVOS EN EL SISTEMA:';
PRINT '==================================';

SELECT
    usuario,
    nombre + ' ' + ISNULL(apellido, '') as nombre_completo,
    email,
    rol,
    estado,
    fecha_creacion
FROM usuarios
WHERE estado = 'activo'
ORDER BY rol DESC, usuario;

PRINT '';
PRINT '🔐 CREDENCIALES PARA LOGIN:';
PRINT '===========================';
PRINT '• admin / test123 (Administrador)';
PRINT '• test_user / test123 (Administrador de prueba)';
PRINT '• operador / test123 (Usuario normal)';
PRINT '';
PRINT '✅ Script completado exitosamente';
