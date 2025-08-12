con- [x] ~~Eliminar todas las contraseñas, usuarios y credenciales hardcodeadas en el código fuente y archivos .env de ejemplo. Migrar a variables de entorno seguras y documentar el uso correcto para producción y testing.~~ ✅ **COMPLETADO** - Ver docs/ENVIRONMENT_VARIABLES.md
---

## 3. Pendientes técnicos detectados (auto-checklist)

- [ ] Reparar la función `create_group_box` en `rexus/ui/standard_components.py` (errores de sintaxis y/o indentación en el CSS del group box)
- [ ] Renombrar variables y métodos para cumplir con el linter (por ejemplo, nombres con tildes o conflictos de nombres)
- [ ] Revisar y limpiar imports no utilizados en todo el proyecto
- [ ] Validar que todos los estilos QSS usen propiedades válidas y soportadas por Qt
- [ ] Revisar warnings de propiedades desconocidas como `row-height` y `transform` en los estilos
- [ ] Mejorar la robustez de la inicialización de QtWebEngine (manejar error de importación)
- [ ] Revisar y corregir posibles errores de conexión/desconexión de señales en los módulos
- [ ] Validar que todos los módulos cargan correctamente en todos los temas
# Checklist de pendientes y mejoras por módulo (ordenado por prioridad)

**Fecha de actualización:** 10 de agosto de 2025

---

## 1. Errores críticos y bloqueantes (Prioridad CRÍTICA)

### [GENERAL / SISTEMA]
- Errores CSS repetidos: `Unknown property row-height` y `box-shadow` (impacto en rendimiento, logs saturados)
- [x] ~~Migrar queries hardcodeadas críticas en módulos principales~~ ✅ PARCIALMENTE RESUELTO (usuarios y logística completados)

### [LOGÍSTICA] ✅ COMPLETADO
- [x] ~~Error: `'SQLQueryManager' object has no attribute 'get_query'`~~ ✅ RESUELTO
- [x] ~~Error: `'LogisticaView' object has no attribute 'cargar_entregas_en_tabla'`~~ ✅ RESUELTO
- [x] ~~Mejorar organización visual y layout de pestañas (Transportes, Estadísticas, Servicios, Mapa)~~ ✅ RESUELTO
  - [x] ~~Problemas: paneles apilados, botones desproporcionados, falta de separación visual, layout saturado, jerarquía visual deficiente, placeholders confusos, splitters desbalanceados, proporciones no responsivas, etc.~~ ✅ RESUELTO

### [API] ✅ COMPLETADO
- [x] ~~Revisar manejo seguro de claves JWT y almacenamiento de secretos~~ ✅ RESUELTO
- [x] ~~Validar exhaustivamente los datos de entrada en todos los endpoints~~ ✅ RESUELTO
- [x] ~~Revisar protección contra ataques comunes: inyección, XSS, CSRF, enumeración de usuarios~~ ✅ RESUELTO
- [x] ~~Implementar autenticación real con hash de contraseñas y usuarios en base de datos~~ ✅ RESUELTO
- [x] ~~Añadir cifrado/anonimización de datos sensibles en logs (CORE)~~ ✅ RESUELTO

---

## 2. Mejoras urgentes y de alta prioridad

### [GENERAL / SISTEMA]
- Limitar información sensible en logs
- Añadir validación estricta de parámetros en todos los endpoints (API)
- Añadir pruebas unitarias y de integración (API, CORE, UTILS)
- Implementar rotación y retención de logs (CORE)
- Considerar integración con SIEM (CORE)
- Validar integridad de registros de auditoría (CORE)
- Considerar cifrado de datos en caché y validación de permisos (CORE)
- Agregar logging/auditoría de errores críticos y fallos de backend (CORE)
- Implementar pruebas automáticas de recuperación ante fallos de backend (CORE)
- Revisar y actualizar patrones de XSS/SQLi periódicamente (UTILS)
- Validar permisos antes de eliminar/comprimir/restaurar archivos (UTILS)
- Considerar cifrado de backups para mayor seguridad (UTILS)

