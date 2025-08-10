-- ============================================
-- SCRIPT DE CREACIÓN: INVENTARIO
-- ============================================
-- Generado automáticamente el: 2025-08-06 08:24:34
-- Total de tablas: 71

-- Crear base de datos si no existe
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'inventario')
BEGIN
    CREATE DATABASE [inventario]
END
GO

USE [inventario]
GO

-- Verificar que las tablas existan

-- Verificar tabla: asistencias
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'asistencias')
BEGIN
    PRINT 'ADVERTENCIA: Tabla asistencias no existe - requiere definición manual'
END

-- Verificar tabla: auditoria
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'auditoria')
BEGIN
    PRINT 'ADVERTENCIA: Tabla auditoria no existe - requiere definición manual'
END

-- Verificar tabla: auditoria_cambios
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'auditoria_cambios')
BEGIN
    PRINT 'ADVERTENCIA: Tabla auditoria_cambios no existe - requiere definición manual'
END

-- Verificar tabla: auditorias_sistema
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'auditorias_sistema')
BEGIN
    PRINT 'ADVERTENCIA: Tabla auditorias_sistema no existe - requiere definición manual'
END

-- Verificar tabla: bonos_descuentos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'bonos_descuentos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla bonos_descuentos no existe - requiere definición manual'
END

-- Verificar tabla: cargas_material
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'cargas_material')
BEGIN
    PRINT 'ADVERTENCIA: Tabla cargas_material no existe - requiere definición manual'
END

-- Verificar tabla: clientes
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'clientes')
BEGIN
    PRINT 'ADVERTENCIA: Tabla clientes no existe - requiere definición manual'
END

-- Verificar tabla: configuracion_sistema
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'configuracion_sistema')
BEGIN
    PRINT 'ADVERTENCIA: Tabla configuracion_sistema no existe - requiere definición manual'
END

-- Verificar tabla: costos_logisticos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'costos_logisticos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla costos_logisticos no existe - requiere definición manual'
END

-- Verificar tabla: cronograma_obras
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'cronograma_obras')
BEGIN
    PRINT 'ADVERTENCIA: Tabla cronograma_obras no existe - requiere definición manual'
END

-- Verificar tabla: departamentos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'departamentos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla departamentos no existe - requiere definición manual'
END

-- Verificar tabla: detalle_entregas
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'detalle_entregas')
BEGIN
    PRINT 'ADVERTENCIA: Tabla detalle_entregas no existe - requiere definición manual'
END

-- Verificar tabla: detalle_pedidos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'detalle_pedidos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla detalle_pedidos no existe - requiere definición manual'
END

-- Verificar tabla: detalles_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'detalles_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla detalles_obra no existe - requiere definición manual'
END

-- Verificar tabla: empleados
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'empleados')
BEGIN
    PRINT 'ADVERTENCIA: Tabla empleados no existe - requiere definición manual'
END

-- Verificar tabla: entregas
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'entregas')
BEGIN
    PRINT 'ADVERTENCIA: Tabla entregas no existe - requiere definición manual'
END

-- Verificar tabla: equipos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'equipos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla equipos no existe - requiere definición manual'
END

-- Verificar tabla: estado_equipos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'estado_equipos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla estado_equipos no existe - requiere definición manual'
END

-- Verificar tabla: estado_material
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'estado_material')
BEGIN
    PRINT 'ADVERTENCIA: Tabla estado_material no existe - requiere definición manual'
END

-- Verificar tabla: herrajes
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'herrajes')
BEGIN
    PRINT 'ADVERTENCIA: Tabla herrajes no existe - requiere definición manual'
END

-- Verificar tabla: herrajes_por_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'herrajes_por_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla herrajes_por_obra no existe - requiere definición manual'
END

-- Verificar tabla: herramientas
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'herramientas')
BEGIN
    PRINT 'ADVERTENCIA: Tabla herramientas no existe - requiere definición manual'
END

