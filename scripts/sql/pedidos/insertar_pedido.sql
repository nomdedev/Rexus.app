-- Insertar nuevo pedido
-- Archivo: insertar_pedido.sql  
-- Módulo: Pedidos
-- Descripción: Inserta un nuevo pedido con validación de datos
-- Parámetros: Usar con cursor.execute() y tupla de valores

INSERT INTO [pedidos] (
    numero_pedido, cliente_id, obra_id, fecha_entrega_solicitada,
    estado, tipo_pedido, prioridad, subtotal, descuento, 
    impuestos, total, observaciones, direccion_entrega,
    responsable_entrega, telefono_contacto, usuario_creador
) VALUES (
    %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s
);

-- Ejemplo de uso en Python:
-- cursor.execute(query, (numero_pedido, cliente_id, obra_id, fecha_entrega, ...))
-- pedido_id = cursor.lastrowid
