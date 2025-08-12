con- [ ] Eliminar todas las contraseñas, usuarios y credenciales hardcodeadas en el código fuente y archivos .env de ejemplo. Migrar a variables de entorno seguras y documentar el uso correcto para producción y testing.
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
- Migrar queries hardcodeadas restantes en archivos backup a SQL externos (~146 ocurrencias)

### [LOGÍSTICA]
- Error: `'SQLQueryManager' object has no attribute 'get_query'`
- Error: `'LogisticaView' object has no attribute 'cargar_entregas_en_tabla'`
- Mejorar organización visual y layout de pestañas (Transportes, Estadísticas, Servicios, Mapa)
  - Problemas: paneles apilados, botones desproporcionados, falta de separación visual, layout saturado, jerarquía visual deficiente, placeholders confusos, splitters desbalanceados, proporciones no responsivas, etc.

### [API]
- Revisar manejo seguro de claves JWT y almacenamiento de secretos
- Validar exhaustivamente los datos de entrada en todos los endpoints
- Revisar protección contra ataques comunes: inyección, XSS, CSRF, enumeración de usuarios
- Implementar autenticación real con hash de contraseñas y usuarios en base de datos
- Añadir cifrado/anonimización de datos sensibles en logs (CORE)

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

### [LOGÍSTICA]
- Optimizar responsividad y compactación visual en todas las pestañas
- Mejorar placeholders de gráficos y fallback de mapa
- Añadir iconografía y colores para estados de servicios

### [INVENTARIO / VIDRIOS]
- Aplicar estilos minimalistas específicos de Logística (método `aplicar_estilos()`)
- Reducir tamaños de botones y campos de entrada
- Unificar colores GitHub-style
- Implementar pestañas con estilo Logística

### [MAIN Y MÓDULOS SECUNDARIOS]
- Migrar todos los estilos a StyleManager y QSS centralizados
- Unificar componentes visuales con StandardComponents
- Implementar feedback visual consistente (notificaciones, loading, errores)
- Integrar monitoreo de experiencia de usuario y pruebas automáticas de UI
- Estandarizar iconografía y nomenclatura de métodos visuales

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
- [ ] Obras: cannot import name 'ObrasView' from 'rexus.modules.obras.view'
- [ ] Vidrios: cannot import name 'VidriosView' from 'rexus.modules.vidrios.view'
- [ ] Inventario: name 'DataSanitizer' is not defined
- [ ] Inventario: wrapped C/C++ object of type RexusButton has been deleted
- [ ] Pedidos: 'SQLQueryManager' object has no attribute 'get_query'
- [ ] Compras: Tablas 'compras' y 'detalle_compras' no existen en la base de datos
- [ ] Mantenimiento: type object 'RexusColors' has no attribute 'DANGER_LIGHT'
- [ ] Auditoría: 'AuditoriaModel' object has no attribute 'data_sanitizer'
- [ ] Auditoría: 'AuditoriaView' object has no attribute 'cargar_registros_auditoría'
- [ ] Usuarios: 'NoneType' object has no attribute 'cursor' (al obtener usuarios optimizado)
- [ ] General: name 'QHBoxLayout' is not defined (en configuración real)
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

---

## 7. Errores técnicos detectados automáticamente (última revisión 12/08/2025)

- [ ] `config.py`: La función `get_env_var` supera la complejidad cognitiva permitida (16 > 15). Refactorizar para simplificar la lógica y mejorar mantenibilidad.
- [ ] `two_factor_auth.py`: Posible vector de SQL injection en la línea donde se construye la query con interpolación de nombre de tabla:
      `query = f"UPDATE [{tabla_validada}] SET configuracion_personal = ? WHERE id = ?"`
      Revisar validación estricta de `tabla_validada` y considerar alternativas más seguras para evitar inyección.

---

## 8. Errores técnicos detectados automáticamente en módulos (última revisión 12/08/2025)

### [LOGÍSTICA]
- [ ] Definir constantes para literales duplicados: "Tabla de transportes no disponible", ".html", "✏️ Editar", "En tránsito", "Estado:", "Almacén Central", "Calle 7 entre 47 y 48, La Plata", "Sucursal Norte", "Av. 13 y 44, La Plata", "Depósito Sur", "Calle 120 y 610, La Plata", "Centro Distribución", "Av. 1 y 60, La Plata", "Buenos Aires", "La Plata", "Validación".
- [ ] El método mostrar_mensaje recibe argumentos de más en varias llamadas (espera máximo 2).
- [ ] Agregar comentario o implementación a métodos vacíos como actualizar_estado_botones.
- [ ] Reemplazar Exception genérico por una excepción más específica en el manejo de errores de mapa y dependencias.
- [ ] Renombrar variables locales como QWebEngineView para cumplir con el estándar de nombres.
- [ ] Eliminar variables locales no usadas como stats_actualizadas.
- [ ] Eliminar o refactorizar código inalcanzable detectado.
- [ ] Refactorizar funciones con complejidad cognitiva alta: crear_panel_filtros_servicios_optimizado, eliminar_transporte_seleccionado.
- [ ] Usar string normal en lugar de f-string sin campos de reemplazo.
- [ ] Evitar try/except/pass (B110) en varios bloques.

