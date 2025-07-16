# Documentación del Esquema de Base de Datos - Rexus.app

## Resumen General

El sistema Rexus.app utiliza una arquitectura de **tres bases de datos separadas** por razones de seguridad y organización:

- **`users`** - Gestión de usuarios, autenticación y permisos
- **`inventario`** - Datos operativos del negocio (obras, materiales, empleados, equipos)
- **`auditoria`** - Trazabilidad y logs del sistema

## Base de Datos: `users`

### Propósito
Manejo exclusivo de autenticación, usuarios y permisos del sistema.

### Tablas Principales

#### `usuarios`
```sql
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    rol VARCHAR(50) NOT NULL DEFAULT 'usuario',
    departamento VARCHAR(100),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
    ultimo_login DATETIME,
    intentos_fallidos INT DEFAULT 0,
    bloqueado BIT DEFAULT 0,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_actualizacion DATETIME DEFAULT GETDATE()
)
```

**Propósito**: Almacena información de usuarios del sistema
**Roles disponibles**: `admin`, `supervisor`, `usuario`
**Relaciones**: Se conecta con otras tablas mediante el campo `usuario` (string)

#### `permisos`
```sql
CREATE TABLE permisos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    permiso VARCHAR(50) NOT NULL,
    concedido BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
```

**Propósito**: Define permisos granulares por usuario y módulo
**Módulos**: `inventario`, `obras`, `herrajes`, `vidrios`, `empleados`, `equipos`, `compras`, `administracion`

#### `sesiones`
```sql
CREATE TABLE sesiones (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    fecha_inicio DATETIME DEFAULT GETDATE(),
    fecha_expiracion DATETIME,
    activa BIT DEFAULT 1,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
```

**Propósito**: Manejo de sesiones activas y tokens de autenticación

## Base de Datos: `inventario`

### Propósito
Contiene todos los datos operativos del negocio: obras, materiales, empleados, equipos, etc.

### Tablas Principales

#### `obras`
```sql
-- Columnas existentes basadas en análisis:
id INT IDENTITY(1,1) PRIMARY KEY,
nombre VARCHAR(300) NOT NULL,
direccion VARCHAR(400),
telefono VARCHAR(20),
fecha_creacion DATETIME DEFAULT GETDATE(),
cliente VARCHAR(200) NOT NULL,
estado VARCHAR(50) DEFAULT 'Planificada',
fecha DATE,
fecha_entrega DATE,
cantidad_aberturas INT,
fecha_compra DATE,
pago_completo BIT,
pago_porcentaje DECIMAL(5,2),
monto_usd DECIMAL(15,2),
monto_ars DECIMAL(15,2),
tipo_obra VARCHAR(100),
usuario_creador VARCHAR(50),
fecha_medicion DATE,
dias_entrega INT,
rowversion TIMESTAMP
```

**Propósito**: Gestión de obras y proyectos
**Estados**: `Planificada`, `En Proceso`, `Activa`, `Finalizada`, `Cancelada`
**Relaciones**: 
- Se conecta con `usuarios` mediante `usuario_creador`
- Es referenciada por `materiales_obra`, `vidrios_por_obra`, `herrajes_por_obra`

#### `herrajes`
```sql
-- Columnas existentes:
id INT IDENTITY(1,1) PRIMARY KEY,
codigo VARCHAR(50) NOT NULL UNIQUE,
nombre VARCHAR(300) NOT NULL,
descripcion TEXT,
categoria VARCHAR(100),
proveedor VARCHAR(200),
precio_unitario DECIMAL(10,2),
stock_actual INT DEFAULT 0,
stock_minimo INT DEFAULT 0,
unidad_medida VARCHAR(20),
especificaciones TEXT,
imagen_url VARCHAR(500),
activo BIT DEFAULT 1,
fecha_creacion DATETIME DEFAULT GETDATE(),
fecha_actualizacion DATETIME DEFAULT GETDATE()
```

