# Diagrama de Relaciones - Base de Datos Rexus.app

## Diagrama General de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DB: users     │    │  DB: inventario │    │  DB: auditoria  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │  usuarios   │ │    │ │    obras    │ │    │ │  auditoria  │ │
│ │  permisos   │ │    │ │  herrajes   │ │    │ │ log_accesos │ │
│ │  sesiones   │ │    │ │   vidrios   │ │    │ │             │ │
│ └─────────────┘ │    │ │  empleados  │ │    │ └─────────────┘ │
│                 │    │ │   equipos   │ │    │                 │
│                 │    │ │ proveedores │ │    │                 │
│                 │    │ │   pedidos   │ │    │                 │
│                 │    │ └─────────────┘ │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌─────────────────┐
                    │   Aplicación    │
                    │   Rexus.app     │
                    └─────────────────┘
```

## Relaciones Principales en DB: inventario

### 1. Flujo Central: Obras

```
                    ┌─────────────┐
                    │    obras    │
                    │             │
                    │ - id        │
                    │ - nombre    │
                    │ - cliente   │
                    │ - estado    │
                    │ - usuario_  │
                    │   creador   │
                    └─────────────┘
                           │
                           │ (1:N)
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │materiales_  │ │herrajes_    │ │vidrios_     │
    │obra         │ │por_obra     │ │por_obra     │
    │             │ │             │ │             │
    │- obra_id    │ │- obra_id    │ │- obra_id    │
    │- material_id│ │- herraje_id │ │- vidrio_id  │
    │- cantidad   │ │- cantidad   │ │- metros_m2  │
    └─────────────┘ └─────────────┘ └─────────────┘
```

### 2. Relaciones de Inventario

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  herrajes   │         │   vidrios   │         │ proveedores │
│             │         │             │         │             │
│ - id        │         │ - id        │         │ - id        │
│ - codigo    │         │ - tipo      │         │ - nombre    │
│ - nombre    │         │ - espesor   │         │ - contacto  │
│ - categoria │         │ - color     │         │ - telefono  │
│ - proveedor │────────▶│ - proveedor │────────▶│ - email     │
│ - precio    │         │ - precio_m2 │         │ - direccion │
│ - stock     │         │ - activo    │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
       │                       │                       │
       │ (N:1)                 │ (N:1)                 │ (1:N)
       │                       │                       │
       ▼                       ▼                       ▼
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│herrajes_    │         │vidrios_     │         │   pedidos   │
│por_obra     │         │por_obra     │         │             │
│             │         │             │         │ - id        │
│- herraje_id │         │- vidrio_id  │         │ - numero    │
│- obra_id    │         │- obra_id    │         │ - proveedor │
│- cantidad   │         │- metros_m2  │         │ - fecha     │
│- precio     │         │- precio_m2  │         │ - estado    │
└─────────────┘         └─────────────┘         └─────────────┘
```

### 3. Relaciones de Recursos Humanos

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│departamentos│         │  empleados  │         │ asistencias │
│             │         │             │         │             │
│ - id        │         │ - id        │         │ - id        │
│ - nombre    │◄────────│ - codigo    │────────▶│ - empleado  │
│ - descripcion│        │ - nombre    │         │ - fecha     │
│             │         │ - apellido  │         │ - horas     │
│             │         │ - dni       │         │ - estado    │
│             │         │ - cargo     │         │             │
│             │         │ - depto_id  │         │             │
│             │         │ - salario   │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
                               │
                               │ (1:N)
                               ▼
                        ┌─────────────┐
                        │   nomina    │
                        │             │
                        │ - id        │
                        │ - empleado  │
                        │ - periodo   │
                        │ - salario   │
                        │ - descuentos│
                        │ - bonos     │
                        └─────────────┘
```

### 4. Relaciones de Equipos y Mantenimiento

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   equipos   │         │mantenimientos│       │historial_   │
│             │         │             │         │mantenimiento│
│ - id        │         │ - id        │         │             │
│ - codigo    │◄────────│ - equipo_id │────────▶│ - id        │
│ - nombre    │         │ - fecha     │         │ - equipo_id │
│ - tipo      │         │ - tipo      │         │ - fecha     │
│ - modelo    │         │ - costo     │         │ - descripcion│
│ - estado    │         │ - realizado │         │ - costo     │
│ - ubicacion │         │             │         │ - tecnico   │
│ - valor     │         │             │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
       │
       │ (1:N)
       ▼
┌─────────────┐
│programacion_│
│mantenimiento│
│             │
│ - id        │
│ - equipo_id │
│ - fecha_prog│
│ - tipo      │
│ - frecuencia│
│ - activo    │
└─────────────┘
```

### 5. Relaciones de Compras y Logística

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   pedidos   │         │detalle_     │         │  entregas   │
│             │         │pedidos      │         │             │
│ - id        │         │             │         │ - id        │
│ - numero    │◄────────│ - pedido_id │────────▶│ - pedido_id │
│ - obra_id   │         │ - producto  │         │ - fecha     │
│ - proveedor │         │ - cantidad  │         │ - cantidad  │
│ - fecha     │         │ - precio    │         │ - estado    │
│ - estado    │         │ - subtotal  │         │ - recibido  │
│ - total     │         │             │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
       │
       │ (N:1)
       ▼
