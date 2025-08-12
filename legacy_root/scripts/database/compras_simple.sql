-- Script simplificado para crear tablas de compras
-- Compatible con SQL Server

-- Crear tabla compras si no existe
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'compras')
BEGIN
    CREATE TABLE compras (
        id INT IDENTITY(1,1) PRIMARY KEY,
        numero_orden VARCHAR(50) UNIQUE NOT NULL,
        proveedor_id INT NOT NULL,
        fecha_orden DATE NOT NULL DEFAULT GETDATE(),
        fecha_entrega_esperada DATE,
        fecha_entrega_real DATE,
        estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
        subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        impuestos DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        observaciones TEXT,
        usuario_creacion VARCHAR(50) NOT NULL,
        fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
        usuario_aprobacion VARCHAR(50),
        fecha_aprobacion DATETIME,
        usuario_cancelacion VARCHAR(50),
        fecha_cancelacion DATETIME,
        motivo_cancelacion TEXT,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    )
    PRINT 'Tabla compras creada exitosamente'
END
ELSE
    PRINT 'Tabla compras ya existe'

-- Crear tabla detalle_compras si no existe  
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'detalle_compras')
BEGIN
    CREATE TABLE detalle_compras (
        id INT IDENTITY(1,1) PRIMARY KEY,
        compra_id INT NOT NULL,
        producto_codigo VARCHAR(50) NOT NULL,
        producto_descripcion VARCHAR(500) NOT NULL,
        cantidad DECIMAL(10,3) NOT NULL,
        precio_unitario DECIMAL(12,2) NOT NULL,
        subtotal DECIMAL(12,2) NOT NULL,
        observaciones TEXT,
        FOREIGN KEY (compra_id) REFERENCES compras(id)
    )
    PRINT 'Tabla detalle_compras creada exitosamente'
END
ELSE
    PRINT 'Tabla detalle_compras ya existe'

-- Crear índices solo si no existen
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_compras_proveedor' AND object_id = OBJECT_ID('compras'))
    CREATE INDEX idx_compras_proveedor ON compras(proveedor_id)

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_compras_fecha' AND object_id = OBJECT_ID('compras'))
    CREATE INDEX idx_compras_fecha ON compras(fecha_orden)

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_compras_estado' AND object_id = OBJECT_ID('compras'))
    CREATE INDEX idx_compras_estado ON compras(estado)

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_detalle_compra' AND object_id = OBJECT_ID('detalle_compras'))
    CREATE INDEX idx_detalle_compra ON detalle_compras(compra_id)

PRINT 'Sistema de Compras: Tablas e indices completados exitosamente'