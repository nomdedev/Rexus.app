# Checklist de Verificación por Módulo

Este checklist debe completarse para cada módulo del sistema, verificando la carga de datos, feedback visual, almacenamiento y tests.

## Información del Módulo

- **Nombre del módulo:** _____________
- **Responsable:** _____________
- **Fecha de verificación:** _____________
- **Versión analizada:** _____________

---

## 1. Verificación de Carga de Datos

### 1.1 Estructura de Datos
- [ ] **Modelo de datos definido correctamente**
  - [ ] Clases/tablas principales identificadas
  - [ ] Relaciones entre entidades documentadas
  - [ ] Campos obligatorios y opcionales definidos
  - [ ] Tipos de datos apropiados
  - [ ] Restricciones de integridad implementadas

- [ ] **Conexión a base de datos**
  - [ ] Conexión se establece correctamente
  - [ ] Pool de conexiones configurado (si aplica)
  - [ ] Timeouts apropiados configurados
  - [ ] Reconexión automática implementada
  - [ ] Cierre adecuado de conexiones

### 1.2 Operaciones CRUD
- [ ] **Create (Crear)**
  - [ ] Datos se insertan correctamente
  - [ ] Validaciones aplicadas antes de insertar
  - [ ] Manejo de IDs autogenerados
  - [ ] Transacciones implementadas apropiadamente
  - [ ] Rollback en caso de error

- [ ] **Read (Leer)**
  - [ ] Consultas SELECT funcionan correctamente
  - [ ] Filtros y búsquedas implementados
  - [ ] Paginación funciona (si aplica)
  - [ ] Ordenamiento por columnas funciona
  - [ ] Joins y relaciones cargan correctamente

- [ ] **Update (Actualizar)**
  - [ ] Actualizaciones se aplican correctamente
  - [ ] Solo se actualizan campos modificados
  - [ ] Versionado/concurrencia manejada
  - [ ] Auditoría de cambios implementada
  - [ ] Validaciones aplicadas antes de actualizar

- [ ] **Delete (Eliminar)**
  - [ ] Eliminaciones funcionan correctamente
  - [ ] Soft delete implementado (si aplica)
  - [ ] Eliminación en cascada configurada apropiadamente
  - [ ] Verificación de dependencias antes de eliminar
  - [ ] Auditoría de eliminaciones

### 1.3 Validación de Datos
- [ ] **Validación de entrada**
  - [ ] Tipos de datos validados
  - [ ] Rangos y límites verificados
  - [ ] Formatos específicos validados (email, teléfono, etc.)
  - [ ] Campos requeridos verificados
  - [ ] Sanitización de datos implementada

- [ ] **Validación de negocio**
  - [ ] Reglas de negocio aplicadas
  - [ ] Unicidad verificada donde corresponde
  - [ ] Relaciones válidas verificadas
  - [ ] Estados válidos verificados
  - [ ] Permisos verificados

---

## 2. Verificación de Feedback Visual

### 2.1 Indicadores de Estado
- [ ] **Indicadores de carga**
  - [ ] Spinner/loading mostrado durante operaciones lentas
  - [ ] Cursor cambia a "wait" durante procesamientos
  - [ ] Barras de progreso para operaciones largas
  - [ ] Textos informativos durante esperas
  - [ ] Deshabilitación de controles durante procesamiento

- [ ] **Estados de la interfaz**
  - [ ] Botones reflejan el estado actual
  - [ ] Campos se habilitan/deshabilitan apropiadamente
  - [ ] Pestañas/secciones muestran estado correcto
  - [ ] Contadores se actualizan en tiempo real
  - [ ] Badges/etiquetas reflejan datos actuales

### 2.2 Mensajes al Usuario
- [ ] **Mensajes de éxito**
  - [ ] Confirmación de operaciones exitosas
  - [ ] Detalles relevantes incluidos
  - [ ] Duración apropiada de visualización
  - [ ] Estilo consistente con la aplicación
  - [ ] Posicionamiento apropiado en la UI