### [UTILS]
- [ ] `two_factor_auth.py`: Posible vector de inyección SQL por construcción de query basada en string (B608). Revisar uso de f-string en queries SQL.
- [ ] `rexus_styles.py`: Varios campos y métodos no cumplen con las convenciones de nombres y pueden causar confusiones.

---

## scripts/production_readiness_audit.py
- Varias líneas: Uso de try/except/continue detectado (B112). Refactorizar para evitar el uso de continue en except.
- Varias líneas: Variable local "e" no utilizada en except Exception as e. Eliminar si no se usa.
- Función check_hardcoded_credentials: Complejidad cognitiva 19 (máximo permitido: 15). Refactorizar para simplificar.
- Función check_missing_error_handling: Complejidad cognitiva 23 (máximo permitido: 15). Refactorizar para simplificar.
- Función check_debug_code: Complejidad cognitiva 19 (máximo permitido: 15). Refactorizar para simplificar.
- Función check_configuration_files: Complejidad cognitiva 22 (máximo permitido: 15). Refactorizar para simplificar.
- Varias líneas: Uso de f-string sin campos de reemplazo, usar string normal en su lugar.

## scripts/refactorizacion_inventario_completa.py
- Varias líneas: Uso de f-string sin campos de reemplazo, usar string normal en su lugar.

## scripts/progress_audit.py
- Línea 7: Uso de subprocess, revisar implicancias de seguridad (B404).
- Línea 43: subprocess.run con path parcial (B607) y posible ejecución de input no confiable (B603).
- Función check_sql_vulnerabilities: Complejidad cognitiva 17 (máximo permitido: 15). Refactorizar.
- Función main: Complejidad cognitiva 25 (máximo permitido: 15). Refactorizar.
- Varias líneas: Uso de f-string sin campos de reemplazo, usar string normal en su lugar.

## scripts/mejora_feedback_visual_simple.py
- Función mejorar_feedback_modulos: Complejidad cognitiva 22 (máximo permitido: 15). Refactorizar.
- Línea 48 y 56: Uso de f-string sin campos de reemplazo, usar string normal en su lugar.
- Función aplicar_mejoras_basicas: Complejidad cognitiva 24 (máximo permitido: 15). Refactorizar.

## scripts/auto_fix_sql_injection.py
- Varias líneas: Uso de f-string sin campos de reemplazo, usar string normal en su lugar.
- Línea 81: El parámetro file_path no se utiliza en la función add_sql_security_imports.
- Función fix_critical_files: Complejidad cognitiva 20 (máximo permitido: 15). Refactorizar.

## scripts/audit_production_config.py
- Varias líneas: Uso de try/except/continue detectado (B112). Refactorizar para evitar el uso de continue en except.
- Función detect_hardcoded_credentials: Complejidad cognitiva 19 (máximo permitido: 15). Refactorizar.
- Función detect_debug_configurations: Complejidad cognitiva 20 (máximo permitido: 15). Refactorizar.
- Función audit_config_files: Complejidad cognitiva 35 (máximo permitido: 15). Refactorizar.
- Varias líneas: Uso de f-string sin campos de reemplazo, usar string normal en su lugar.

## scripts/auditor_completo_sql.py
- Línea 172: Variable local "conexion" no utilizada.
- Líneas 216 y 237: Expresión usada como condición siempre constante, reemplazar por una condición válida.
- Línea 367, 430, 450, 456, 458, 461: Uso de f-string sin campos de reemplazo, usar string normal en su lugar.
- Línea 378: Usar una excepción más específica en lugar de Exception.

## scripts/database_performance_optimizer.py
- Línea 302: Posible vector de inyección SQL por construcción de query basada en string (B608). Revisar uso de f-string en queries SQL.

---

## rexus/ui/standard_components.py
- Línea 53: Definir una constante en vez de duplicar el literal 'Segoe UI' (aparece 4 veces).

