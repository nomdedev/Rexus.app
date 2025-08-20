-- Crear tabla para almacenar presupuestos asociados a obras (SQLite)
-- Esta tabla almacena los archivos PDF de presupuestos subidos por los usuarios

CREATE TABLE IF NOT EXISTS presupuestos_obras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obra_id INTEGER NOT NULL,
    nombre_archivo TEXT NOT NULL,
    ruta_archivo TEXT NOT NULL,
    fecha_carga DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado TEXT NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO', 'ARCHIVADO')),
    tipo_presupuesto TEXT DEFAULT 'GENERAL' CHECK (tipo_presupuesto IN ('GENERAL', 'MATERIALES', 'MANO_OBRA', 'EQUIPOS')),
    version INTEGER DEFAULT 1,
    observaciones TEXT,
    usuario_carga TEXT,
    tamaño_archivo INTEGER DEFAULT 0,
    hash_archivo TEXT,
    
    -- Índices para optimizar consultas
    FOREIGN KEY (obra_id) REFERENCES obras(id) ON DELETE CASCADE
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_presupuestos_obra_id ON presupuestos_obras(obra_id);
CREATE INDEX IF NOT EXISTS idx_presupuestos_estado ON presupuestos_obras(estado);
CREATE INDEX IF NOT EXISTS idx_presupuestos_fecha ON presupuestos_obras(fecha_carga);

-- Trigger para actualizar fecha_modificacion
CREATE TRIGGER IF NOT EXISTS update_presupuestos_obras_timestamp 
    AFTER UPDATE ON presupuestos_obras
BEGIN
    UPDATE presupuestos_obras 
    SET fecha_modificacion = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;