- [ ] **Mensajes de error**
  - [ ] Errores mostrados de forma clara
  - [ ] Mensajes específicos y útiles
  - [ ] Sugerencias de corrección incluidas
  - [ ] No se expone información sensible
  - [ ] Logging de errores implementado

- [ ] **Mensajes informativos**
  - [ ] Avisos apropiados para acciones importantes
  - [ ] Confirmaciones antes de operaciones destructivas
  - [ ] Help/tooltips disponibles donde es útil
  - [ ] Mensajes de validación en tiempo real
  - [ ] Información contextual relevante

### 2.3 Actualización de Datos
- [ ] **Refresh automático**
  - [ ] Tablas se actualizan tras modificaciones
  - [ ] Contadores se recalculan automáticamente
  - [ ] Relaciones se refrescan apropiadamente
  - [ ] Cache se invalida cuando es necesario
  - [ ] UI se sincroniza con base de datos

- [ ] **Refresh manual**
  - [ ] Botón de actualizar disponible
  - [ ] F5/Ctrl+R funcionan apropiadamente
  - [ ] Refresh preserva filtros y ordenamiento
  - [ ] Posición actual se mantiene tras refresh
  - [ ] Selecciones se mantienen si es apropiado

---

## 3. Verificación de Almacenamiento en BD

### 3.1 Integridad de Datos
- [ ] **Consistencia**
  - [ ] Datos se almacenan en formato correcto
  - [ ] Codificación de caracteres apropiada (UTF-8)
  - [ ] Decimales con precisión correcta
  - [ ] Fechas en formato estándar
  - [ ] Referencias foráneas válidas

- [ ] **Transacciones**
  - [ ] Operaciones complejas usan transacciones
  - [ ] Rollback funciona correctamente en errores
  - [ ] Aislamiento apropiado configurado
  - [ ] Deadlocks manejados apropiadamente
  - [ ] Timeouts de transacción configurados

### 3.2 Rendimiento
- [ ] **Consultas optimizadas**
  - [ ] Índices apropiados definidos
  - [ ] Consultas N+1 evitadas
  - [ ] JOINs optimizados
  - [ ] LIMIT/TOP usados para grandes datasets
  - [ ] Consultas lentas identificadas y optimizadas

- [ ] **Manejo de memoria**
  - [ ] Resultados grandes paginados
  - [ ] Conexiones cerradas apropiadamente
  - [ ] Cursores liberados tras uso
  - [ ] Memoria liberada tras operaciones grandes
  - [ ] Cache implementado donde es beneficioso

### 3.3 Seguridad
- [ ] **Prevención de inyección SQL**
  - [ ] Consultas parametrizadas usadas
  - [ ] Input sanitizado antes de uso
  - [ ] Validación de nombres de tabla/columna
  - [ ] Escapado apropiado de caracteres especiales
  - [ ] No concatenación directa de SQL

- [ ] **Permisos y acceso**
  - [ ] Usuario de BD tiene permisos mínimos necesarios
  - [ ] Auditoría de accesos implementada
  - [ ] Encriptación de datos sensibles
  - [ ] Logs de seguridad configurados
  - [ ] Acceso a BD desde aplicación únicamente

---

## 4. Verificación de Tests

### 4.1 Cobertura de Tests
- [ ] **Tests unitarios**
  - [ ] Métodos principales probados
  - [ ] Validaciones probadas
  - [ ] Manejo de errores probado
  - [ ] Edge cases cubiertos
  - [ ] Mocks usados apropiadamente

- [ ] **Tests de integración**
  - [ ] Operaciones de BD probadas
  - [ ] Flujos completos probados
  - [ ] Interacción entre módulos probada
  - [ ] APIs externas mockeadas
  - [ ] Configuraciones diferentes probadas

### 4.2 Edge Cases Identificados
- [ ] **Datos límite**
  - [ ] Strings vacíos/null
  - [ ] Números muy grandes/pequeños
  - [ ] Fechas límite (1900, 2100, etc.)
  - [ ] Arrays/listas vacías
  - [ ] Caracteres especiales/unicode

- [ ] **Condiciones de error**
  - [ ] BD no disponible
  - [ ] Timeout de operaciones
  - [ ] Memoria insuficiente
  - [ ] Permisos insuficientes
  - [ ] Datos corruptos

