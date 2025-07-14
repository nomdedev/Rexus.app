# 🎉 MANUAL DE USUARIO - SISTEMA COMPLETO

## 🚀 INICIO DE SESIÓN

### Credenciales Disponibles:

1. **ADMINISTRADOR** (Acceso Completo)
   - Usuario: `admin`
   - Contraseña: `admin`
   - Acceso: Todos los 12 módulos + Gestión de permisos

2. **USUARIOS NORMALES** (Acceso Limitado)
   - Usuario: `usuario` / Contraseña: `demo`
   - Usuario: `prueba` / Contraseña: `1`

---

## 🛡️ GESTIÓN DE PERMISOS (Solo Admin)

### Pasos para Gestionar Permisos:

1. **Inicia sesión como admin** (`admin` / `admin`)
2. **Ve al módulo "Usuarios"** en el sidebar
3. **Selecciona la pestaña "Permisos de módulos"**
4. **Selecciona un usuario** del combo desplegable
5. **Marca/desmarca los módulos** que deseas permitir
6. **Haz clic en "Guardar permisos"**

### Reglas del Sistema:
- ✅ **Máximo 12 módulos por usuario** (todos los disponibles)
- ✅ **Admin SIEMPRE tiene acceso completo** (no modificable)
- ✅ **No duplicación de permisos** (sistema automático)
- ✅ **Auditoría completa** de todos los cambios

### Módulos Disponibles:
1. **Obras** - Gestión de proyectos y obras
2. **Inventario** - Control de stock y materiales
3. **Herrajes** - Gestión de herrajes específicos
4. **Compras / Pedidos** - Gestión de compras y pedidos
5. **Logística** - Control logístico y distribución
6. **Vidrios** - Gestión específica de vidrios
7. **Mantenimiento** - Mantenimiento de equipos
8. **Producción** - Control de producción
9. **Contabilidad** - Gestión contable
10. **Auditoría** - Registro de eventos del sistema
11. **Usuarios** - Gestión de usuarios (solo admin)
12. **Configuración** - Configuración del sistema

---

## 📊 INTERFAZ DE USUARIO

### Características:
- **Sidebar Inteligente** - Solo muestra módulos permitidos
- **Header Moderno** - Búsqueda, notificaciones, perfil, tema
- **Feedback Visual** - Confirmaciones y mensajes claros
- **Status Bar** - Información del usuario actual
- **Diseño Responsivo** - Se adapta al tamaño de ventana

### Navegación:
- **Clic en sidebar** - Cambiar entre módulos
- **Indicador de usuario** - Muestra usuario actual y rol
- **Mensajes de estado** - Confirmaciones en la barra inferior

---

## 🔧 FUNCIONALIDADES TÉCNICAS

### Para ADMIN:
- ✅ **Gestión completa de usuarios** (crear, editar, suspender)
- ✅ **Asignación de permisos** por módulo
- ✅ **Acceso a auditoría** completa del sistema
- ✅ **Configuración avanzada** del sistema
- ✅ **Vista de resumen** de permisos por usuario

### Para USUARIOS:
- ✅ **Acceso a módulos asignados** únicamente
- ✅ **Interfaz limpia** sin opciones no permitidas
- ✅ **Configuración básica** siempre disponible
- ✅ **Feedback claro** de permisos limitados

---

## 🛠️ SOLUCIÓN DE PROBLEMAS

### Si el botón "Ingresar" no funciona:
1. Verifica las credenciales correctas
2. Asegúrate de que la base de datos esté conectada
3. Revisa los logs en la carpeta `logs/`

### Si no ves todos los módulos:
1. Verifica tu rol de usuario
2. Contacta al administrador para asignar permisos
3. Los usuarios normales tienen máximo 12 módulos

### Si eres admin y no puedes gestionar permisos:
1. Verifica que estés logueado como `admin`
2. Ve al módulo "Usuarios" → pestaña "Permisos de módulos"
3. La pestaña solo es visible para usuarios admin

---

## 🎯 PRUEBAS RECOMENDADAS

### 1. Prueba de Login Admin:
- Inicia sesión como `admin` / `admin`
- Verifica que veas todos los 12 módulos
- Ve a "Usuarios" → "Permisos de módulos"

### 2. Prueba de Gestión de Permisos:
- Selecciona un usuario normal
- Modifica sus permisos
- Guarda y verifica el mensaje de confirmación

### 3. Prueba de Usuario Normal:
- Inicia sesión como `usuario` / `demo`
- Verifica que solo veas módulos asignados
- No deberías ver la pestaña de gestión de permisos

---

## 📈 ESTADO DEL SISTEMA

```
✅ LOGIN FUNCIONAL - Botón "Ingresar" operativo
✅ PERMISOS CONFIGURADOS - Máximo 12 módulos por usuario
✅ ADMIN COMPLETO - Acceso total para administradores
✅ INTERFACE MODERNA - Diseño profesional y responsive
✅ AUDITORÍA ACTIVA - Registro de todos los cambios
✅ BASE NORMALIZADA - Sin duplicados ni inconsistencias
```

---

## 🎊 ¡EL SISTEMA ESTÁ COMPLETO Y FUNCIONAL!

**Para comenzar:** Ejecuta `python main.py` y usa las credenciales proporcionadas.

**Para soporte:** Revisa los logs en la carpeta `logs/` o consulta la documentación técnica en `RESUMEN_IMPLEMENTACION.md`.

¡Disfruta usando el sistema! 🚀
