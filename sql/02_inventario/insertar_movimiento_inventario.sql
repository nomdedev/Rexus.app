INSERT INTO movimientos_inventario (
            inventario_id, tipo_movimiento, cantidad, fecha_movimiento, 
            costo_unitario, observaciones, usuario_responsable, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)