- [ ] **Concurrencia**
  - [ ] Múltiples usuarios simultáneos
  - [ ] Modificaciones concurrentes
  - [ ] Deadlocks
  - [ ] Race conditions
  - [ ] Estados inconsistentes

### 4.3 Tests de Seguridad
- [ ] **Inyección SQL**
  - [ ] Intentos de inyección probados
  - [ ] Validación de input probada
  - [ ] Escapado de caracteres probado
  - [ ] Consultas parametrizadas verificadas
  - [ ] Logs de intentos maliciosos

- [ ] **XSS y otros ataques**
  - [ ] Input malicioso probado
  - [ ] Sanitización verificada
  - [ ] Output encoding verificado
  - [ ] Validación de URLs probada
  - [ ] Subida de archivos segura probada

---

## 5. Sugerencias y Mejoras Identificadas

### 5.1 Mejoras de Rendimiento
- [ ] **Identificadas:**
  - [ ] _________________________________
  - [ ] _________________________________
  - [ ] _________________________________

### 5.2 Mejoras de UX
- [ ] **Identificadas:**
  - [ ] _________________________________
  - [ ] _________________________________
  - [ ] _________________________________

### 5.3 Mejoras de Seguridad
- [ ] **Identificadas:**
  - [ ] _________________________________
  - [ ] _________________________________
  - [ ] _________________________________

### 5.4 Mejoras de Calidad de Código
- [ ] **Identificadas:**
  - [ ] _________________________________
  - [ ] _________________________________
  - [ ] _________________________________

---

## 6. Edge Cases Adicionales Sugeridos

### 6.1 Edge Cases de Datos
- [ ] Probar con base de datos vacía
- [ ] Probar con millones de registros
- [ ] Probar con caracteres especiales (émojis, acentos, símbolos)
- [ ] Probar con nombres muy largos (>255 caracteres)
- [ ] Probar con números negativos donde no se esperan
- [ ] Probar con fechas futuras/pasadas extremas
- [ ] Probar con decimales con muchos dígitos
- [ ] Probar con arrays/listas muy grandes
- [ ] Probar con JSON malformado
- [ ] Probar con archivos muy grandes

### 6.2 Edge Cases de Red/Sistema
- [ ] Probar con conexión de red lenta
- [ ] Probar con pérdida intermitente de conexión
- [ ] Probar con BD en mantenimiento
- [ ] Probar con memoria RAM limitada
- [ ] Probar con espacio en disco limitado
- [ ] Probar con múltiples ventanas/pestañas abiertas
- [ ] Probar con cambio de zona horaria
- [ ] Probar con diferentes resoluciones de pantalla
- [ ] Probar con diferentes navegadores/versiones
- [ ] Probar con antivirus bloqueando archivos

### 6.3 Edge Cases de Usuario
- [ ] Probar navegación muy rápida (clicks múltiples)
- [ ] Probar con usuario sin permisos
- [ ] Probar con sesión expirada
- [ ] Probar con múltiples logins simultáneos
- [ ] Probar con usuario inactivo por mucho tiempo
- [ ] Probar con datos inconsistentes de sesión previa
- [ ] Probar copiar/pegar en campos no esperados
- [ ] Probar drag & drop donde no está permitido
- [ ] Probar con JavaScript deshabilitado
- [ ] Probar con cookies deshabilitadas

---

## Resumen de Verificación

### Estadísticas
- **Total de checks:** _______ / _______
- **Porcentaje completado:** _______ %
- **Críticos faltantes:** _______
- **Mejoras identificadas:** _______

### Estado General
- [ ] ✅ Módulo cumple todos los estándares
- [ ] ⚠️ Módulo necesita mejoras menores
- [ ] ❌ Módulo necesita mejoras críticas

### Próximos Pasos
1. _________________________________
2. _________________________________
3. _________________________________

### Notas Adicionales
_________________________________________________
_________________________________________________
_________________________________________________

---

**Verificador:** _________________ **Fecha:** _________ **Firma:** _________
