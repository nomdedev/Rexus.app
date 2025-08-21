-- Crear tabla pedidos en SQL Server
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos' AND xtype='U')
CREATE TABLE pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    numero_pedido NVARCHAR(50) NOT NULL UNIQUE,
    cliente_id INT,
    obra_id INT,
    estado NVARCHAR(20) DEFAULT 'PENDIENTE',
    fecha_pedido DATETIME DEFAULT GETDATE(),
    fecha_entrega DATETIME,
    subtotal DECIMAL(10,2) DEFAULT 0,
    impuestos DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) DEFAULT 0,
    observaciones NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);