**Propósito**: Gestión de herrajes y accesorios
**Categorías**: `Bisagras`, `Cerraduras`, `Manijas`, `Aldabas`, `Candados`, `Rieles`, `Tornilleria`, `Picaportes`
**Relaciones**: 
- Se conecta con `proveedores` mediante `proveedor`
- Es referenciada por `herrajes_por_obra`

#### `vidrios`
```sql
-- Columnas existentes:
id INT IDENTITY(1,1) PRIMARY KEY,
tipo VARCHAR(100) NOT NULL,
espesor DECIMAL(5,2),
color VARCHAR(50),
precio_m2 DECIMAL(10,2),
proveedor VARCHAR(200),
especificaciones TEXT,
propiedades TEXT,
activo BIT DEFAULT 1,
fecha_creacion DATETIME DEFAULT GETDATE(),
fecha_actualizacion DATETIME DEFAULT GETDATE()
```

**Propósito**: Gestión de vidrios y cristales
**Tipos**: `Templado`, `Laminado`, `Común`, `Esmerilado`, `Tintado`, `Espejo`, `Doble`, `Decorativo`
**Relaciones**: 
- Se conecta con `proveedores` mediante `proveedor`
- Es referenciada por `vidrios_por_obra`, `vidrios_medidas`

#### `empleados`
```sql
-- Columnas existentes:
id INT IDENTITY(1,1) PRIMARY KEY,
codigo VARCHAR(50) NOT NULL UNIQUE,
nombre VARCHAR(100) NOT NULL,
apellido VARCHAR(100) NOT NULL,
dni VARCHAR(20) UNIQUE,
telefono VARCHAR(20),
email VARCHAR(100),
direccion VARCHAR(300),
fecha_nacimiento DATE,
fecha_ingreso DATE,
salario_base DECIMAL(10,2),
cargo VARCHAR(100),
departamento_id INT,
estado VARCHAR(20) DEFAULT 'Activo',
activo BIT DEFAULT 1,
fecha_creacion DATETIME DEFAULT GETDATE(),
fecha_modificacion DATETIME DEFAULT GETDATE()
```

**Propósito**: Gestión de empleados y recursos humanos
**Estados**: `Activo`, `Inactivo`, `Vacaciones`, `Licencia`
**Relaciones**: 
- Se conecta con `departamentos` mediante `departamento_id`
- Es referenciada por `asistencias`, `nomina`, `historial_laboral`

#### `equipos`
```sql
-- Columnas existentes:
id INT IDENTITY(1,1) PRIMARY KEY,
codigo VARCHAR(50) NOT NULL UNIQUE,
nombre VARCHAR(300) NOT NULL,
tipo VARCHAR(100),
modelo VARCHAR(100),
marca VARCHAR(100),
numero_serie VARCHAR(100),
fecha_adquisicion DATE,
fecha_instalacion DATE,
ubicacion VARCHAR(100),
estado VARCHAR(50) DEFAULT 'Operativo',
valor_adquisicion DECIMAL(12,2),
vida_util_anos INT,
ultima_revision DATE,
proxima_revision DATE,
observaciones TEXT,
activo BIT DEFAULT 1,
fecha_creacion DATETIME DEFAULT GETDATE(),
fecha_modificacion DATETIME DEFAULT GETDATE()
```

**Propósito**: Gestión de equipos y maquinaria
**Estados**: `Operativo`, `Mantenimiento`, `Fuera de Servicio`, `En Reparación`
**Relaciones**: 
- Es referenciada por `mantenimientos`, `historial_mantenimiento`

#### `proveedores`
```sql
-- Columnas existentes:
id INT IDENTITY(1,1) PRIMARY KEY,
nombre VARCHAR(200) NOT NULL,
contacto VARCHAR(100),
telefono VARCHAR(20),
email VARCHAR(100),
direccion VARCHAR(300)
```

**Propósito**: Gestión de proveedores y contactos
**Relaciones**: 
- Es referenciada por `herrajes`, `vidrios`, `pedidos`, `materiales_proveedores`