┌─────────────┐
│ transportes │
│             │
│ - id        │
│ - pedido_id │
│ - vehiculo  │
│ - conductor │
│ - fecha     │
│ - estado    │
│ - costo     │
└─────────────┘
```

## Relaciones entre Bases de Datos

### 1. Autenticación y Permisos (users ↔ inventario)

```
┌─────────────┐         ┌─────────────┐
│DB: users    │         │DB: inventario│
│             │         │             │
│┌───────────┐│  string │┌───────────┐│
││ usuarios  ││ usuario ││   obras   ││
││           ││────────▶││           ││
││- usuario  ││         ││- usuario_ ││
││- password ││         ││  creador  ││
││- rol      ││         ││           ││
│└───────────┘│         │└───────────┘│
│             │         │             │
│┌───────────┐│         │┌───────────┐│
││ permisos  ││         ││ empleados ││
││           ││         ││           ││
││- usuario  ││         ││- codigo   ││
││- modulo   ││         ││           ││
││- permiso  ││         ││           ││
│└───────────┘│         │└───────────┘│
└─────────────┘         └─────────────┘
```

### 2. Auditoría (inventario → auditoria)

```
┌─────────────┐         ┌─────────────┐
│DB: inventario│         │DB: auditoria│
│             │         │             │
│┌───────────┐│         │┌───────────┐│
││Cualquier  ││ Trigger ││ auditoria ││
││Cambio     ││────────▶││           ││
││en Tabla   ││         ││- usuario  ││
││           ││         ││- accion   ││
││           ││         ││- tabla    ││
││           ││         ││- valores  ││
│└───────────┘│         │└───────────┘│
│             │         │             │
│┌───────────┐│         │┌───────────┐│
││Login/     ││         ││log_accesos││
││Logout     ││────────▶││           ││
││Events     ││         ││- usuario  ││
││           ││         ││- exitoso  ││
││           ││         ││- fecha    ││
│└───────────┘│         │└───────────┘│
└─────────────┘         └─────────────┘
```

## Flujo de Datos Típico

### 1. Creación de Obra Completa

```
1. Login → users.usuarios
2. Crear obra → inventario.obras
3. Asignar herrajes → inventario.herrajes_por_obra
4. Asignar vidrios → inventario.vidrios_por_obra
5. Crear pedidos → inventario.pedidos
6. Registrar entregas → inventario.entregas
7. Actualizar stock → inventario.herrajes / inventario.vidrios
8. Auditar cambios → auditoria.auditoria
```

### 2. Gestión de Inventario

```
1. Verificar stock → inventario.herrajes / inventario.vidrios
2. Crear pedido → inventario.pedidos
3. Recibir mercancía → inventario.entregas
4. Actualizar stock → inventario.herrajes / inventario.vidrios
5. Notificar stock bajo → inventario.vw_InventarioBajoStock
```

### 3. Seguimiento de Equipos

```
1. Registrar equipo → inventario.equipos
2. Programar mantenimiento → inventario.programacion_mantenimiento
3. Ejecutar mantenimiento → inventario.mantenimientos
4. Actualizar historial → inventario.historial_mantenimiento
5. Cambiar estado → inventario.equipos.estado
```

## Índices Recomendados

### Índices de Rendimiento
```sql
-- Búsquedas frecuentes
CREATE INDEX IX_obras_estado ON obras(estado);
CREATE INDEX IX_obras_usuario_creador ON obras(usuario_creador);
CREATE INDEX IX_herrajes_categoria ON herrajes(categoria);
CREATE INDEX IX_vidrios_tipo ON vidrios(tipo);
CREATE INDEX IX_empleados_departamento ON empleados(departamento_id);
CREATE INDEX IX_equipos_estado ON equipos(estado);

-- Relaciones FK
CREATE INDEX IX_materiales_obra_obra_id ON materiales_obra(obra_id);
CREATE INDEX IX_herrajes_por_obra_obra_id ON herrajes_por_obra(obra_id);
CREATE INDEX IX_vidrios_por_obra_obra_id ON vidrios_por_obra(obra_id);
CREATE INDEX IX_pedidos_obra_id ON pedidos(obra_id);

-- Auditoría
CREATE INDEX IX_auditoria_usuario_fecha ON auditoria(usuario, fecha);
CREATE INDEX IX_log_accesos_usuario_fecha ON log_accesos(usuario, fecha);
```

### Índices de Integridad
```sql
-- Campos únicos
CREATE UNIQUE INDEX IX_herrajes_codigo ON herrajes(codigo);
CREATE UNIQUE INDEX IX_empleados_codigo ON empleados(codigo);
CREATE UNIQUE INDEX IX_equipos_codigo ON equipos(codigo);
CREATE UNIQUE INDEX IX_empleados_dni ON empleados(dni);

-- Campos de búsqueda
CREATE INDEX IX_herrajes_nombre ON herrajes(nombre);
CREATE INDEX IX_vidrios_color ON vidrios(color);
CREATE INDEX IX_empleados_apellido ON empleados(apellido);
```

## Consideraciones de Escalabilidad

### 1. Particionamiento
- Tabla `auditoria`: Por año/mes
- Tabla `log_accesos`: Por mes
- Tabla `historial_mantenimiento`: Por año

### 2. Archivado
- Auditorías > 2 años → tabla archivo
- Logs > 6 meses → tabla archivo
- Mantenimientos > 5 años → tabla archivo

### 3. Replicación
- DB `users`: Master-Slave para alta disponibilidad
- DB `inventario`: Master-Slave con réplicas de lectura
- DB `auditoria`: Solo escritura en master

Esta documentación sirve como guía para entender las relaciones y planificar futuras mejoras en el sistema.