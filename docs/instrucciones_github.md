# Instrucciones para Publicar el Código en GitHub de forma Segura

Este documento proporciona pasos específicos para asegurar que los datos sensibles estén protegidos al subir el código a GitHub.

## 1. Preparación del Repositorio Local

### Verificación Final de Seguridad

Antes de realizar el primer commit, verifica:

1. **Credenciales**:
   - Asegúrate de que `core/config.py` contiene solo referencias a variables de entorno.
   - Verifica que `core/config.example.py` no contenga credenciales reales.
   - Confirma que `.env` y cualquier archivo con credenciales esté en `.gitignore`.

2. **SQL Injection**:
   - Todas las consultas SQL deben usar parametrización.
   - Para nombres de tablas y columnas, se deben usar listas blancas de valores permitidos.

3. **Archivos Sensibles**:
   - Realiza una última verificación de archivos que podrían contener información sensible.
   - Verifica que los archivos de test privados están ignorados correctamente.

## 2. Comandos Git para el Primer Push

```powershell
# Inicializar repositorio local (si aún no existe)
git init

# Verificar archivos que se incluirán en el commit
git status

# Agregar todos los archivos excepto los ignorados
git add .

# Verificar nuevamente qué se va a commitear
git status

# Realizar el primer commit
git commit -m "Versión inicial segura para GitHub"

# Agregar el repositorio remoto (reemplaza URL_REPOSITORIO con la URL real)
git remote add origin URL_REPOSITORIO

# Subir al repositorio remoto
git push -u origin master
```

## 3. Verificación Post-Push

Después de subir el código, verifica en GitHub:

1. **Archivos Sensibles**: Confirma que no aparecen archivos con información sensible.
2. **Configuración**: Asegúrate de que solo está disponible el archivo `config.example.py` y no `config.py`.
3. **Tests Privados**: Confirma que los tests con datos privados no se subieron.

## 4. Configuración de Seguridad en GitHub

1. **Dependabot**: Activa Dependabot para alertas de seguridad en dependencias.
2. **Secret Scanning**: Activa la detección automática de secretos.
3. **Protección de Ramas**: Configura reglas para proteger la rama principal.

## 5. Documentación para Colaboradores

Asegúrate de que los nuevos colaboradores entiendan:

1. Cómo configurar correctamente el entorno local con variables de entorno.
2. La importancia de seguir las prácticas de seguridad descritas en `docs/seguridad_github.md`.
3. La estructura y convenciones de código seguro.

## Recordatorio

* Nunca subas archivos `.env` o archivos de configuración con credenciales reales.
* Usa siempre parametrización en consultas SQL.
* Valida entradas de usuario para prevenir inyecciones.
* Mantén actualizado el archivo de documentación de seguridad.
