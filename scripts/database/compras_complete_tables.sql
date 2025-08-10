-- Script de Tablas de Compras Completado
-- Rexus.app - Sistema de Compras

-- Tabla principal de compras
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='compras' AND xtype='U')
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
    );
    PRINT 'Tabla compras creada exitosamente';
END

-- Tabla de proveedores
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='proveedores' AND xtype='U')
BEGIN
    CREATE TABLE proveedores (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo VARCHAR(20) UNIQUE NOT NULL,
        nombre VARCHAR(200) NOT NULL,
        razon_social VARCHAR(200),
        nit VARCHAR(20),
        telefono VARCHAR(20),
        email VARCHAR(100),
        direccion VARCHAR(500),
        ciudad VARCHAR(100),
        contacto_principal VARCHAR(100),
        estado VARCHAR(20) DEFAULT 'ACTIVO',
        calificacion DECIMAL(3,2) DEFAULT 0.00,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
    PRINT 'Tabla proveedores creada exitosamente';
END

-- Tabla de detalle de compras
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detalle_compras' AND xtype='U')
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
    );
    PRINT 'Tabla detalle_compras creada exitosamente';
END

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras(fecha_orden);
CREATE INDEX IF NOT EXISTS idx_compras_estado ON compras(estado);
CREATE INDEX IF NOT EXISTS idx_proveedores_codigo ON proveedores(codigo);
CREATE INDEX IF NOT EXISTS idx_detalle_compra ON detalle_compras(compra_id);

PRINT 'Sistema de Compras: Tablas e índices completados exitosamente';
