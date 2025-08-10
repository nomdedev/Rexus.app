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

