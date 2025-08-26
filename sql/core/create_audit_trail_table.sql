-- Archivo SQL: Crear tabla audit_trail si no existe
-- Ubicación: sql/core/create_audit_trail_table.sql
-- Propósito: Corrección SQL injection en audit_trail.py _create_audit_table_if_not_exists()

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
    ip_address VARCHAR(45)
);

-- Crear índices para optimización
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_tabla_fecha')
CREATE INDEX idx_tabla_fecha ON audit_trail (tabla, fecha_cambio);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_usuario_fecha')
CREATE INDEX idx_usuario_fecha ON audit_trail (usuario_id, fecha_cambio);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_registro')
CREATE INDEX idx_registro ON audit_trail (tabla, registro_id);