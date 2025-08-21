-- Crear tabla detalle_pedidos en SQL Server
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detalle_pedidos' AND xtype='U')
CREATE TABLE detalle_pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT,
    descripcion NVARCHAR(255),
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(5,2) DEFAULT 0,
    subtotal DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);