### [LOGÍSTICA] ✅ COMPLETADO
- [x] ~~Optimizar responsividad y compactación visual en todas las pestañas~~ ✅ RESUELTO
- [x] ~~Mejorar placeholders de gráficos y fallback de mapa~~ ✅ RESUELTO
- [x] ~~Añadir iconografía y colores para estados de servicios~~ ✅ RESUELTO

### [INVENTARIO / VIDRIOS] ✅ COMPLETADO
- [x] ~~Aplicar estilos minimalistas específicos de Logística (método `aplicar_estilos()`)~~ ✅ RESUELTO
- [x] ~~Reducir tamaños de botones y campos de entrada~~ ✅ RESUELTO
- [x] ~~Unificar colores GitHub-style~~ ✅ RESUELTO
- [x] ~~Implementar pestañas con estilo Logística~~ ✅ RESUELTO

### [MAIN Y MÓDULOS SECUNDARIOS] ✅ COMPLETADO
- [x] ~~Migrar todos los estilos a StyleManager y QSS centralizados~~ ✅ RESUELTO
- [x] ~~Unificar componentes visuales con StandardComponents~~ ✅ RESUELTO
- [x] ~~Implementar feedback visual consistente (notificaciones, loading, errores)~~ ✅ RESUELTO
- [x] ~~Integrar monitoreo de experiencia de usuario y pruebas automáticas de UI~~ ✅ RESUELTO
- [x] ~~Estandarizar iconografía y nomenclatura de métodos visuales~~ ✅ RESUELTO

---

## 2.5. Errores críticos en Tests (PRIORIDAD CRÍTICA) 🧪

### [TESTS / COBERTURA]
- **Error crítico**: `NameError: name 'Dict' not defined` en password_manager.py (imports faltantes) ✅ CORREGIDO
- **Error crítico**: `fixture 'sample_usuario_data' not found` - fixtures inconsistentes entre tests
- **Error crítico**: `sqlite3.OperationalError: unable to open database file` - base de datos de testing no accesible
- **Error crítico**: Múltiples fallos (47 de 248 tests failing) - Suite de tests rota
- **Cobertura crítica**: 13 módulos principales - Status testing:
  - ❌ administracion - Sin tests específicos  
  - ✅ auditoria - Tests implementados (test_auditoria.py) - 32 tests
  - ✅ compras - Tests implementados (test_compras.py) - 20 tests 
  - ✅ configuracion - Tests implementados (test_configuracion.py) - 25 tests
  - ✅ herrajes - Tests implementados (test_herrajes.py) - 29 tests
  - ✅ inventario - Tests implementados (test_inventario.py) - 21 tests
  - ✅ logistica - Tests implementados (test_logistica.py) - 18 tests
  - ✅ mantenimiento - Tests implementados (test_mantenimiento.py) - 30 tests
  - ❌ notificaciones - Sin tests específicos
  - ✅ obras - Tests implementados (test_obras.py) - 26 tests
  - ✅ pedidos - Tests implementados (test_pedidos.py) - 24 tests
  - ✅ usuarios - Tests implementados (test_usuarios.py) - 25 tests
  - ✅ vidrios - Tests implementados (test_vidrios.py) - 28 tests

### [FIXTURES Y CONFIGURACIÓN]
- Fixtures inconsistentes: `sample_usuario_data` vs `sample_user_data`
- Paths de base de datos incorrectos en test environment
- Configuración pytest.ini necesita revisión
- conftest.py requiere actualización para nuevos módulos

### [IMPACTO EN CALIDAD]
- **Riesgo alto**: Cambios recientes en código sin validación por tests
- **Regresiones posibles**: Estilos, métodos nuevos, imports sin verificar
- **Cobertura estimada**: ~15% (solo tests de core/security/utils/ui)
- **Tests funcionales**: 0% para módulos de negocio principales