-- Verificar tabla: historial
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'historial')
BEGIN
    PRINT 'ADVERTENCIA: Tabla historial no existe - requiere definición manual'
END

-- Verificar tabla: historial_laboral
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'historial_laboral')
BEGIN
    PRINT 'ADVERTENCIA: Tabla historial_laboral no existe - requiere definición manual'
END

-- Verificar tabla: historial_mantenimiento
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'historial_mantenimiento')
BEGIN
    PRINT 'ADVERTENCIA: Tabla historial_mantenimiento no existe - requiere definición manual'
END

-- Verificar tabla: inventario
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario')
BEGIN
    PRINT 'ADVERTENCIA: Tabla inventario no existe - requiere definición manual'
END

-- Verificar tabla: inventario_items
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario_items')
BEGIN
    PRINT 'ADVERTENCIA: Tabla inventario_items no existe - requiere definición manual'
END

-- Verificar tabla: inventario_perfiles
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario_perfiles')
BEGIN
    PRINT 'ADVERTENCIA: Tabla inventario_perfiles no existe - requiere definición manual'
END

-- Verificar tabla: libro_contable
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'libro_contable')
BEGIN
    PRINT 'ADVERTENCIA: Tabla libro_contable no existe - requiere definición manual'
END

-- Verificar tabla: logistica_por_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'logistica_por_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla logistica_por_obra no existe - requiere definición manual'
END

-- Verificar tabla: logs_sistema
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'logs_sistema')
BEGIN
    PRINT 'ADVERTENCIA: Tabla logs_sistema no existe - requiere definición manual'
END

-- Verificar tabla: mantenimientos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'mantenimientos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla mantenimientos no existe - requiere definición manual'
END

-- Verificar tabla: materiales
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'materiales')
BEGIN
    PRINT 'ADVERTENCIA: Tabla materiales no existe - requiere definición manual'
END

-- Verificar tabla: materiales_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'materiales_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla materiales_obra no existe - requiere definición manual'
END

-- Verificar tabla: materiales_proveedores
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'materiales_proveedores')
BEGIN
    PRINT 'ADVERTENCIA: Tabla materiales_proveedores no existe - requiere definición manual'
END

-- Verificar tabla: modulos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'modulos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla modulos no existe - requiere definición manual'
END

-- Verificar tabla: movimientos_inventario
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'movimientos_inventario')
BEGIN
    PRINT 'ADVERTENCIA: Tabla movimientos_inventario no existe - requiere definición manual'
END

-- Verificar tabla: nomina
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'nomina')
BEGIN
    PRINT 'ADVERTENCIA: Tabla nomina no existe - requiere definición manual'
END

-- Verificar tabla: notificaciones
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'notificaciones')
BEGIN
    PRINT 'ADVERTENCIA: Tabla notificaciones no existe - requiere definición manual'
END

-- Verificar tabla: obra_materiales
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'obra_materiales')
BEGIN
    PRINT 'ADVERTENCIA: Tabla obra_materiales no existe - requiere definición manual'
END

-- Verificar tabla: obras
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'obras')
BEGIN
    PRINT 'ADVERTENCIA: Tabla obras no existe - requiere definición manual'
END

-- Verificar tabla: pagos_materiales
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pagos_materiales')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pagos_materiales no existe - requiere definición manual'
END

-- Verificar tabla: pagos_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pagos_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pagos_obra no existe - requiere definición manual'
END

-- Verificar tabla: pagos_pedidos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pagos_pedidos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pagos_pedidos no existe - requiere definición manual'
END

-- Verificar tabla: pagos_por_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pagos_por_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pagos_por_obra no existe - requiere definición manual'
END

-- Verificar tabla: parametros_modulos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'parametros_modulos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla parametros_modulos no existe - requiere definición manual'
END

-- Verificar tabla: pedidos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pedidos no existe - requiere definición manual'
END

-- Verificar tabla: pedidos_compra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_compra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pedidos_compra no existe - requiere definición manual'
END

