# Configuración de Roles y Permisos de Usuario - Rexus.app

## 🎯 Sistema de Control de Acceso Basado en Roles (RBAC)

La aplicación Rexus.app implementa un sistema completo de control de acceso donde cada tipo de usuario tiene acceso solo a los módulos necesarios para su función.

---

## 👥 ROLES DE USUARIO CONFIGURADOS

### 🔧 1. ADMIN (Administrador)
**Descripción**: Administrador del sistema con acceso completo  
**Módulos disponibles**: **12 módulos (TODOS)**

✅ **Acceso completo a**:
- Inventario
- Administración  
- Obras
- Pedidos
- Logística (con mapa interactivo)
- Herrajes
- Vidrios
- Usuarios
- Auditoría
- Configuración
- Compras
- Mantenimiento

**Funciones típicas**:
- Gestión completa del sistema
- Configuración de usuarios y permisos
- Acceso a auditoría y logs
- Configuración del sistema
- Supervisión de todas las operaciones

---

### 👨‍💼 2. SUPERVISOR  
**Descripción**: Supervisor con permisos de gestión  
**Módulos disponibles**: **8 módulos**

✅ **Acceso a**:
- Inventario
- Obras
- Pedidos
- Logística
- Herrajes
- Vidrios
- Compras
- Mantenimiento

**Funciones típicas**:
- Supervisión de operaciones diarias
- Gestión de inventario y materiales
- Coordinación de obras y proyectos
- Supervisión de compras y pedidos

---

### 💰 3. CONTABILIDAD
**Descripción**: Especialista en contabilidad y finanzas  
**Módulos disponibles**: **7 módulos**

✅ **Acceso a**:
- Administración
- Compras
- Pedidos
- Obras
- Inventario
- Auditoría
- Usuarios

**Funciones típicas**:
- Gestión financiera y administrativa
- Control de compras y gastos  
- Auditoría de operaciones
- Gestión de usuarios relacionados con finanzas
- Análisis de costos de obras

---

### 📦 4. INVENTARIO
**Descripción**: Especialista en inventario y materiales  
**Módulos disponibles**: **7 módulos**

✅ **Acceso a**:
- Inventario
- Herrajes
- Vidrios
- Compras
- Pedidos
- Logística
- Mantenimiento

**Funciones típicas**:
- Gestión completa de stock
- Control de herrajes y vidrios
- Gestión de compras de materiales
- Coordinación logística de entregas
- Mantenimiento de equipos de almacén

---

### 🏗️ 5. OBRAS
**Descripción**: Especialista en obras y construcción  
**Módulos disponibles**: **7 módulos**

✅ **Acceso a**:
- Obras
- Inventario
- Herrajes
- Vidrios
- Pedidos
- Logística
- Mantenimiento

**Funciones típicas**:
- Gestión de proyectos de construcción
- Control de materiales para obras
- Pedidos específicos de obra
- Coordinación logística para sitios
- Mantenimiento de equipos de obra

---

### 👤 6. USUARIO
**Descripción**: Usuario básico con permisos limitados  
**Módulos disponibles**: **3 módulos**

✅ **Acceso de solo lectura a**:
- Inventario
- Obras
- Pedidos

**Funciones típicas**:
- Consulta de inventario disponible
- Visualización del estado de obras
- Consulta de pedidos realizados
- Sin permisos de modificación

---

## 🔐 MATRIZ DE PERMISOS POR MÓDULO