#### `pedidos`
```sql
-- Estructura inferida:
id INT IDENTITY(1,1) PRIMARY KEY,
numero_pedido VARCHAR(50) NOT NULL UNIQUE,
obra_id INT,
proveedor_id INT,
fecha_pedido DATE,
fecha_entrega_estimada DATE,
fecha_entrega_real DATE,
estado VARCHAR(50) DEFAULT 'Pendiente',
subtotal DECIMAL(12,2),
impuestos DECIMAL(12,2),
total DECIMAL(12,2),
usuario_solicita VARCHAR(50),
observaciones TEXT,
fecha_creacion DATETIME DEFAULT GETDATE()
```

**Propósito**: Gestión de pedidos a proveedores
**Estados**: `Pendiente`, `Aprobado`, `En Proceso`, `Entregado`, `Cancelado`
**Relaciones**: 
- Se conecta con `obras` mediante `obra_id`
- Se conecta con `proveedores` mediante `proveedor_id`
- Es referenciada por `detalle_pedidos`

### Tablas de Relación (Junction Tables)

#### `materiales_obra`
**Propósito**: Relaciona obras con materiales de inventario
**Campos clave**: `obra_id`, `material_id`, `cantidad_requerida`, `cantidad_asignada`

#### `herrajes_por_obra`
**Propósito**: Relaciona obras con herrajes específicos
**Campos clave**: `obra_id`, `herraje_id`, `cantidad`, `precio_unitario`

#### `vidrios_por_obra`
**Propósito**: Relaciona obras con vidrios específicos
**Campos clave**: `obra_id`, `vidrio_id`, `metros_cuadrados`, `precio_m2`

#### `vidrios_medidas`
**Propósito**: Almacena medidas específicas de vidrios por obra
**Campos clave**: `obra_id`, `vidrio_id`, `ancho`, `alto`, `cantidad`

### Tablas de Soporte

#### `departamentos`
**Propósito**: Catalogar departamentos de la empresa
**Relaciones**: Es referenciada por `empleados`

#### `clientes`
**Propósito**: Gestión de clientes (separada de obras)
**Relaciones**: Puede conectarse con `obras` mediante `cliente`

#### `transportes`
**Propósito**: Gestión de logística y transporte
**Relaciones**: Se conecta con `obras` y `pedidos`

#### `nomina`
**Propósito**: Gestión de nóminas y pagos
**Relaciones**: Se conecta con `empleados`

## Base de Datos: `auditoria`

### Propósito
Registro de trazabilidad y logs del sistema para seguridad y cumplimiento.

### Tablas Principales

#### `auditoria`
```sql
CREATE TABLE auditoria (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    accion VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100),
    registro_id INT,
    valores_anteriores TEXT,
    valores_nuevos TEXT,
    fecha DATETIME DEFAULT GETDATE(),
    ip_address VARCHAR(45),
    detalles TEXT
)
```

**Propósito**: Registro de cambios en datos críticos
**Acciones**: `INSERT`, `UPDATE`, `DELETE`, `LOGIN`, `LOGOUT`

#### `log_accesos`
```sql
CREATE TABLE log_accesos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    exitoso BIT DEFAULT 1,
    fecha DATETIME DEFAULT GETDATE(),
    ip_address VARCHAR(45),
    user_agent TEXT,
    mensaje TEXT
)
```

**Propósito**: Registro de intentos de acceso y login

## Flujo de Datos entre Bases de Datos

### 1. Autenticación
```
users.usuarios → validación → session token → acceso a inventario
```

### 2. Flujo de Obra Completa
```
users.usuarios (creador) → 
inventario.obras → 
inventario.materiales_obra + inventario.herrajes_por_obra + inventario.vidrios_por_obra →
inventario.pedidos → 
inventario.proveedores
```

### 3. Auditoría
```
Cualquier cambio en inventario → auditoria.auditoria
Login/Logout → auditoria.log_accesos
```

## Vistas Importantes

### `vw_ResumenObrasPendientes`
**Propósito**: Vista consolidada de obras pendientes con materiales
**Fuentes**: `obras`, `materiales_obra`, `herrajes_por_obra`, `vidrios_por_obra`

