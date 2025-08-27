IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ordenes_proveedor')
CREATE INDEX idx_ordenes_proveedor ON ordenes_compra(proveedor_id)
