IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ordenes_fecha')
CREATE INDEX idx_ordenes_fecha ON ordenes_compra(fecha_orden)
