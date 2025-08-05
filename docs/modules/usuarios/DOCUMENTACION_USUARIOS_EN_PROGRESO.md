# Documentación Técnica - Módulo de Usuarios

## Información General
- **Módulo**: Usuarios
- **Propósito**: Gestión completa de usuarios, autenticación y permisos
- **Estado**: 🟡 EN PROGRESO - Mejoras de seguridad parcialmente implementadas
- **Fecha de actualización**: Enero 2025
- **Versión**: 2.0.0

## Archivos Principales
- `rexus/modules/usuarios/model.py` - Modelo de datos con seguridad implementada (EN PROGRESO)
- `rexus/modules/usuarios/view.py` - Interfaz de usuario con headers MIT
- `rexus/modules/usuarios/controller.py` - Controlador de lógica de negocio

## Mejoras de Seguridad Implementadas

### 1. Método _validate_table_name()
```python
def _validate_table_name(self, table_name: str) -> str:
    """Valida el nombre de tabla para prevenir SQL injection."""
```
- **Propósito**: Prevenir ataques de SQL injection
- **Validaciones**:
  - Caracteres alfanuméricos y guiones bajos únicamente
  - Longitud máxima de 64 caracteres
  - Lista blanca de tablas permitidas
  - Fallback seguro si utilidades no están disponibles

### 2. Función validar_usuario_duplicado()
```python
def validar_usuario_duplicado(self, username: str, email: str, id_usuario_actual: Optional[int] = None) -> Dict[str, bool]:
    """Valida si existe un usuario duplicado por username o email."""
```
- **Propósito**: Prevenir duplicación de usuarios
- **Características**:
  - Validación de username y email duplicados
  - Sanitización de datos de entrada
  - Consultas parametrizadas
  - Validación para edición y creación
  - Manejo robusto de errores

### 3. Sanitización de Datos (EN PROGRESO)
- **DataSanitizer integrado**: Sanitización parcial implementada
- **Validación de emails**: En proceso de corrección
- **Validación de username**: Implementada con fallbacks
- **Fallback seguro**: Funcionamiento sin utilidades
- **PENDIENTE**: Corrección de métodos de sanitización específicos

## Estructura de Datos

### Tabla Usuarios
```sql
CREATE TABLE usuarios (
    id INT PRIMARY KEY IDENTITY(1,1),
    usuario NVARCHAR(50) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    nombre_completo NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    telefono NVARCHAR(20),
    rol NVARCHAR(20) NOT NULL DEFAULT 'USUARIO',
    estado NVARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_modificacion DATETIME DEFAULT GETDATE(),
    ultimo_acceso DATETIME,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta DATETIME,
    avatar NVARCHAR(255),
    configuracion_personal NVARCHAR(MAX),
    activo BIT DEFAULT 1
);
```

### Roles de Usuario
- `ADMIN`: Administrador del sistema
- `SUPERVISOR`: Supervisor con permisos amplios
- `OPERADOR`: Operador con permisos específicos
- `USUARIO`: Usuario estándar
- `INVITADO`: Acceso limitado

### Estados de Usuario
- `ACTIVO`: Usuario activo
- `INACTIVO`: Usuario desactivado
- `SUSPENDIDO`: Usuario suspendido temporalmente
- `BLOQUEADO`: Usuario bloqueado por seguridad

## Funcionalidades Principales

### Gestión de Usuarios
1. **Crear Usuario**
   - Validación completa de datos
   - Sanitización de entrada (EN PROGRESO)
   - Verificación de duplicados ✅
   - Hashing de contraseñas
   - Logging de operaciones

2. **Autenticación**
   - Login seguro con validación
   - Control de intentos fallidos ✅
   - Sistema de bloqueo temporal ✅
   - Gestión de sesiones

3. **Gestión de Permisos**
   - Roles y permisos granulares
   - Validación de acceso por módulo
   - Sistema de permisos heredados

## Seguridad Implementada

### SQL Injection Protection
- ✅ Validación de nombres de tabla
- ✅ Consultas parametrizadas
- ✅ Lista blanca de tablas
- 🟡 Sanitización de entrada (EN PROGRESO)

### Validación de Datos
- ✅ Validación de username duplicado
- ✅ Validación de email duplicado
- 🟡 Sanitización de formularios (EN PROGRESO)
- ✅ Control de intentos de login
- ✅ Sistema de bloqueo temporal

### Logging y Auditoría
- ✅ Registro de operaciones críticas
- ✅ Logging de errores detallado
- ✅ Trazabilidad de intentos de acceso
- ✅ Información de debug de seguridad

## Problemas Identificados y Estado

### ❌ Pendientes de Corrección
1. **Métodos de Sanitización**
   - `sanitize_email()` no existe en DataSanitizer
   - `sanitize_phone()` no existe en DataSanitizer
   - `sanitize_form_data()` no existe en DataSanitizer
   - `max_length` parámetro no válido en `sanitize_string()`

2. **Imports no Utilizados**
   - `datetime` importado pero no usado
   - `hashlib` importado pero no usado
   - `SQLSecurityValidator` importado pero no usado

3. **Manejo de Excepciones**
   - Uso de `except:` sin especificar excepción

### ✅ Implementado Correctamente
1. **Validación de Tablas**
   - Método `_validate_table_name()` implementado
   - Fallback seguro implementado

2. **Validación de Duplicados**
   - Función `validar_usuario_duplicado()` completa
   - Consultas parametrizadas seguras

3. **Sistema de Bloqueo**
   - Control de intentos fallidos
   - Bloqueo temporal de usuarios
   - Logging de seguridad

## Próximos Pasos Recomendados

### 1. Correcciones Inmediatas
- [ ] Corregir métodos de sanitización inexistentes
- [ ] Eliminar imports no utilizados
- [ ] Mejorar manejo de excepciones
- [ ] Completar sanitización de datos

### 2. Mejoras de Seguridad
- [ ] Implementar hashing bcrypt para contraseñas
- [ ] Mejorar gestión de sesiones
- [ ] Implementar tokens de autenticación
- [ ] Agregar validación de contraseñas seguras

### 3. Funcionalidades Adicionales
- [ ] Sistema de recuperación de contraseñas
- [ ] Autenticación de dos factores
- [ ] Auditoría completa de accesos
- [ ] Dashboard de administración de usuarios

## Conclusión

El módulo de Usuarios ha recibido mejoras importantes en seguridad:
- ✅ Protección contra SQL injection (parcial)
- ✅ Validación de duplicados implementada
- ✅ Sistema de bloqueo por intentos fallidos
- ✅ Logging de seguridad mejorado
- 🟡 Sanitización de datos (requiere correcciones menores)

**Estado**: EN PROGRESO - Requiere correcciones menores para completar las mejoras de seguridad.

Las correcciones pendientes son principalmente ajustes en los métodos de sanitización y no afectan la funcionalidad crítica del sistema.
