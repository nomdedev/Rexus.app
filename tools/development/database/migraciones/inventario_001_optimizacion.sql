-- Migración 001: Optimización de tabla inventario
-- Esta migración agrega índices y normaliza campos críticos

IF NOT EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_codigo_inventario')
BEGIN
    CREATE INDEX idx_codigo_inventario ON inventario(codigo);
END

-- Normalizar campo 'descripcion' a NVARCHAR(255)
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'inventario' AND COLUMN_NAME = 'descripcion' AND DATA_TYPE <> 'nvarchar')
BEGIN
    ALTER TABLE inventario ALTER COLUMN descripcion NVARCHAR(255);
END

-- Optimización de consulta frecuente
-- (Ejemplo de vista materializada para reportes rápidos)
IF OBJECT_ID('inventario_resumen', 'V') IS NULL
BEGIN
    EXEC('CREATE VIEW inventario_resumen AS SELECT codigo, descripcion, cantidad, fecha_ultima_actualizacion FROM inventario');
END

-- Fin de migración
GO
