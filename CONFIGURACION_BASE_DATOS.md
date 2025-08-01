# Configuración de Base de Datos - Rexus.app

## 🎯 Problema Identificado

La aplicación no puede mostrar todos los módulos correctamente porque **faltan las variables de entorno** para la conexión a la base de datos. 

### Síntomas actuales:
- ❌ Solo se ven algunos módulos (Inventario, Obras, Pedidos)
- ❌ El mapa interactivo no se muestra
- ❌ Los módulos fallan al cargar porque no pueden conectarse a la BD
- ⚠️ La aplicación funciona en "modo demo" sin datos reales

## 🔧 Solución: Configurar Variables de Entorno

### 1. Crear archivo `.env`

Crea un archivo llamado `.env` en la raíz del proyecto (`C:\Users\Oficina\Documents\Proyectos\Apps\Rexus.app\.env`) con el siguiente contenido:

```env
# Configuración del servidor de base de datos
DB_SERVER=DESKTOP-QHMPTGO\\SQLEXPRESS
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_USERNAME=sa
DB_PASSWORD=tu_contraseña_aqui

# Bases de datos específicas
DB_USERS=users
DB_INVENTARIO=inventario  
DB_AUDITORIA=auditoria

# Configuración adicional de seguridad
FALLBACK_ADMIN_PASSWORD=admin
```

### 2. Configurar las contraseñas correctas

**IMPORTANTE**: Reemplaza `tu_contraseña_aqui` con la contraseña real de tu SQL Server.

### 3. Verificar que las bases de datos existen

Asegúrate de que las siguientes bases de datos existen en tu SQL Server:
- `users` - Para usuarios y permisos
- `inventario` - Para datos de inventario, obras, herrajes, vidrios, etc.
- `auditoria` - Para logs y trazabilidad

## 🚀 Resultado Esperado

Una vez configuradas las variables de entorno, la aplicación debería:

✅ **Conectarse correctamente a la base de datos**  
✅ **Cargar todos los 12 módulos para el usuario admin**:
- Inventario
- Obras  
- Herrajes
- Vidrios
- Logística (con mapa interactivo)
- Pedidos
- Compras
- Administración
- Mantenimiento
- Auditoría
- Usuarios
- Configuración

✅ **Mostrar el mapa interactivo en el módulo de Logística**  
✅ **Usar datos reales de la base de datos**  
✅ **Sistema de permisos funcionando correctamente**

## 🔍 Verificación

Para verificar que todo funciona:

1. **Ejecutar test de conexión**:
```bash
python test_user_permissions_db.py
```

2. **Verificar que aparecen estos mensajes**:
```
✅ Users DB: Connected
✅ Users DB: Connection active  
✅ Admin login: SUCCESS
✅ Modules for admin: 12
```

3. **Ejecutar la aplicación principal**:
```bash
python main.py
```

4. **Login con admin/admin**

5. **Verificar que se ven todos los módulos en el sidebar**

## 🛠️ Alternativa: Modo Demo Mejorado

Si no puedes configurar la base de datos, hemos mejorado el sistema para que funcione mejor en modo demo:

- ✅ Usuario admin/admin funciona sin BD
- ✅ Todos los módulos son accesibles  
- ✅ El mapa interactivo funciona
- ℹ️ Los datos son de demostración

## 📋 Checklist de Verificación

- [ ] Archivo `.env` creado con variables correctas
- [ ] Contraseña de BD configurada correctamente  
- [ ] Bases de datos `users`, `inventario`, `auditoria` existen
- [ ] Test de conexión pasa exitosamente
- [ ] Login admin/admin funciona
- [ ] Se ven todos los 12 módulos en el sidebar
- [ ] El mapa se muestra en el módulo de Logística
- [ ] Los datos se cargan desde la base de datos real

## 🚨 Solución de Problemas

### Problema: "No se encuentra el nombre del origen de datos"
**Solución**: Verifica que `ODBC Driver 17 for SQL Server` esté instalado en tu sistema.

### Problema: "Login failed for user 'sa'"  
**Solución**: Verifica que la contraseña en `.env` sea correcta y que el usuario `sa` esté habilitado.

### Problema: "Database does not exist"
**Solución**: Crea las bases de datos `users`, `inventario`, `auditoria` en SQL Server Management Studio.

### Problema: Módulos siguen sin aparecer
**Solución**: 
1. Reinicia la aplicación completamente
2. Verifica los logs en consola para errores específicos
3. Ejecuta `test_user_permissions_db.py` para diagnosticar

---

**Una vez configurado correctamente, tendrás acceso completo a todos los módulos con el usuario admin, incluyendo el mapa interactivo en Logística.**