-- Índices de optimización para mejorar rendimiento de consultas
-- Archivo: indices_optimizacion.sql

-- Índices para tabla obra_materiales (consultas de recursos)
CREATE INDEX IF NOT EXISTS idx_obra_materiales_obra_id ON obra_materiales(obra_id);
CREATE INDEX IF NOT EXISTS idx_obra_materiales_material_tipo ON obra_materiales(material_id, tipo_material);
CREATE INDEX IF NOT EXISTS idx_obra_materiales_fecha ON obra_materiales(fecha_asignacion);

-- Índices para tabla obra_personal (consultas de personal)
CREATE INDEX IF NOT EXISTS idx_obra_personal_obra_id ON obra_personal(obra_id);
CREATE INDEX IF NOT EXISTS idx_obra_personal_activo ON obra_personal(activo);
CREATE INDEX IF NOT EXISTS idx_obra_personal_fechas ON obra_personal(fecha_inicio, fecha_fin);

-- Índices para módulo inventario (consultas frecuentes)
CREATE INDEX IF NOT EXISTS idx_inventario_codigo ON inventario(codigo);
CREATE INDEX IF NOT EXISTS idx_inventario_categoria ON inventario(categoria);
CREATE INDEX IF NOT EXISTS idx_inventario_stock ON inventario(cantidad_disponible);

-- Índices para módulo obras (búsquedas y filtros)
CREATE INDEX IF NOT EXISTS idx_obras_estado ON obras(estado);
CREATE INDEX IF NOT EXISTS idx_obras_codigo ON obras(codigo_obra);
CREATE INDEX IF NOT EXISTS idx_obras_responsable ON obras(responsable);
CREATE INDEX IF NOT EXISTS idx_obras_fechas ON obras(fecha_inicio, fecha_finalizacion);

-- Índices para módulo usuarios (autenticación y permisos)
CREATE INDEX IF NOT EXISTS idx_usuarios_usuario ON usuarios(usuario);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_estado ON usuarios(estado);
CREATE INDEX IF NOT EXISTS idx_permisos_usuario_id ON permisos_usuario(usuario_id);

-- Índices para módulo compras (transacciones frecuentes)
CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras(fecha_compra);
CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_detalle_compras_compra_id ON detalle_compras(compra_id);

-- Índices para módulo pedidos (seguimiento y estados)
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado);
CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha_pedido);

-- Índices para módulo herrajes (consultas de stock)
CREATE INDEX IF NOT EXISTS idx_herrajes_codigo ON herrajes(codigo);
CREATE INDEX IF NOT EXISTS idx_herrajes_categoria ON herrajes(categoria);
CREATE INDEX IF NOT EXISTS idx_herrajes_stock ON herrajes(stock_actual);

-- Índices para módulo vidrios (consultas de tipo y stock)
CREATE INDEX IF NOT EXISTS idx_vidrios_tipo ON vidrios(tipo);
CREATE INDEX IF NOT EXISTS idx_vidrios_stock ON vidrios(stock_disponible);
CREATE INDEX IF NOT EXISTS idx_vidrios_codigo ON vidrios(codigo);

-- Índices para auditoría (consultas de logs)
CREATE INDEX IF NOT EXISTS idx_auditoria_tabla ON auditoria(tabla_afectada);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha_operacion);
CREATE INDEX IF NOT EXISTS idx_auditoria_operacion ON auditoria(tipo_operacion);

-- Índices compuestos para consultas complejas
CREATE INDEX IF NOT EXISTS idx_obra_materiales_compuesto ON obra_materiales(obra_id, tipo_material, material_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_auth ON usuarios(usuario, estado);
CREATE INDEX IF NOT EXISTS idx_obras_activas ON obras(estado, fecha_inicio) WHERE estado IN ('EN_PROGRESO', 'INICIADA');

-- Comentarios para mantenimiento
-- Estos índices mejoran significativamente el rendimiento de:
-- 1. Consultas de recursos por obra (obra_materiales)
-- 2. Búsquedas de inventario por código/categoría
-- 3. Autenticación de usuarios
-- 4. Filtros por estado en obras y pedidos
-- 5. Consultas de auditoría por fecha/usuario
-- 6. Joins complejos entre tablas relacionadas

-- Nota: Ejecutar estos índices en horarios de menor carga
-- Monitorear el uso de espacio en disco después de la creación