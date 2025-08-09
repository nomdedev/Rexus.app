# Checklist pendientes y hallazgos de auditoría (unificado)

**Fecha de actualización:** 9 de agosto de 2025

---

## Introducción
Este documento unifica todos los puntos pendientes, checklist de tareas, y hallazgos críticos de las auditorías realizadas en Rexus.app. La información está agrupada por módulo y priorizada según la criticidad del problema.

---

## 1. Checklist General y Estado

### a) Logs de fallback logic
- Estado: COMPLETADO
- Acción: Eliminados logs innecesarios, solo quedan logs críticos para funcionalidades opcionales.

### b) Errores de esquema de base de datos
- Estado: COMPLETADO
- Acción: Corregidos 16 problemas de esquema en tablas principales (`obras`, `pedidos`, `vidrios`).

### c) Importaciones circulares
- Estado: COMPLETADO
- Acción: No se detectaron importaciones circulares tras escaneo de 6,909 módulos.

### d) Errores de sintaxis
- Estado: COMPLETADO
- Acción: Limpieza masiva de archivos y directorios con errores, preservando archivos esenciales.

### e) Vulnerabilidades de SQL injection
- Estado: COMPLETADO
- Acción: Refactorización completa, consultas externalizadas y uso de SQLQueryManager.

---

## 2. Consolidación de Base de Datos (pendientes)
- [ ] Crear tabla `productos` consolidada (inventario, herrajes, vidrios, materiales)
- [ ] Migrar datos a `productos` y verificar integridad
- [ ] Crear tabla `auditoria` unificada y migrar datos
- [ ] Crear sistema unificado de pedidos y migrar datos
- [ ] Consolidar relaciones producto-obra
- [ ] Unificar movimientos de inventario

---

## 3. Hallazgos y pendientes por módulo (prioridad CRÍTICA/ALTA)

### API
- Revisar manejo seguro de claves JWT y almacenamiento de secretos (**CRÍTICO**)
- Validar exhaustivamente los datos de entrada en todos los endpoints (**CRÍTICO**)
- Revisar protección contra ataques comunes: inyección, XSS, CSRF, enumeración de usuarios (**CRÍTICO**)
- Configurar CORS y TrustedHost de forma restrictiva en producción (**ALTA**)
- Implementar autenticación real con hash de contraseñas y usuarios en base de datos (**CRÍTICO**)
- Añadir rate limiting distribuido para despliegues multi-nodo (**ALTA**)
- Limitar información sensible en logs (**ALTA**)
- Añadir validación estricta de parámetros en todos los endpoints (**ALTA**)
- Añadir pruebas unitarias y de integración (**ALTA**)

### UTILS
- Revisar y actualizar patrones de XSS/SQLi periódicamente (**ALTA**)
- Añadir pruebas unitarias (**ALTA**)
- Limitar información sensible en logs (**ALTA**)
- Validar permisos antes de eliminar/comprimir/restaurar archivos (**ALTA**)
- Considerar cifrado de backups para mayor seguridad (**ALTA**)

### CORE
- Añadir cifrado/anonimización de datos sensibles en logs (**CRÍTICO**)
- Implementar rotación y retención de logs (**ALTA**)
- Considerar integración con SIEM (**ALTA**)
- Añadir pruebas unitarias (**ALTA**)
- Validar integridad de registros de auditoría (**ALTA**)
- Considerar cifrado de datos en caché y validación de permisos (**ALTA**)
- Agregar logging/auditoría de errores críticos y fallos de backend (**ALTA**)
- Implementar pruebas automáticas de recuperación ante fallos de backend (**ALTA**)

---

## 4. Recomendaciones generales
- Fortalecer la cobertura de tests, priorizando componentes críticos y escenarios de error.
- Integrar herramientas automáticas de cobertura y seguridad en CI/CD.
- Documentar criterios de aceptación y expected outcomes en cada test.
- Mantener la documentación de auditoría y checklist actualizada.

---

## 5. Problemas de UI/UX, feedback visual y experiencia de usuario

### Generales
- Falta de un sistema de feedback visual consistente para operaciones críticas y errores.
- Uso de print y QMessageBox en vez de notificaciones visuales centralizadas.
- Ausencia de loading indicators y estados de progreso en operaciones largas.
- Inconsistencias en iconografía (mezcla de emojis, texto y SVG/PNG).
- Falta de pruebas automáticas de visualización, animaciones y fallback de UI.
- No hay integración con sistemas de monitoreo de experiencia de usuario.

### Inventario (CRÍTICO)
- 17 violaciones UI detectadas: estilos inline, componentes no estandarizados, colores hardcodeados, métodos duplicados, paginación incompleta, manejo inconsistente de errores.
- Lógica de negocio en la vista, acceso directo a controller, validación de datos en la vista.
- Carga síncrona sin indicadores, recreación completa de tabla, conexiones de señales por fila.
- Plan de corrección: migrar a StyleManager, unificar componentes, separar lógica MVC, implementar loading states, centralizar manejo de errores.