### [PROGRESO ACTUAL EN TESTS] 🔄 ✅ COMPLETADO
- [x] ~~Error `NameError: name 'Dict'` en password_manager.py~~ ✅ CORREGIDO
- [x] ~~Error `fixture 'sample_usuario_data' not found`~~ ✅ CORREGIDO  
- [x] ~~Error base de datos testing no accesible~~ ✅ CORREGIDO (fixture con tmp_path)
- [x] ~~Creado test básico para módulo logística~~ ✅ COMPLETADO
- [x] ~~Creados tests para usuarios, inventario, estilos~~ ✅ COMPLETADO
- [x] ~~Documentación estándares de testing~~ ✅ COMPLETADO
- [x] ~~Tests para módulos de negocio restantes~~ ✅ COMPLETADO (11/13 módulos)
- [x] ~~Estructura de directorios testing~~ ✅ CORREGIDO
- [x] ~~Archivos de configuración pytest~~ ✅ CORREGIDO
- **Estado actual suite**: ✅ **270 TESTS IMPLEMENTADOS** - Suite completa funcionando
- **Test coverage**: ✅ **11 módulos principales** con tests comprehensivos (4,185 líneas de código)
- **Tests modulares**: ✅ **Estructura completa** para testing individual + estándares documentados

### [ERRORES TESTING ACTUALES - Agosto 2025] 🚨
- [x] ~~**Estructura directories**: Faltan directorios `integration`, `e2e`, `performance`, `security` en tests/~~ ✅ CORREGIDO
- [ ] **Marcadores pytest**: Warnings sobre marcadores no registrados (performance, ui, e2e, etc.) - PARCIALMENTE CORREGIDO (pytest.ini actualizado)
- [x] ~~**Archivo ESTANDARES_TESTING.md**: Falta en directorio tests/ (existe como TESTING_STANDARDS.md)~~ ✅ CORREGIDO
- [x] ~~**Tests módulos restantes**: Faltan tests para pedidos, auditoria, configuracion, mantenimiento, vidrios~~ ✅ COMPLETADO (Solo administracion y notificaciones pendientes - 11/13 completados)
- [x] ~~**ConsultasManager warning**: Missing consultas_manager_refactorizado en inventario~~ ✅ CORREGIDO

---

## 3. Mejoras medias y optimización

### [GENERAL]
- Fortalecer la cobertura de tests, priorizando componentes críticos y escenarios de error
- Integrar herramientas automáticas de cobertura y seguridad en CI/CD
- Documentar criterios de aceptación y expected outcomes en cada test
- Mantener la documentación de auditoría y checklist actualizada

### [INVENTARIO]
- Mejoras UI menores pendientes (optimización, no bloqueante)
- Loading states podrían mejorarse

### [MAIN Y MÓDULOS SECUNDARIOS]
- Uso de print para logs y advertencias, sin logging estructurado
- No hay auditoría de accesos ni monitoreo de experiencia de usuario
- Falta de pruebas automáticas de fallback visual y recuperación ante fallos de recursos gráficos

---

## 4. Mejoras opcionales, limpieza y recomendaciones generales

### [BASE DE DATOS]
- Crear tabla `productos` consolidada (inventario, herrajes, vidrios, materiales) [OPCIONAL]
- Migrar datos a `productos` y verificar integridad [OPCIONAL]

### [GENERAL]
- Eliminar código muerto y helpers no usados
- Auditar utilidades y helpers no referenciados (ej: `BackupIntegration`, `InventoryIntegration`, `SmartTooltip`, validadores avanzados)
- Eliminar o documentar clases/componentes modernos no integrados
- Mejorar feedback visual y experiencia de usuario: unificar notificaciones visuales, loading indicators y manejo de errores
- Estandarizar iconografía y nomenclatura visual
- Aumentar cobertura de tests y edge cases: integración, edge cases en formularios, roles y permisos, sanitización activa, pruebas automáticas de visualización y fallback de UI

### [SISTEMA / LIMPIEZA]
- Archivos de respaldo no eliminados (.backup, model_refactorizado.py obsoletos)
- Queries hardcodeadas en archivos backup (no crítico)

---

## 5. Acciones útiles y mejoras incrementales sugeridas

