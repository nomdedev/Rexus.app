IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_entregas' AND xtype='U')
CREATE TABLE pedidos_entregas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    numero_entrega NVARCHAR(50) NOT NULL,
    fecha_entrega DATETIME NOT NULL,
    responsable_entrega NVARCHAR(100),
    observaciones_entrega NTEXT,
    estado_entrega NVARCHAR(50) NOT NULL DEFAULT 'PENDIENTE',
    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);