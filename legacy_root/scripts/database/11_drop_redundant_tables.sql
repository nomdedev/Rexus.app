-- Script para eliminar tablas redundantes después de la migración exitosa
-- EJECUTAR SOLO DESPUÉS DE VERIFICAR QUE LA MIGRACIÓN FUNCIONA CORRECTAMENTE
-- Este script debe ejecutarse manualmente por un administrador

-- IMPORTANTE: CREAR BACKUP COMPLETO ANTES DE EJECUTAR
-- VERIFICAR QUE TODOS LOS SISTEMAS FUNCIONEN CON LAS NUEVAS TABLAS

-- Verificaciones previas
PRINT 'Iniciando proceso de eliminación de tablas redundantes...';
PRINT 'ADVERTENCIA: Este proceso es irreversible. Asegúrese de tener backups.';

-- Verificar que las tablas consolidadas existen
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='productos' AND xtype='U')
BEGIN
    PRINT 'ERROR: Tabla productos no existe. Abortando eliminación.';
    RETURN;
END

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_consolidado' AND xtype='U')
BEGIN
    PRINT 'ERROR: Tabla pedidos_consolidado no existe. Abortando eliminación.';
    RETURN;
END

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='productos_obra' AND xtype='U')
BEGIN
    PRINT 'ERROR: Tabla productos_obra no existe. Abortando eliminación.';
    RETURN;
END

-- Verificar que las tablas consolidadas tienen datos
DECLARE @productos_count INT, @pedidos_count INT, @productos_obra_count INT;

SELECT @productos_count = COUNT(*) FROM productos;
SELECT @pedidos_count = COUNT(*) FROM pedidos_consolidado;
SELECT @productos_obra_count = COUNT(*) FROM productos_obra;

PRINT 'Productos en tabla consolidada: ' + CAST(@productos_count AS VARCHAR(10));
PRINT 'Pedidos en tabla consolidada: ' + CAST(@pedidos_count AS VARCHAR(10));
PRINT 'Productos-obra en tabla consolidada: ' + CAST(@productos_obra_count AS VARCHAR(10));

-- Solo continuar si hay datos en las tablas consolidadas
IF @productos_count = 0
BEGIN
    PRINT 'ERROR: No hay datos en tabla productos. Abortando eliminación.';
    RETURN;
END

-- Eliminar tablas redundantes de inventario
PRINT 'Eliminando tablas redundantes de inventario...';

IF EXISTS (SELECT * FROM sysobjects WHERE name='inventario_perfiles' AND xtype='U')
BEGIN
    DROP TABLE inventario_perfiles;
    PRINT 'Tabla inventario_perfiles eliminada.';
END

-- Eliminar tablas redundantes de herrajes
PRINT 'Eliminando tablas redundantes de herrajes...';

IF EXISTS (SELECT * FROM sysobjects WHERE name='herrajes' AND xtype='U')
BEGIN
    DROP TABLE herrajes;
    PRINT 'Tabla herrajes eliminada.';
END

IF EXISTS (SELECT * FROM sysobjects WHERE name='herrajes_inventario' AND xtype='U')
BEGIN
    DROP TABLE herrajes_inventario;
    PRINT 'Tabla herrajes_inventario eliminada.';
END

IF EXISTS (SELECT * FROM sysobjects WHERE name='herrajes_obra' AND xtype='U')
BEGIN
    DROP TABLE herrajes_obra;
    PRINT 'Tabla herrajes_obra eliminada.';
END

-- Eliminar tablas redundantes de vidrios
PRINT 'Eliminando tablas redundantes de vidrios...';

IF EXISTS (SELECT * FROM sysobjects WHERE name='vidrios' AND xtype='U')
BEGIN
    DROP TABLE vidrios;
    PRINT 'Tabla vidrios eliminada.';
END

IF EXISTS (SELECT * FROM sysobjects WHERE name='vidrios_inventario' AND xtype='U')
BEGIN
    DROP TABLE vidrios_inventario;
    PRINT 'Tabla vidrios_inventario eliminada.';
END

IF EXISTS (SELECT * FROM sysobjects WHERE name='vidrios_obra' AND xtype='U')
BEGIN
    DROP TABLE vidrios_obra;
    PRINT 'Tabla vidrios_obra eliminada.';
END

-- Eliminar tablas redundantes de pedidos
PRINT 'Eliminando tablas redundantes de pedidos...';

IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos' AND xtype='U')
BEGIN
    DROP TABLE pedidos;
    PRINT 'Tabla pedidos eliminada.';
END

IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_detalle' AND xtype='U')
BEGIN
    DROP TABLE pedidos_detalle;
    PRINT 'Tabla pedidos_detalle eliminada.';
END

IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_herrajes' AND xtype='U')
BEGIN
    DROP TABLE pedidos_herrajes;
    PRINT 'Tabla pedidos_herrajes eliminada.';
END

-- Eliminar tablas redundantes de historial
PRINT 'Eliminando tablas redundantes de historial...';

IF EXISTS (SELECT * FROM sysobjects WHERE name='historial' AND xtype='U')
BEGIN
    DROP TABLE historial;
    PRINT 'Tabla historial eliminada (reemplazada por movimientos_inventario).';
END

-- Eliminar otras tablas redundantes específicas
IF EXISTS (SELECT * FROM sysobjects WHERE name='materiales_obra' AND xtype='U')
BEGIN
    DROP TABLE materiales_obra;
    PRINT 'Tabla materiales_obra eliminada (reemplazada por productos_obra).';
END

IF EXISTS (SELECT * FROM sysobjects WHERE name='inventario_movimientos' AND xtype='U')
BEGIN
    DROP TABLE inventario_movimientos;
    PRINT 'Tabla inventario_movimientos eliminada (reemplazada por movimientos_inventario).';
END

-- Actualizar estadísticas
PRINT 'Actualizando estadísticas de base de datos...';
EXEC sp_updatestats;

-- Verificar espacio liberado
PRINT 'Proceso de limpieza completado.';
PRINT 'Verifique que la aplicación funcione correctamente con las nuevas tablas.';
PRINT 'Si hay problemas, restaure desde el backup creado antes de este proceso.';

-- Resumen final
PRINT '';
PRINT 'RESUMEN DE CONSOLIDACIÓN:';
PRINT '- Base de datos consolidada de ~45 tablas a ~15 tablas principales';
PRINT '- Eliminación de redundancia de datos';
PRINT '- Mejora en integridad referencial';
PRINT '- Optimización de consultas y rendimiento';
PRINT '- Estructura unificada para mejor mantenimiento';
PRINT '';
PRINT 'CONSOLIDACIÓN COMPLETADA EXITOSAMENTE';