## rexus/modules/logistica/view.py
- Varias líneas: Uso de try/except/pass detectado (B110). Refactorizar para evitar except/pass.
- Varias líneas: Definir una constante en vez de duplicar los literales "Tabla de transportes no disponible", ".html", "✏️ Editar", "En tránsito", "Estado:", "Almacén Central", "Calle 7 entre 47 y 48, La Plata", "Sucursal Norte", "Av. 13 y 44, La Plata", "Depósito Sur", "Calle 120 y 610, La Plata", "Centro Distribución", "Av. 1 y 60, La Plata", 'Buenos Aires', 'La Plata', "Validación".
- Varias líneas: El método mostrar_mensaje recibe más argumentos de los esperados.
- Línea 345: El método actualizar_estado_botones está vacío, agregar comentario o implementación.
- Línea 399: Definir una constante en vez de duplicar el literal '.html'.
- Líneas 416 y 424: Usar una excepción más específica en lugar de Exception.
- Varias líneas: Renombrar la variable local "QWebEngineView" para cumplir con la convención de nombres.
- Línea 1042 y 1228: Eliminar o refactorizar código inalcanzable.
- Varias líneas: Uso de f-string sin campos de reemplazo, usar string normal en su lugar.
- Línea 1242: Refactorizar la función crear_panel_filtros_servicios_optimizado para reducir la complejidad cognitiva (actual: 18, máximo: 15).
- Línea 1715: Refactorizar la función eliminar_transporte_seleccionado para reducir la complejidad cognitiva (actual: 16, máximo: 15).
- Línea 1843: Eliminar la variable local "stats_actualizadas" si no se utiliza.

## rexus/modules/herrajes/view.py
- Varias líneas: Definir una constante en vez de duplicar el literal de estilos para QTableWidget (aparece 3 veces).
- Varias líneas: Uso de f-string sin campos de reemplazo en setStyleSheet de QPushButton, usar string normal en su lugar.
- Varias líneas: Definir una constante en vez de duplicar el literal "Funcionalidad no disponible" (5 veces) y "Selección requerida" (3 veces).
- Línea 971: Refactorizar la función on_buscar para reducir la complejidad cognitiva (actual: 17, máximo: 15).
- Línea 1237: Refactorizar la función obtener_datos_fila para reducir la complejidad cognitiva (actual: 17, máximo: 15).

# =========================
# Errores detectados en rexus/modules/herrajes/model.py
# =========================
- Literal duplicado: "[ERROR HERRAJES] No hay conexión a la base de datos" se repite 3 veces. Definirlo como constante.

# =========================
# Errores detectados en rexus/modules/herrajes/inventario_integration.py
# =========================
- La función sincronizar_stock_herrajes tiene Complejidad Cognitiva 21 (máximo permitido: 15). Refactorizar para reducir complejidad.
- Literal duplicado: "Sin conexión a la base de datos" se repite 4 veces. Definirlo como constante.
- Variables locales no usadas: reemplazar "estado", "precio_inv" y "stock_inv" por "_" donde no se usan.
- Variable local no usada: reemplazar "precio" por "_" donde no se usa.

# =========================
# Errores detectados en rexus/modules/herrajes/improved_dialogs.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/herrajes/controller_simple.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/herrajes/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/herrajes/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/view_completa.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/view_integrated.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/auditoria/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/auditoria/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/auditoria/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/auditoria/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/detalle_model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/inventory_integration.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/proveedores_model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/configuracion/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/configuracion/database_config_dialog.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/configuracion/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/configuracion/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/configuracion/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/inventario/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/inventario/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/inventario/obras_asociadas_dialog.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/inventario/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/inventario/view_mejorada.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/inventario/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/mantenimiento/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/mantenimiento/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/mantenimiento/programacion_model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/mantenimiento/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/mantenimiento/view_completa.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/mantenimiento/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/notificaciones/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/notificaciones/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/notificaciones/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/notificaciones/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/cronograma_view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/data_mapper.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/model_adapter.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/model_clean.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/validator_extended.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/widgets_advanced.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/obras/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/pedidos/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/pedidos/improved_dialogs.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/pedidos/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/pedidos/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/pedidos/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/improved_dialogs.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/model_secure.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/security_dialog.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/security_features.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/view_admin.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/view_modern.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/usuarios/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/vidrios/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/vidrios/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/vidrios/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/vidrios/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/contabilidad/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/contabilidad/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/contabilidad/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/recursos_humanos/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/recursos_humanos/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/administracion/recursos_humanos/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/dialogs/dialog_proveedor.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/dialogs/dialog_seguimiento.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/dialogs/__init__.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/pedidos/controller.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/pedidos/model.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/pedidos/view.py
# =========================
- Sin errores detectados.

# =========================
# Errores detectados en rexus/modules/compras/pedidos/__init__.py
# =========================
- Sin errores detectados.

