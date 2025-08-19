IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_historial' AND xtype='U')
CREATE TABLE pedidos_historial (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    estado_anterior NVARCHAR(50),
    estado_nuevo NVARCHAR(50) NOT NULL,
    fecha_cambio DATETIME NOT NULL DEFAULT GETDATE(),
    usuario_id INT,
    observaciones NTEXT,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);