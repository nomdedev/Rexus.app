USE users;
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U')
BEGIN
    CREATE TABLE usuarios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario NVARCHAR(50) UNIQUE NOT NULL,
        password_hash NVARCHAR(255) NOT NULL,
        nombre NVARCHAR(100) NOT NULL,
        apellido NVARCHAR(100) NOT NULL,
        nombre_completo AS (nombre + ' ' + apellido) PERSISTED,
        email NVARCHAR(100) UNIQUE,
        telefono NVARCHAR(20),
        rol NVARCHAR(50) NOT NULL DEFAULT 'USUARIO',
        estado NVARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
        fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
        fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
        ultimo_acceso DATETIME,
        intentos_fallidos INT DEFAULT 0,
        bloqueado_hasta DATETIME,
        avatar NVARCHAR(255),
        configuracion_personal NTEXT,
        activo BIT NOT NULL DEFAULT 1
    );
    PRINT '✅ Tabla usuarios creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla usuarios ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='roles' AND xtype='U')
BEGIN
    CREATE TABLE roles (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(50) UNIQUE NOT NULL,
        descripcion NVARCHAR(255),
        permisos_json NTEXT,
        fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
        activo BIT NOT NULL DEFAULT 1
    );
    PRINT '✅ Tabla roles creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla roles ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='permisos_usuario' AND xtype='U')
BEGIN
    CREATE TABLE permisos_usuario (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL,
        modulo NVARCHAR(50) NOT NULL,
        permisos NVARCHAR(255) NOT NULL,
        fecha_asignacion DATETIME NOT NULL DEFAULT GETDATE(),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    );
    PRINT '✅ Tabla permisos_usuario creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla permisos_usuario ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sesiones_usuario' AND xtype='U')
BEGIN
    CREATE TABLE sesiones_usuario (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL,
        token_sesion NVARCHAR(255) NOT NULL,
        ip_address NVARCHAR(45),
        user_agent NVARCHAR(255),
        fecha_inicio DATETIME NOT NULL DEFAULT GETDATE(),
        fecha_fin DATETIME,
        activa BIT NOT NULL DEFAULT 1,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    );
    PRINT '✅ Tabla sesiones_usuario creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla sesiones_usuario ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='auditoria_sistema' AND xtype='U')
BEGIN
    CREATE TABLE auditoria_sistema (
        id INT IDENTITY(1,1) PRIMARY KEY,
        timestamp DATETIME NOT NULL DEFAULT GETDATE(),
        event_type NVARCHAR(50) NOT NULL,
        level NVARCHAR(20) NOT NULL,
        usuario_id INT NULL,
        usuario_nombre NVARCHAR(100) NULL,
        ip_address NVARCHAR(45) NULL,
        user_agent NVARCHAR(500) NULL,
        modulo NVARCHAR(50) NOT NULL,
        accion NVARCHAR(100) NOT NULL,
        detalles NTEXT NULL,
        resultado NVARCHAR(20) NOT NULL,
        session_id NVARCHAR(100) NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    PRINT '✅ Tabla auditoria_sistema creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla auditoria_sistema ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rbac_roles' AND xtype='U')
BEGIN
    CREATE TABLE rbac_roles (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(50) UNIQUE NOT NULL,
        display_name NVARCHAR(100) NOT NULL,
        descripcion NVARCHAR(255),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla rbac_roles creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla rbac_roles ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rbac_permissions' AND xtype='U')
BEGIN
    CREATE TABLE rbac_permissions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(100) UNIQUE NOT NULL,
        display_name NVARCHAR(100) NOT NULL,
        modulo NVARCHAR(50) NOT NULL,
        descripcion NVARCHAR(255),
        es_sensible BIT DEFAULT 0,
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla rbac_permissions creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla rbac_permissions ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rbac_role_permissions' AND xtype='U')
BEGIN
    CREATE TABLE rbac_role_permissions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        role_id INT NOT NULL,
        permission_id INT NOT NULL,
        granted_by INT NULL,
        fecha_asignacion DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (role_id) REFERENCES rbac_roles(id),
        FOREIGN KEY (permission_id) REFERENCES rbac_permissions(id),
        FOREIGN KEY (granted_by) REFERENCES usuarios(id),
        UNIQUE(role_id, permission_id)
    );
    PRINT '✅ Tabla rbac_role_permissions creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla rbac_role_permissions ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rbac_user_roles' AND xtype='U')