- Integrar monitoreo de experiencia de usuario y reportes automáticos de errores
- Añadir métricas de uso y performance en cada módulo
- Mejorar documentación de expected outcomes y criterios de aceptación visual
- Implementar onboarding interactivo y ayuda contextual en la UI
- Soporte para accesibilidad avanzada (navegación por teclado, lectores de pantalla)
- Exportar datos: Botón para exportar la tabla o los datos filtrados a Excel/CSV/PDF
- Historial de cambios: Opción para ver el historial de modificaciones de un registro
- Acciones masivas: Selección múltiple para eliminar, actualizar o exportar varios registros a la vez
- Favoritos o marcadores: Permitir marcar registros frecuentes o importantes
- Búsqueda avanzada: Filtros combinados, búsqueda por rangos de fechas, estados, etc.
- Feedback inmediato: Notificaciones visuales al guardar, eliminar, o ante errores
- Accesos rápidos: Atajos de teclado para las acciones principales (nuevo, guardar, buscar, etc.)
- Ayuda contextual: Tooltips explicativos y enlaces a documentación o tutoriales
- Recuperar borrados recientes: Opción de deshacer o recuperar registros eliminados recientemente
- Visualización adaptable: Cambiar entre vista tabla, tarjetas, o gráficos según el contexto

---

## 6. Errores y advertencias detectados en la última ejecución (11/08/2025)

### Errores críticos
- [x] ~~Obras: cannot import name 'ObrasView' from 'rexus.modules.obras.view'~~ ✅ RESUELTO
- [x] ~~Vidrios: cannot import name 'VidriosView' from 'rexus.modules.vidrios.view'~~ ✅ RESUELTO
- [x] ~~Inventario: name 'DataSanitizer' is not defined~~ ✅ RESUELTO
- [x] ~~Inventario: wrapped C/C++ object of type RexusButton has been deleted~~ ✅ RESUELTO (corregido método cleanup)
- [x] ~~Pedidos: 'SQLQueryManager' object has no attribute 'get_query'~~ ✅ RESUELTO
- [x] ~~Compras: Tablas 'compras' y 'detalle_compras' no existen en la base de datos~~ ✅ RESUELTO
- [x] ~~Mantenimiento: type object 'RexusColors' has no attribute 'DANGER_LIGHT'~~ ✅ RESUELTO
- [x] ~~Auditoría: 'AuditoriaModel' object has no attribute 'data_sanitizer'~~ ✅ RESUELTO
- [x] ~~Auditoría: 'AuditoriaView' object has no attribute 'cargar_registros_auditoría'~~ ✅ RESUELTO
- [ ] Usuarios: 'NoneType' object has no attribute 'cursor' (al obtener usuarios optimizado)
- [x] ~~General: name 'QHBoxLayout' is not defined (en configuración real)~~ ✅ RESUELTO
- [ ] ComprasView: Error inicializando protección XSS

### Warnings y problemas menores
- [ ] Métodos de carga de datos no encontrados en varios controladores (cargar_logistica, cargar_compras, cargar_auditoria, etc.)
- [ ] Varios módulos usan fallback por errores de inicialización
- [ ] QtWebEngine no disponible (no afecta si no usas mapas embebidos)
- [ ] QLayout: Attempting to add QLayout "" to QFrame "", which already has a layout (varios módulos)
- [ ] Error obteniendo registros: 'AuditoriaModel' object has no attribute 'data_sanitizer'
- [ ] Error obteniendo usuarios optimizado: 'NoneType' object has no attribute 'cursor'
- [ ] Error obteniendo compras: Invalid object name 'compras'
- [ ] Error obteniendo estadísticas: Invalid object name 'compras'
- [ ] Error obteniendo entregas: Incorrect syntax near the keyword 'ORDER'
- [ ] Error obteniendo pedidos: 'SQLQueryManager' object has no attribute 'get_query'
- [ ] Error obteniendo usuarios: 'NoneType' object has no attribute 'cursor'
- [ ] Error creando configuración real: name 'QHBoxLayout' is not defined

