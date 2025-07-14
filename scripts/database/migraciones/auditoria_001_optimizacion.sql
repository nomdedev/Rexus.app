USE auditoria;

IF NOT EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_fecha_auditoria')
BEGIN
    CREATE INDEX idx_fecha_auditoria ON auditoria(fecha_evento);
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'auditoria' AND COLUMN_NAME = 'evento' AND DATA_TYPE <> 'nvarchar')
BEGIN
    ALTER TABLE auditoria ALTER COLUMN evento NVARCHAR(150);
END

IF OBJECT_ID('auditoria_resumen', 'V') IS NULL
BEGIN
    EXEC('CREATE VIEW auditoria_resumen AS SELECT usuario, evento, fecha_evento FROM auditoria');
END

GO