BEGIN
    CREATE TABLE rbac_user_roles (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL,
        role_id INT NOT NULL,
        assigned_by INT NOT NULL,
        fecha_asignacion DATETIME DEFAULT GETDATE(),
        fecha_expiracion DATETIME NULL,
        activo BIT DEFAULT 1,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (role_id) REFERENCES rbac_roles(id),
        FOREIGN KEY (assigned_by) REFERENCES usuarios(id),
        UNIQUE(usuario_id, role_id)
    );
    PRINT '✅ Tabla rbac_user_roles creada';
END
ELSE
BEGIN
    PRINT 'ℹ️  Tabla rbac_user_roles ya existe';
END
GO
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_usuarios_usuario')
BEGIN
    CREATE INDEX idx_usuarios_usuario ON usuarios(usuario);
    PRINT '✅ Índice idx_usuarios_usuario creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_usuarios_email')
BEGIN
    CREATE INDEX idx_usuarios_email ON usuarios(email);
    PRINT '✅ Índice idx_usuarios_email creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_usuarios_estado')
BEGIN
    CREATE INDEX idx_usuarios_estado ON usuarios(estado);
    PRINT '✅ Índice idx_usuarios_estado creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_permisos_usuario')
BEGIN
    CREATE INDEX idx_permisos_usuario ON permisos_usuario(usuario_id);
    PRINT '✅ Índice idx_permisos_usuario creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_sesiones_usuario')
BEGIN
    CREATE INDEX idx_sesiones_usuario ON sesiones_usuario(usuario_id);
    PRINT '✅ Índice idx_sesiones_usuario creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_auditoria_timestamp')
BEGIN
    CREATE INDEX idx_auditoria_timestamp ON auditoria_sistema(timestamp);
    PRINT '✅ Índice idx_auditoria_timestamp creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_auditoria_usuario')
BEGIN
    CREATE INDEX idx_auditoria_usuario ON auditoria_sistema(usuario_id);
    PRINT '✅ Índice idx_auditoria_usuario creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_auditoria_event_type')
BEGIN
    CREATE INDEX idx_auditoria_event_type ON auditoria_sistema(event_type);
    PRINT '✅ Índice idx_auditoria_event_type creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_auditoria_level')
BEGIN
    CREATE INDEX idx_auditoria_level ON auditoria_sistema(level);
    PRINT '✅ Índice idx_auditoria_level creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_rbac_user_roles_usuario')
BEGIN
    CREATE INDEX idx_rbac_user_roles_usuario ON rbac_user_roles(usuario_id);
    PRINT '✅ Índice idx_rbac_user_roles_usuario creado';
END
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_rbac_role_permissions_role')
BEGIN
    CREATE INDEX idx_rbac_role_permissions_role ON rbac_role_permissions(role_id);
    PRINT '✅ Índice idx_rbac_role_permissions_role creado';
END
GO
PRINT '';
PRINT '🎉 SCRIPT DE CREACIÓN DE TABLAS COMPLETADO';
PRINT '============================================';
PRINT 'Tablas creadas para Rexus.app v2.0.0:';
PRINT '- usuarios (con controles de seguridad)';
PRINT '- roles';
PRINT '- permisos_usuario';
PRINT '- sesiones_usuario';
PRINT '- auditoria_sistema';
PRINT '- rbac_roles';
PRINT '- rbac_permissions';
PRINT '- rbac_role_permissions';
PRINT '- rbac_user_roles';
PRINT '';
PRINT 'Siguiente paso: Ejecutar create_admin_simple.py para crear usuario admin';
PRINT '============================================';
GO