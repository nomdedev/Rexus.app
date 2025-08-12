-- Creación de tabla principal de pedidos
-- Archivo: create_pedidos_table.sql
-- Módulo: Pedidos
-- Descripción: Crea la tabla principal de pedidos con todas las relaciones

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos' AND xtype='U')
CREATE TABLE pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    numero_pedido NVARCHAR(50) UNIQUE NOT NULL,
    cliente_id INT,
    obra_id INT,
    fecha_pedido DATETIME NOT NULL DEFAULT GETDATE(),
    fecha_entrega_solicitada DATETIME,
    fecha_entrega_real DATETIME,
    estado NVARCHAR(50) NOT NULL DEFAULT 'BORRADOR',
    tipo_pedido NVARCHAR(50) NOT NULL DEFAULT 'MATERIAL',
    prioridad NVARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    descuento DECIMAL(12,2) NOT NULL DEFAULT 0,
    impuestos DECIMAL(12,2) NOT NULL DEFAULT 0,
    total DECIMAL(12,2) NOT NULL DEFAULT 0,
    observaciones NTEXT,
    direccion_entrega NTEXT,
    responsable_entrega NVARCHAR(100),
    telefono_contacto NVARCHAR(50),
    usuario_creador INT,
    usuario_aprobador INT,
    fecha_aprobacion DATETIME,
    motivo_cancelacion NTEXT,
    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
    fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
    activo BIT NOT NULL DEFAULT 1
);