### Main y módulos secundarios
- Uso de print para logs y advertencias, sin logging estructurado.
- No hay auditoría de accesos ni monitoreo de experiencia de usuario.
- Falta de pruebas automáticas de fallback visual y recuperación ante fallos de recursos gráficos.

### Recomendaciones UI/UX
- Migrar todos los estilos a StyleManager y QSS centralizados.
- Unificar componentes visuales con StandardComponents.
- Implementar feedback visual consistente (notificaciones, loading, errores).
- Integrar monitoreo de experiencia de usuario y pruebas automáticas de UI.
- Estandarizar iconografía y nomenclatura de métodos visuales.
- Documentar criterios de aceptación visual y expected outcomes.

---

## 6. Seguridad de contraseñas y hashing (CRÍTICO)
- Scripts de mantenimiento usan SHA256 simple y contraseñas hardcodeadas (admin/admin).
- Plan de remediación: migrar todos los scripts a password_security.py (bcrypt/Argon2), eliminar contraseñas hardcodeadas, regenerar usuarios admin, auditar base de datos para hashes inseguros.
- Implementar políticas de contraseñas estrictas, 2FA obligatorio para admin, rotación automática y alertas de seguridad.

---

## 7. Modernización, estandarización y métricas de calidad
- Issues comunes: imports duplicados, logging inconsistente, constructores no estandarizados, falta de framework UI, métodos duplicados.
- Plan de corrección: limpiar imports, unificar logging, estandarizar constructores, migrar a framework UI, completar métodos pendientes, añadir tests y documentación.
- Métricas de calidad: arquitectura MVC, seguridad, UI framework, documentación, testing (ver detalles en auditoría de módulos restantes).

---

## 8. Fases de corrección y próximos pasos
- Fase 1 (Crítica): migración de seguridad, corrección de UI/UX en inventario, limpieza de imports y logging, migración de scripts de mantenimiento.
- Fase 2 (Funcional): completar métodos pendientes, mejorar validación, modernizar módulos básicos, añadir tests.
- Fase 3 (Optimización): integración entre módulos, optimización de consultas, documentación, monitoreo y training de seguridad.

---

## 9. Estado de los tests, cobertura y edge cases

### Cobertura actual
- Cobertura de validación exitosa: 60% (3/5 componentes críticos)
- SQL Injection: 100% protegido
- XSS: 91.7% protegido (11/12 módulos)
- Configuración segura: 75% implementado
- Sistema de autorización: estructura completa, falta activación total

### Edge cases y pendientes
- Faltan tests de integración básicos en algunos módulos
- Faltan tests de penetración y validación de rendimiento
- Faltan pruebas automáticas de visualización, animaciones y fallback de UI
- Faltan tests de edge cases en formularios, validaciones de entrada y manejo de errores extremos
- Faltan tests de roles y permisos en AuthManager
- Faltan tests de sanitización activa en formularios y entradas de usuario

### Próximos pasos de testing
- Corregir encoding de security.py para habilitar tests de seguridad
- Activar decoradores @auth_required en métodos críticos y probar sistema de permisos
- Implementar sanitización XSS activa y validar en tiempo real
- Añadir tests de integración y penetración en todos los módulos
- Validar cobertura de tests y documentar resultados
- Capacitar al equipo en testing de edge cases y seguridad

### Métricas y recomendaciones
- Incrementar cobertura de tests a >85% en componentes críticos
- Documentar criterios de aceptación y expected outcomes en cada test
- Integrar reportes automáticos de cobertura y seguridad en CI/CD
- Mantener la documentación de tests y resultados actualizada

---

## 10. Módulos sin funcionalidades, problemas de fallback y causas

### Módulos sin funcionalidades completas
- Módulo Vidrios: solo CRUD básico, sin manejo de errores robusto, sin logging ni framework UI, falta documentación y tests.
- Módulo Pedidos: validación de datos insuficiente, integración incompleta con inventario, logging inconsistente, métodos pendientes.
- Módulo Auditoría: faltan métodos críticos, validación de rutas de export, threading sin manejo de errores robusto, falta de tests.
- Módulo Administración: validación de usuario y rol solo al inicio, sin logs de auditoría en operaciones críticas, sin pruebas unitarias.

### Problemas de fallback y visibilidad de funcionalidades
- Varios módulos implementan fallback en autenticación y seguridad: si los decoradores de seguridad no están disponibles, el sistema permite acceso sin restricciones (riesgo CWE-285, Broken Access Control).
- En inventario, el fallback de autenticación no restringe acceso y la sanitización depende de la disponibilidad de utilidades de seguridad.
- Fallbacks en modelos: si utilidades de seguridad no están disponibles, se degrada la protección y no se fuerza error seguro.
- Problemas de visibilidad: la falta de logging estructurado y de feedback visual hace que los usuarios no vean errores, fallos o la ausencia de funcionalidades.
- La ausencia de validación y logging en formularios y vistas permite que errores pasen desapercibidos y no se reporten ni al usuario ni al equipo.

### Causas principales
- Implementación de fallback inseguro para evitar bloqueos en desarrollo, pero no reforzado para producción.
- Falta de logging centralizado y estructurado para detectar y reportar fallos.
- Ausencia de validación exhaustiva de datos en todas las capas (vista, controlador, modelo).
- Falta de documentación y tests en módulos secundarios.
- Integración incompleta entre módulos (ej: pedidos ↔ inventario).

