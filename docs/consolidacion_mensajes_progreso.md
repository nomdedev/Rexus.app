# Consolidación de Mensajes de Error - Progreso

## Estado: PARCIALMENTE COMPLETADO

### Constantes Agregadas a usuarios/constants.py

✅ **Nuevas constantes de error creadas:**
- MSG_ERROR_2FA_* (4 constantes para errores de 2FA)
- MSG_ERROR_BD_* (3 constantes para errores de BD)
- MSG_ERROR_SEGURIDAD_* (4 constantes para errores de seguridad)
- MSG_ERROR_PASSWORD_* (3 constantes para validación de contraseñas)
- TITULO_ERROR, TITULO_ADVERTENCIA, TITULO_CONFIRMACION, TITULO_EXITO

### Archivos Parcialmente Migrados

#### ✅ view.py (2/4 mensajes migrados)
- ✅ "Error al buscar usuarios" → MSG_ERROR_BUSCAR_USUARIOS
- ✅ "Error" → TITULO_ERROR

#### ✅ security_dialog.py (4/12 mensajes migrados)
- ✅ "Error generando 2FA" → MSG_ERROR_2FA_GENERAR
- ✅ "Ingrese un código de 6 dígitos" → MSG_ERROR_2FA_CODIGO_FORMATO
- ✅ "Código incorrecto..." → MSG_ERROR_2FA_CODIGO_INVALIDO
- ✅ "Error verificando 2FA" → MSG_ERROR_2FA_VERIFICAR

### Pendientes por Migrar

#### controller.py
- "Error de base de datos cargando usuarios"
- "Error buscando usuarios"
- "Error creando usuario" (ya existe constante)
- Múltiples mensajes de error de operaciones CRUD

#### security_dialog.py (8 restantes)
- "Error cargando estado de seguridad"
- "Error deshabilitando 2FA"
- "Error desbloqueando cuenta"
- "Ingrese su contraseña actual"
- "Las contraseñas no coinciden"
- "Contraseña actual incorrecta"

#### improved_dialogs.py
- Múltiples mensajes "Error" hardcodeados

#### model.py
- Ya usa logging, pero puede beneficiarse de constantes para logs específicos

### Patrón de Migración

```python
# ANTES:
QMessageBox.warning(self, "Error", "Error al buscar usuarios")

# DESPUÉS:
from .constants import UsuariosConstants
QMessageBox.warning(self, UsuariosConstants.TITULO_ERROR, UsuariosConstants.MSG_ERROR_BUSCAR_USUARIOS)
```

### Beneficios Obtenidos

1. **Centralización** - Mensajes en un solo lugar
2. **Consistencia** - Mismo mensaje para la misma operación
3. **Mantenibilidad** - Cambiar mensaje en un solo lugar
4. **Localización** - Base para futuras traducciones

### Próximos Pasos

1. Completar migración en security_dialog.py
2. Migrar controller.py usando las constantes existentes
3. Crear constantes específicas para mensajes de logs
4. Migrar improved_dialogs.py y otros diálogos
5. Validar que todos los mensajes funcionen correctamente

### Estimación

- **Completado**: ~15%
- **Constantes creadas**: 20+ nuevas constantes
- **Archivos iniciados**: 2/10
- **Tiempo estimado restante**: 2-3 horas de trabajo sistemático