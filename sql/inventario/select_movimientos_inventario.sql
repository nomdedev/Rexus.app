SELECT m.id, m.inventario_id, i.codigo, i.descripcion, i.categoria, 
            m.tipo_movimiento, m.cantidad, m.fecha_movimiento, m.costo_unitario, 
            m.observaciones, m.usuario_responsable 
        FROM movimientos_inventario m 
        INNER JOIN inventario i ON m.inventario_id = i.id 
        WHERE m.activo = 1