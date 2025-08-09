-- Script para corregir esquemas de base de datos
-- Generado automáticamente

ALTER TABLE obras ADD codigo_obra VARCHAR(255) DEFAULT '' NOT NULL;
ALTER TABLE obras ADD nombre_obra VARCHAR(255) DEFAULT '' NOT NULL;
ALTER TABLE obras ADD fecha_actualizacion DATETIME DEFAULT NULL NULL;
ALTER TABLE pedidos ADD activo BIT DEFAULT 1 NOT NULL;
ALTER TABLE pedidos ADD numero_pedido VARCHAR(255) DEFAULT '' NOT NULL;
ALTER TABLE pedidos ADD fecha_entrega_solicitada DATETIME DEFAULT NULL NULL;
ALTER TABLE pedidos ADD tipo_pedido VARCHAR(255) NULL;
ALTER TABLE pedidos ADD prioridad VARCHAR(255) NULL;
ALTER TABLE pedidos ADD total DECIMAL(10,2) DEFAULT 0.00 NULL;
ALTER TABLE pedidos ADD observaciones NTEXT NULL;
ALTER TABLE pedidos ADD responsable_entrega VARCHAR(255) NULL;
ALTER TABLE pedidos ADD cantidad_pendiente INT DEFAULT 0 NULL;
ALTER TABLE vidrios ADD dimensiones VARCHAR(255) NULL;
ALTER TABLE vidrios ADD color_acabado VARCHAR(255) NULL;
ALTER TABLE vidrios ADD stock INT DEFAULT 0 NULL;
ALTER TABLE vidrios ADD estado VARCHAR(255) NULL;