| Módulo         | ADMIN | SUPER | CONTA | INVEN | OBRAS | USUARIO |
|----------------|-------|-------|-------|-------|-------|---------|
| Inventario     | ✅    | ✅    | ✅    | ✅    | ✅    | ✅ (R)  |
| Administración | ✅    | ❌    | ✅    | ❌    | ❌    | ❌      |
| Obras          | ✅    | ✅    | ✅    | ❌    | ✅    | ✅ (R)  |
| Pedidos        | ✅    | ✅    | ✅    | ✅    | ✅    | ✅ (R)  |
| Logística      | ✅    | ✅    | ❌    | ✅    | ✅    | ❌      |
| Herrajes       | ✅    | ✅    | ❌    | ✅    | ✅    | ❌      |
| Vidrios        | ✅    | ✅    | ❌    | ✅    | ✅    | ❌      |
| Usuarios       | ✅    | ❌    | ✅    | ❌    | ❌    | ❌      |
| Auditoría      | ✅    | ❌    | ✅    | ❌    | ❌    | ❌      |
| Configuración  | ✅    | ❌    | ❌    | ❌    | ❌    | ❌      |
| Compras        | ✅    | ✅    | ✅    | ✅    | ❌    | ❌      |
| Mantenimiento  | ✅    | ✅    | ❌    | ✅    | ✅    | ❌      |

**Leyenda**: ✅ = Acceso completo, ✅ (R) = Solo lectura, ❌ = Sin acceso

---

## 🚀 IMPLEMENTACIÓN TÉCNICA

### Cómo funciona el sistema:

1. **Login de usuario**: El usuario se autentica con username/password
2. **Identificación de rol**: El sistema identifica el rol del usuario
3. **Asignación de módulos**: Se cargan solo los módulos permitidos para ese rol
4. **Interfaz personalizada**: El sidebar muestra únicamente los módulos accesibles

### Archivos involucrados:
- `rexus/core/security.py` - Lógica de permisos por rol
- `rexus/main/app.py` - Carga de módulos según permisos
- `rexus/core/auth.py` - Sistema de autenticación

---

## 📝 USUARIOS DE EJEMPLO

Para probar cada rol, se pueden crear usuarios con estos roles:

```sql
-- Usuarios de ejemplo (en la base de datos 'users')
INSERT INTO usuarios (username, password_hash, rol, activo) VALUES 
('admin', '[hash]', 'ADMIN', 1),
('supervisor', '[hash]', 'SUPERVISOR', 1),
('contabilidad', '[hash]', 'CONTABILIDAD', 1),
('inventario', '[hash]', 'INVENTARIO', 1),
('obras', '[hash]', 'OBRAS', 1),
('usuario', '[hash]', 'USUARIO', 1);
```

---

## 🔧 PERSONALIZACIÓN DE ROLES

### Para modificar permisos de un rol:

1. **Editar** `rexus/core/security.py`
2. **Encontrar** el método `get_user_modules()`
3. **Modificar** la lista de módulos para el rol deseado
4. **Reiniciar** la aplicación

### Ejemplo - Agregar módulo "Auditoría" al SUPERVISOR:
```python
elif self.current_role in ['supervisor', 'SUPERVISOR']:
    return [
        "Inventario", "Obras", "Pedidos", "Logística", 
        "Herrajes", "Vidrios", "Compras", "Mantenimiento",
        "Auditoría"  # <- Módulo agregado
    ]
```

---

## ✅ VERIFICACIÓN DEL SISTEMA

### Para verificar que los roles funcionan correctamente:

1. **Ejecutar test**:
   ```bash
   python test_user_roles_permissions.py
   ```

2. **Resultado esperado**:
   ```
   ADMIN: 12 modules - OK
   SUPERVISOR: 8 modules - OK  
   CONTABILIDAD: 7 modules - OK
   INVENTARIO: 7 modules - OK
   OBRAS: 7 modules - OK
   USUARIO: 3 modules - OK
   ```

3. **Login con diferentes usuarios** y verificar que solo aparezcan los módulos correspondientes

---

## 🎯 BENEFICIOS DEL SISTEMA

✅ **Seguridad**: Cada usuario ve solo lo que necesita  
✅ **Eficiencia**: Interfaz limpia y enfocada por rol  
✅ **Control**: Administrador tiene control total sobre accesos  
✅ **Escalabilidad**: Fácil agregar nuevos roles o modificar existentes  
✅ **Auditoría**: Registro de acciones por rol de usuario  

---

**El sistema de roles está completamente configurado y funcional. Cada usuario verá únicamente los módulos apropiados para su función en la empresa.**