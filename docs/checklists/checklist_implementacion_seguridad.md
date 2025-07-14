# Checklist de Implementación de Seguridad

Este checklist presenta todas las acciones que deben implementarse para mejorar la seguridad de la aplicación. Marca cada elemento a medida que se completa.

## Protección contra Inyección SQL

- [ ] **Verificar conexiones a base de datos**
  - [ ] Revisar todos los módulos que realizan conexiones directas a la base de datos
  - [ ] Reemplazar cualquier construcción manual de SQL por consultas parametrizadas
  - [ ] Implementar time-out en todas las conexiones

- [ ] **Implementar consultas parametrizadas en todas las operaciones**
  - [ ] Módulo de usuarios
  - [ ] Módulo de obras
  - [ ] Módulo de inventario
  - [ ] Módulo de herrajes
  - [ ] Módulo de vidrios
  - [ ] Módulo de pedidos
  - [ ] Módulo de configuración
  - [ ] Módulo de auditoría

- [ ] **Usar los constructores de SQL seguro**
  - [ ] Reemplazar SELECT directos por `construir_select_seguro`
  - [ ] Reemplazar INSERT directos por `construir_insert_seguro`
  - [ ] Reemplazar UPDATE directos por `construir_update_seguro`
  - [ ] Reemplazar DELETE directos por `construir_delete_seguro`
  - [ ] Verificar que siempre exista cláusula WHERE en DELETE/UPDATE

- [ ] **Validar nombres de tablas y columnas**
  - [ ] Actualizar `TABLAS_PERMITIDAS` con todas las tablas del sistema
  - [ ] Actualizar `COLUMNAS_PERMITIDAS` con todas las columnas por tabla
  - [ ] Implementar validación de nombres en todas las consultas dinámicas

## Validación y Sanitización de Datos de Entrada

- [ ] **Implementar validación en todos los formularios**
  - [ ] Formularios de login y registro
  - [ ] Formularios de edición de perfil
  - [ ] Formularios de creación/edición de obras
  - [ ] Formularios de inventario
  - [ ] Formularios de pedidos
  - [ ] Formularios de configuración

- [ ] **Sanitizar todos los datos de entrada**
  - [ ] Campos de texto libre (usar `sanitizar_html`)
  - [ ] URLs y enlaces (usar `sanitizar_url`)
  - [ ] Datos JSON (usar `sanitizar_json`)
  - [ ] Valores numéricos (usar `sanitizar_numerico`)
  - [ ] Fechas (usar `sanitizar_fecha_sql`)

- [ ] **Prevención de XSS**
  - [ ] Revisar todos los campos donde se muestra contenido ingresado por el usuario
  - [ ] Aplicar `detectar_xss` en datos críticos
  - [ ] Implementar sanitización HTML en todos los campos de texto libre
  - [ ] Asegurar que el contenido HTML generado siempre esté escapado

## Análisis y Monitoreo de Seguridad

- [ ] **Implementar escaneo regular de código**
  - [ ] Configurar análisis automático en pipeline de CI/CD
  - [ ] Programar análisis semanal con `analizar_seguridad_sql_codigo.py`
  - [ ] Bloquear commits con vulnerabilidades críticas

- [ ] **Auditoría y monitoreo**
  - [ ] Implementar registro de intentos de inyección SQL
  - [ ] Implementar registro de intentos de XSS
  - [ ] Configurar alertas para patrones sospechosos
  - [ ] Revisar logs de seguridad semanalmente

- [ ] **Escaneo de vulnerabilidades completo**
  - [ ] Ejecutar `escanear_vulnerabilidades.py` mensualmente
  - [ ] Documentar y priorizar vulnerabilidades encontradas
  - [ ] Verificar la resolución de problemas reportados

## Integración de Módulos y Pruebas

- [ ] **Integrar validadores con módulos existentes**
  - [ ] Integrar `FormValidator` en todos los controladores
  - [ ] Reemplazar validación manual por las utilidades centralizadas
  - [ ] Estandarizar manejo de errores de validación en UI

- [ ] **Pruebas de seguridad**
  - [ ] Crear pruebas de penetración para inyección SQL
  - [ ] Crear pruebas de penetración para XSS
  - [ ] Crear pruebas para validadores de formulario
  - [ ] Verificar sanitización correcta en todos los módulos

- [ ] **Actualizar documentación**
  - [ ] Incorporar guías de seguridad en manuales de desarrollo
  - [ ] Capacitar al equipo sobre las nuevas utilidades
  - [ ] Documentar excepciones y casos especiales

## Configuración y Permisos

- [ ] **Revisar permisos de base de datos**
  - [ ] Auditar permisos de usuario de aplicación en BD
  - [ ] Aplicar principio de mínimo privilegio
  - [ ] Separar usuarios por ambiente (dev, test, prod)

- [ ] **Configuraciones de seguridad**
  - [ ] Revisión de contraseñas y claves en archivos de configuración
  - [ ] Implementar almacenamiento seguro de credenciales
  - [ ] Verificar exclusión de archivos sensibles en `.gitignore`

## Extensión a Otras Áreas

- [ ] **Seguridad en JSON/APIs**
  - [ ] Validar todas las entradas y salidas JSON
  - [ ] Aplicar limitación de tasa (rate limiting) en APIs sensibles
  - [ ] Implementar autenticación robusta en todas las APIs

- [ ] **Protección contra otras vulnerabilidades**
  - [ ] Implementar protección contra CSRF
  - [ ] Revisar gestión de sesiones
  - [ ] Revisar política de contraseñas
  - [ ] Implementar bloqueo de cuentas tras intentos fallidos

## Verificación Final

- [ ] **Test de penetración completo**
  - [ ] Pruebas de inyección SQL en todos los endpoints
  - [ ] Pruebas de XSS en todos los campos de entrada
  - [ ] Pruebas de fuerza bruta en autenticación
  - [ ] Verificar encriptación de datos sensibles

- [ ] **Documentación de seguridad actualizada**
  - [ ] Manual de respuesta a incidentes
  - [ ] Procedimientos de recuperación
  - [ ] Política de actualizaciones de seguridad

## Mantenimiento Continuo

- [ ] **Plan de actualización de seguridad**
  - [ ] Programación de revisiones mensuales
  - [ ] Responsables asignados por área
  - [ ] Procedimiento para implementar parches de seguridad

---

## Registro de Implementación

| Fecha | Elemento Implementado | Responsable | Observaciones |
|-------|------------------------|------------|---------------|
|       |                        |            |               |
|       |                        |            |               |
|       |                        |            |               |

## Versión del Checklist: 1.0.0
Fecha de creación: 25 de junio de 2025