### `vw_InventarioBajoStock`
**Propósito**: Vista de items con stock bajo el mínimo
**Fuentes**: `inventario`, `herrajes`, `vidrios`

### `v_estado_materiales_obra`
**Propósito**: Estado consolidado de materiales por obra
**Fuentes**: `obras`, `materiales_obra`, `inventario`

### `v_estado_vidrios_obra`
**Propósito**: Estado consolidado de vidrios por obra
**Fuentes**: `obras`, `vidrios_por_obra`, `vidrios`

### `v_estado_pagos_obra`
**Propósito**: Estado consolidado de pagos por obra
**Fuentes**: `obras`, `pagos_obra`, `pagos_materiales`

## Consideraciones de Seguridad

### Separación de Responsabilidades
- **users**: Solo login y permisos
- **inventario**: Solo datos operativos  
- **auditoria**: Solo logs (escritura)

### Conexiones
- La aplicación debe conectarse a `users` para autenticación
- Post-login, usar `inventario` para operaciones
- Los logs se escriben automáticamente a `auditoria`

### Permisos de Base de Datos
- Usuario de aplicación: CRUD en `inventario`, SELECT en `users`, INSERT en `auditoria`
- Usuario de admin: Full access a todas las bases
- Usuario de auditor: SELECT en `auditoria`

## Mejoras Futuras Recomendadas

### 1. Normalización
- Crear tabla `categorias_herrajes` para normalizar categorías
- Crear tabla `tipos_vidrios` para normalizar tipos
- Crear tabla `estados_obra` para normalizar estados

### 2. Relaciones Faltantes
- Agregar foreign keys explícitas donde sea posible
- Crear índices en campos de búsqueda frecuente
- Implementar constraints de integridad referencial

### 3. Campos Adicionales
- Agregar campos de auditoría (`created_by`, `modified_by`) en todas las tablas
- Implementar soft deletes con campo `deleted_at`
- Agregar campos de versioning para control de cambios

### 4. Optimización
- Implementar particionamiento en tablas de auditoría
- Crear índices compuestos para consultas frecuentes
- Implementar archivado automático de registros antiguos

## Datos de Prueba Poblados

El sistema incluye datos de prueba completos:

### Usuarios
- **admin/admin123**: Acceso completo
- **supervisor/super123**: Gestión de obras
- **compras/comp123**: Gestión de compras
- **almacen/alm123**: Gestión de inventario

### Datos Operativos
- **8 obras** con diferentes estados
- **10 herrajes** con stock y precios
- **10 vidrios** con especificaciones
- **10 empleados** con información completa
- **10 equipos** con seguimiento de mantenimiento
- **10 proveedores** activos

### Relaciones
- Obras asignadas a usuarios responsables
- Materiales asignados a obras específicas
- Proveedores vinculados a materiales
- Empleados asignados a departamentos

## Comandos Útiles para Desarrollo

### Verificar Estructura
```sql
-- Listar todas las tablas
SELECT table_name FROM information_schema.tables WHERE table_schema = 'dbo'

-- Ver estructura de una tabla
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'nombre_tabla'

-- Ver relaciones
SELECT * FROM information_schema.key_column_usage
```

### Consultas de Negocio
```sql
-- Obras con materiales asignados
SELECT o.nombre, COUNT(mo.id) as materiales_asignados
FROM obras o
LEFT JOIN materiales_obra mo ON o.id = mo.obra_id
GROUP BY o.id, o.nombre

-- Stock bajo mínimo
SELECT nombre, stock_actual, stock_minimo
FROM herrajes
WHERE stock_actual <= stock_minimo

-- Proveedores más utilizados
SELECT p.nombre, COUNT(h.id) as productos_suministrados
FROM proveedores p
LEFT JOIN herrajes h ON p.nombre = h.proveedor
GROUP BY p.nombre
ORDER BY productos_suministrados DESC
```

Esta documentación debe actualizarse cada vez que se modifique el esquema de la base de datos.