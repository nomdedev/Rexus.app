SELECT categoria, COUNT(*) as productos, SUM(stock_actual) as unidades, 
            SUM(stock_actual * precio_unitario) as valor_categoria 
        FROM inventario WHERE activo = 1 GROUP BY categoria