-- Verificar tabla: pedidos_consolidado
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_consolidado')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pedidos_consolidado no existe - requiere definición manual'
END

-- Verificar tabla: pedidos_detalle
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_detalle')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pedidos_detalle no existe - requiere definición manual'
END

-- Verificar tabla: pedidos_herrajes
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_herrajes')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pedidos_herrajes no existe - requiere definición manual'
END

-- Verificar tabla: pedidos_historial
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_historial')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pedidos_historial no existe - requiere definición manual'
END

-- Verificar tabla: pedidos_material
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_material')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pedidos_material no existe - requiere definición manual'
END

-- Verificar tabla: pedidos_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla pedidos_obra no existe - requiere definición manual'
END

-- Verificar tabla: permisos_usuario
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'permisos_usuario')
BEGIN
    PRINT 'ADVERTENCIA: Tabla permisos_usuario no existe - requiere definición manual'
END

-- Verificar tabla: productos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'productos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla productos no existe - requiere definición manual'
END

-- Verificar tabla: productos_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'productos_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla productos_obra no existe - requiere definición manual'
END

-- Verificar tabla: programacion_mantenimiento
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'programacion_mantenimiento')
BEGIN
    PRINT 'ADVERTENCIA: Tabla programacion_mantenimiento no existe - requiere definición manual'
END

-- Verificar tabla: proveedores
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'proveedores')
BEGIN
    PRINT 'ADVERTENCIA: Tabla proveedores no existe - requiere definición manual'
END

-- Verificar tabla: proveedores_transporte
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'proveedores_transporte')
BEGIN
    PRINT 'ADVERTENCIA: Tabla proveedores_transporte no existe - requiere definición manual'
END

-- Verificar tabla: recibos
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'recibos')
BEGIN
    PRINT 'ADVERTENCIA: Tabla recibos no existe - requiere definición manual'
END

-- Verificar tabla: reserva_materiales
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'reserva_materiales')
BEGIN
    PRINT 'ADVERTENCIA: Tabla reserva_materiales no existe - requiere definición manual'
END

-- Verificar tabla: roles
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'roles')
BEGIN
    PRINT 'ADVERTENCIA: Tabla roles no existe - requiere definición manual'
END

-- Verificar tabla: rutas
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'rutas')
BEGIN
    PRINT 'ADVERTENCIA: Tabla rutas no existe - requiere definición manual'
END

-- Verificar tabla: tipos_mantenimiento
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tipos_mantenimiento')
BEGIN
    PRINT 'ADVERTENCIA: Tabla tipos_mantenimiento no existe - requiere definición manual'
END

-- Verificar tabla: transportes
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'transportes')
BEGIN
    PRINT 'ADVERTENCIA: Tabla transportes no existe - requiere definición manual'
END

-- Verificar tabla: users
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'users')
BEGIN
    PRINT 'ADVERTENCIA: Tabla users no existe - requiere definición manual'
END

-- Verificar tabla: usuarios
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'usuarios')
BEGIN
    PRINT 'ADVERTENCIA: Tabla usuarios no existe - requiere definición manual'
END

-- Verificar tabla: vidrios
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'vidrios')
BEGIN
    PRINT 'ADVERTENCIA: Tabla vidrios no existe - requiere definición manual'
END

-- Verificar tabla: vidrios_medidas
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'vidrios_medidas')
BEGIN
    PRINT 'ADVERTENCIA: Tabla vidrios_medidas no existe - requiere definición manual'
END

-- Verificar tabla: vidrios_por_obra
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'vidrios_por_obra')
BEGIN
    PRINT 'ADVERTENCIA: Tabla vidrios_por_obra no existe - requiere definición manual'
END

-- ============================================
-- FIN DEL SCRIPT DE VERIFICACIÓN
-- ============================================
-- Para completar este script, necesitas:
-- 1. Exportar la estructura real de cada tabla
-- 2. Incluir las definiciones CREATE TABLE
-- 3. Agregar datos iniciales si es necesario