### Soluciones recomendadas
- Mejorar todos los fallbacks para que, si las utilidades de seguridad o decoradores no están disponibles, se deniegue el acceso y se reporte el error.
- Implementar logging estructurado y centralizado en todos los módulos.
- Validar y sanear todos los datos de entrada en cada capa.
- Completar funcionalidades pendientes y documentar puntos de entrada y protecciones.
- Añadir feedback visual y notificaciones de error para el usuario.
- Integrar y testear todos los módulos para asegurar visibilidad y trazabilidad de fallos.

---

## 11. Mejoras prioritarias, mejoras incrementales y acciones útiles para el usuario

### Priorización de mejoras prioritarias

| Mejora prioritaria                                      | Estado actual | Responsable | Urgencia | Siguiente acción sugerida                  |
|---------------------------------------------------------|---------------|-------------|----------|--------------------------------------------|
| Integración avanzada con inventario                     | Pendiente     |             | Alta     | Auditar módulos compras/pedidos/obras      |
| Backup automático antes de operaciones críticas         | Parcial       |             | Alta     | Integrar hooks de backup en módulos clave  |
| Tooltips inteligentes y accesibilidad                   | Pendiente     |             | Media    | Implementar en todas las vistas            |
| Validadores avanzados y protección XSS                  | Parcial       |             | Alta     | Revisar formularios y aplicar validadores  |
| Uso de componentes modernos y factory de módulos        | Parcial       |             | Media    | Migrar instanciación a factory             |
| Exponer reportes y estadísticas en la UI                | Pendiente     |             | Media    | Agregar botones y vistas de reportes       |
| Eliminar código muerto y helpers no usados              | Pendiente     |             | Alta     | Auditar y limpiar utilidades               |
| Feedback visual y experiencia de usuario unificada      | Parcial       |             | Alta     | Unificar notificaciones y loading          |
| Migrar estilos a StyleManager y StandardComponents      | Parcial       |             | Alta     | Refactorizar vistas y componentes          |
| Aumentar cobertura de tests y edge cases                | Parcial       |             | Alta     | Plan de tests y edge cases                 |

> Completar responsable y fecha estimada en cada fila según asignación de equipo.

### Cosas que debemos mejorar (prioridad alta)
- Integrar funcionalidades existentes pero no activas:
  - Integración avanzada con inventario (compras, pedidos, obras).
  - Sistema de backup automático antes de operaciones críticas.
  - Tooltips inteligentes y accesibilidad en todas las vistas.
  - Validadores avanzados y protección XSS en todos los formularios.
  - Uso de componentes modernos y factory de módulos para instanciar vistas.
  - Exponer reportes y estadísticas en la UI.
- Eliminar código muerto y clases no usadas:
  - Auditar utilidades y helpers no referenciados (ej: `BackupIntegration`, `InventoryIntegration`, `SmartTooltip`, validadores avanzados).
  - Eliminar o documentar clases/componentes modernos no integrados.
- Mejorar feedback visual y experiencia de usuario:
  - Unificar notificaciones visuales, loading indicators y manejo de errores.
  - Migrar estilos a StyleManager y componentes visuales a StandardComponents.
  - Estandarizar iconografía y nomenclatura visual.
- Aumentar cobertura de tests y edge cases:
  - Tests de integración, edge cases en formularios, roles y permisos, sanitización activa.
  - Pruebas automáticas de visualización y fallback de UI.

### Cosas que podríamos mejorar (mejoras incrementales)
- Integrar monitoreo de experiencia de usuario y reportes automáticos de errores.
- Añadir métricas de uso y performance en cada módulo.
- Mejorar documentación de expected outcomes y criterios de aceptación visual.
- Implementar onboarding interactivo y ayuda contextual en la UI.
- Soporte para accesibilidad avanzada (navegación por teclado, lectores de pantalla).

### Acciones útiles que podríamos implementar en cada view para el usuario
- Exportar datos: Botón para exportar la tabla o los datos filtrados a Excel/CSV/PDF.
- Historial de cambios: Opción para ver el historial de modificaciones de un registro.
- Acciones masivas: Selección múltiple para eliminar, actualizar o exportar varios registros a la vez.
- Favoritos o marcadores: Permitir marcar registros frecuentes o importantes.
- Búsqueda avanzada: Filtros combinados, búsqueda por rangos de fechas, estados, etc.
- Feedback inmediato: Notificaciones visuales al guardar, eliminar, o ante errores.
- Accesos rápidos: Atajos de teclado para las acciones principales (nuevo, guardar, buscar, etc.).
- Ayuda contextual: Tooltips explicativos y enlaces a documentación o tutoriales.
- Recuperar borrados recientes: Opción de deshacer o recuperar registros eliminados recientemente.
- Visualización adaptable: Cambiar entre vista tabla, tarjetas, o gráficos según el contexto.

---

**Este checklist debe ser revisado y actualizado tras cada ciclo de auditoría, cambio mayor en la arquitectura o revisión de experiencia de usuario.**
