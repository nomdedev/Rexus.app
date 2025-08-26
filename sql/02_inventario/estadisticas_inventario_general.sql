SELECT COUNT(*) as total_productos, SUM(stock_actual) as total_unidades, 
            SUM(stock_actual * precio_unitario) as valor_total_inventario 
        FROM inventario WHERE activo = 1