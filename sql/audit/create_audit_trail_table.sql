-- Crear tabla audit_trail si no existe
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='audit_trail' AND xtype='U')
CREATE TABLE audit_trail (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tabla VARCHAR(100) NOT NULL,
    accion VARCHAR(20) NOT NULL,
    registro_id INT NOT NULL,
    usuario_id INT,
    usuario_nombre VARCHAR(100),
    datos_anteriores TEXT,
    datos_nuevos TEXT,
    modulo VARCHAR(50),
    detalles TEXT,
    fecha_cambio DATETIME NOT NULL DEFAULT GETDATE(),
    ip_address VARCHAR(45),
    INDEX idx_tabla_fecha (tabla, fecha_cambio),
    INDEX idx_usuario_fecha (usuario_id, fecha_cambio),
    INDEX idx_registro (tabla, registro_id)
);
