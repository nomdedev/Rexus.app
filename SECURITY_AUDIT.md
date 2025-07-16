### 12. Uso inseguro de f-strings en SQL detectado en los siguientes archivos (riesgo de SQL Injection)

Se detectó el uso de f-strings para construir sentencias SQL en los siguientes archivos y líneas. Esto representa un riesgo crítico de SQL Injection si algún valor es manipulable. Deben refactorizarse para usar parámetros y/o listas blancas estrictas para nombres de tablas/campos.

**src/modules/vidrios/model.py**
- Líneas: 303, 309, 315, 321, 327, 515, 530

**src/core/audit_trail.py**
- Líneas: 164, 298, 339, 356, 360, 398, 409, 442

**src/core/database.py**
- Línea: 95

**src/core/backup_manager.py**
- Líneas: 281, 292, 296, 301

**src/modules/mantenimiento/model.py**
- Líneas: 547, 551, 560, 568, 575, 637

**src/modules/inventario/model.py**
- Líneas: 1835, 1840, 1850, 1858

**src/modules/logistica/model.py**
- Líneas: 494, 524, 528, 532, 540, 548, 555, 624

**src/modules/configuracion/model.py**
- Líneas: 139, 171, 230, 292, 398

**src/modules/herrajes/model.py**
- Líneas: 65, 95, 113, 133, 149, 150, 151, 152, 425, 431, 437, 443, 527, 533, 565, 599, 604, 634, 667, 675, 684, 715, 745, 776, 783

**src/modules/administracion/recursos_humanos/model.py**
- Líneas: 203, 400, 725, 729, 738, 750

**src/modules/administracion/contabilidad/model.py**
- Líneas: 138, 309, 614, 630, 642, 654, 760, 772, 779

**src/api/server.py**
- Línea: 292

**Acción recomendada:**
Refactorizar todas estas sentencias para eliminar el uso de f-strings en SQL. Usar parámetros para los valores y listas blancas estrictas para los nombres de tablas/campos si deben ser dinámicos.
# Informe de Auditoría de Seguridad - Rexus.app

## Problemas detectados y recomendaciones

### 1. Creación automática de usuarios admin/test
- Grave riesgo de seguridad: si la tabla está vacía, se crean usuarios por defecto con credenciales conocidas.
- Recomendación: eliminar la creación automática de usuarios en producción. Solo debe hacerse en scripts de instalación o migración controlada.


### 2. Consultas SQL con f-strings y vulnerabilidad a SQL Injection
- Uso de f-strings para construir consultas SQL en `src/modules/usuarios/model.py` y otros módulos.
- Hallazgo crítico: El análisis automático (Bandit B608) detectó múltiples lugares donde se construyen queries SQL usando f-strings, lo que permite SQL Injection si algún valor es manipulable.
- Ejemplo: `cursor.execute(f"""SELECT ... WHERE campo = '{valor}'""")`
- Recomendación: Refactorizar todas las consultas para usar parámetros (`?` o `%s`) y nunca interpolar variables directamente en el SQL. Validar estrictamente nombres de tablas/campos si son dinámicos.

### 3. Control de intentos fallidos de login
- No hay bloqueo de cuenta tras varios intentos fallidos.
- Recomendación: implementar contador de intentos y bloqueo temporal tras X fallos.

### 4. Contraseñas débiles
- No se fuerza la complejidad mínima de contraseñas.
- Recomendación: exigir longitud mínima, mayúsculas, minúsculas, números y símbolos.

### 5. Falta de auditoría y logs de seguridad
- No se auditan accesos, cambios críticos ni eventos sospechosos.
- Recomendación: registrar todos los accesos, cambios de permisos, borrados y bloqueos de usuarios.

### 6. Roles y permisos poco granulares
- El sistema de roles es básico y no restringe acciones sensibles de forma granular.
- Recomendación: definir permisos por acción y módulo, y validarlos en cada endpoint/función crítica.

### 7. Validación de entradas insuficiente
- No se valida ni limita el tamaño/tipo de los campos de entrada.
- Recomendación: validar y sanear todos los datos recibidos antes de procesarlos o almacenarlos.

### 8. Cifrado de datos sensibles
- Solo se hashean contraseñas, pero otros datos sensibles no están cifrados.
- Recomendación: cifrar emails, teléfonos y otros datos personales si es necesario.

### 9. Logs de seguridad centralizados
- No hay un sistema de logs de seguridad centralizado ni alertas.
- Recomendación: implementar logs centralizados y alertas ante eventos críticos.

### 10. Uso de HTTPS/TLS

### 11. Carga de recursos locales sin validación (icon_loader.py)
-- El cargador de iconos permite cargar archivos locales por nombre, lo que puede ser explotado si el nombre proviene de entrada de usuario.
-- Recomendación: validar que el nombre del icono solo contenga caracteres permitidos (letras, números, guiones bajos) y nunca aceptar rutas relativas ni caracteres especiales.



---

## Notas adicionales
- Esta auditoría es preliminar. Se recomienda una revisión completa de todo el código y dependencias.
- Mantener actualizado el software y las librerías de terceros.
- Realizar pruebas de penetración periódicas.

---

¿Deseas que priorice la corrección de alguno de estos puntos o que continúe con un análisis más profundo de otros módulos?
