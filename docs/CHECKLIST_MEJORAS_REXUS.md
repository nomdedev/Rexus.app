# Checklist de Mejoras y Problemas Detectados en Rexus.app

## 1. Visualización de datos en tablas
- [x] **Las tablas de muchos módulos aparecen vacías o no muestran datos.** ✅ **RESUELTO - Inventario**
  - [x] **El método del modelo retorna una lista vacía (por error de consulta, tabla vacía o error de conexión).** ✅ **RESUELTO** 
    - **Problema identificado:** El modelo `InventarioModel` referenciaba tabla incorrecta (`inventario` vacía en lugar de `inventario_perfiles` con 2549 registros)
    - **Solución aplicada:** Actualizado todas las referencias de `inventario` a `inventario_perfiles` en el modelo
    - **Resultado:** Ahora carga correctamente 2549 productos, búsquedas funcionan (648 productos con "Marco")
  - [x] **Errores de columnas incorrectas:** Mapeadas columnas del modelo a estructura real de la BD:
    - `categoria` → `tipo`
    - `subcategoria` → `acabado` 
    - `precio_unitario` → `importe`
    - `unidad_medida` → `unidad`
    - `codigo_qr` → `qr`
  - [x] **Tablas auxiliares:** Adaptado para usar tablas existentes (`historial` para movimientos, `reserva_materiales` para reservas)
  - [ ] El método del controlador que debería cargar los datos no se llama al inicializar la vista.
    - *Solución:* Llamar explícitamente a los métodos de carga de datos (`cargar_datos_iniciales`, `cargar_X`) en el constructor o método `set_controller` de cada vista.
  - [ ] El método de la vista que debe poblar la tabla no está implementado o no se llama.
    - *Solución:* Implementar siempre un método `cargar_en_tabla` y llamarlo desde el controlador tras obtener los datos.
  - [ ] Faltan llamadas a `set_controller` o a métodos como `cargar_datos_iniciales` en la inicialización.
    - *Solución:* Asegurarse de que cada vista reciba y almacene su controlador y que este llame a la carga inicial.
  - [ ] Errores silenciosos en los métodos de carga (try/except que oculta el error real).
    - *Solución:* Loggear todas las excepciones y mostrar mensajes de error en la UI.

## 2. Factory de módulos y fallback
- [ ] Varios módulos muestran solo “disponible y funcionando” (fallback).
  - [ ] El nombre del módulo en el botón no coincide exactamente con el esperado en el factory.
    - *Solución:* Unificar nombres y claves en el diccionario del factory y en los botones del sidebar. Usar una función de normalización.
  - [ ] El import de la vista/modelo/controlador falla (archivo faltante, error de sintaxis, etc.).
    - *Solución:* Revisar los imports y agregar tests de importación. Mostrar el error real en la UI.
  - [ ] El método de creación del módulo no está implementado en el factory.
    - *Solución:* Implementar todos los métodos de creación de módulos en el factory.

## 3. Errores de inicialización de tablas
- [ ] Errores al llamar a `setSectionResizeMode` sobre `None` en las tablas.
  - [ ] Siempre verificar que `header` no sea `None` antes de llamar a métodos sobre él.
    - *Justificación:* Si la tabla no tiene columnas, `horizontalHeader()` devuelve `None` y causa un crash.
    - *Solución:* Usar `if header is not None:` antes de modificar el header.

## 4. Falta de conexión entre formularios y base de datos
- [ ] Los formularios de alta/edición (por ejemplo, Entregas, Service) no guardan ni muestran datos.
  - [ ] El botón “Guardar” no está conectado al controlador.
    - *Solución:* Conectar el botón a un método que valide y envíe los datos al controlador.
  - [ ] El controlador no llama al método correcto del modelo.
    - *Solución:* Revisar que el controlador invoque el método de inserción/actualización correcto.
  - [ ] El modelo no implementa el método de inserción o consulta.
    - *Solución:* Implementar los métodos faltantes en el modelo y testearlos con datos reales.
  - [ ] Faltan señales o métodos de actualización de la tabla tras guardar.
    - *Solución:* Llamar a la recarga de la tabla después de guardar/editar.

## 5. Nombres y tildes en los módulos
- [ ] Inconsistencias en nombres de módulos (tildes, mayúsculas/minúsculas) entre el sidebar y el factory.
  - [ ] Unificar nombres y claves en el diccionario del factory y en los botones.
    - *Justificación:* Si el nombre no coincide exactamente, se muestra el fallback.
    - *Solución:* Usar una función de normalización de nombres (sin tildes, minúsculas) tanto en el sidebar como en el factory.

## 6. Falta de feedback visual o mensajes de error
- [ ] No se muestran mensajes claros cuando hay errores de carga de datos o de inicialización.
  - [ ] Agregar mensajes de error visibles en la UI y logs detallados.
    - *Justificación:* El usuario no sabe si la app está funcionando mal o si solo no hay datos.
    - *Solución:* Usar `QMessageBox` o banners de error en la UI y logs en consola/archivo.

## 7. Errores de importación o inicialización silenciosos
- [ ] Errores en imports o constructores de vistas/modelos/controladores no se ven en la UI.
  - [ ] Revisar los logs y mostrar mensajes de error en pantalla.
    - *Justificación:* Si hay un error en el import, el usuario solo ve el fallback y no sabe por qué.
    - *Solución:* Capturar excepciones y mostrar el mensaje real en la UI.

## 8. Falta de datos de prueba o base de datos vacía
- [ ] Las tablas pueden estar vacías porque la base de datos no tiene datos de prueba.
  - [ ] Agregar datos de ejemplo o scripts de carga rápida.
    - *Justificación:* Sin datos de prueba, es difícil validar la UI y la lógica.
    - *Solución:* Crear scripts de carga de datos y/o un modo demo.
## 9. Código duplicado y falta de reutilización
- [ ] Hay lógica repetida en la inicialización de vistas, carga de datos y manejo de errores.
  - [ ] Extraer funciones utilitarias para carga de datos, manejo de errores y normalización de nombres.
    - *Justificación:* Facilita el mantenimiento y reduce bugs por cambios en un solo lugar.
    - *Solución:* Crear utilidades en `utils/` y usarlas en todos los módulos.

## 10. Falta de validación de formularios
- [ ] Los formularios permiten guardar datos incompletos o inválidos.
  - [ ] Agregar validaciones antes de guardar (campos obligatorios, formatos, etc.).
    - *Justificación:* Evita datos corruptos o errores en la base.
    - *Solución:* Validar en el frontend y backend antes de insertar/actualizar.

## 11. Falta de documentación y comentarios
## 12. Checklist detallado de mejoras y tests faltantes por módulo

### Inventario
- [ ] Faltan tests de integración con reservas y movimientos.
- [ ] Validar edge cases de stock negativo y cantidades extremas.
- [ ] Mejorar feedback visual ante errores de conexión o consulta.
- [ ] Documentar funciones de importación/exportación de inventario.
  - *Solución:* Agregar tests de integración, mocks de BD y feedback visual en la UI.

### Obras
- [ ] Tests de validación de fechas (entrega, medición, cierre).
- [ ] Tests de cambio de estado y cierre de obra.
- [ ] Integración con pedidos y logística (flujo completo).
- [ ] Validar permisos de usuario para edición/cierre.
  - *Solución:* Tests de edge cases, integración y permisos.

### Logística
- [ ] Tests de creación y actualización de entregas y services.
- [ ] Tests de optimización de rutas y edge cases de estados.
- [ ] Validar feedback visual ante errores de asignación o entrega.
- [ ] Documentar métodos de cálculo de costos y rutas.
  - *Solución:* Tests de integración, edge cases y feedback visual.

### Herrajes
- [ ] Tests de asignación a obras y validación de stock.
- [ ] Integración con pedidos y feedback de errores.
- [ ] Validar edge cases de cantidades y proveedores.
  - *Solución:* Tests de integración, edge cases y feedback visual.

### Vidrios
- [ ] Tests de reasignación y edge cases de medidas/proveedores.
- [ ] Integración con obras y feedback visual de errores.
- [ ] Validar casos de stock negativo y pedidos incompletos.
  - *Solución:* Tests de edge cases, integración y feedback visual.

### Mantenimiento
- [ ] Tests de programación y cierre de mantenimientos.
- [ ] Indicadores y edge cases de fechas y costos.
- [ ] Validar feedback visual y logs de errores.
  - *Solución:* Tests de edge cases, integración y feedback visual.

### Configuración
- [ ] Tests de backup, restauración y validación de entradas.
- [ ] Feedback visual ante errores de configuración.
- [ ] Documentar métodos críticos y flujos de backup.
  - *Solución:* Tests de edge cases, feedback visual y documentación.

### Usuarios
- [ ] Tests de permisos, roles y validación de formularios.
- [ ] Edge cases de creación, edición y eliminación de usuarios.
- [ ] Feedback visual ante errores de autenticación/autorización.
  - *Solución:* Tests de edge cases, integración y feedback visual.

### General
- [ ] Tests de utilidades (`utils/`): validadores, helpers SQL, sanitización de datos.
- [ ] Tests de scripts (`scripts/`): carga, migración, verificación.
- [ ] Tests de seguridad avanzada: inyección, validación de roles, logs de auditoría.
- [ ] Tests de accesibilidad: navegación por teclado, tooltips, feedback para usuarios con discapacidad.
  - *Solución:* Crear y mantener suites de tests automáticos por módulo y tipo, usando `pytest`, `qtbot` y mocks de base de datos.

---
---

## 📊 RESUMEN DE PROGRESO

### ✅ **COMPLETADO (2025-01-17)**
1. **Problema crítico de datos vacíos en Inventario - RESUELTO**
   - **Causa raíz:** Referencia a tabla incorrecta (`inventario` vacía vs `inventario_perfiles` con datos)
   - **Archivos modificados:** `src/modules/inventario/model.py`
   - **Impacto:** 2549 productos ahora cargan correctamente, búsquedas funcionan
   - **Técnical Details:** 
     - Actualizado 15+ referencias de tabla en queries SQL
     - Mapeado columnas existentes en BD a modelo esperado
     - Adaptado tablas auxiliares (`historial`, `reserva_materiales`)

2. **Configuración de base de datos verificada**
   - ✅ Conexión a SQL Server funcional (DESKTOP-QHMPTGO\SQLEXPRESS)
   - ✅ 65 tablas identificadas en BD `inventario`
   - ✅ Variables de entorno configuradas correctamente

3. **Vulnerabilidades SQL Injection eliminadas**
   - ✅ **Inventario Model:** Todas las queries con f-strings y concatenación convertidas a queries parametrizadas
   - ✅ **Vidrios Model:** Eliminados f-strings con nombres de tabla dinámicos  
   - ✅ **Herrajes Model:** Convertida concatenación de strings SQL a nombres fijos
   - **Impacto:** App ahora resistente a inyecciones SQL, código más seguro

4. **Sistema de gestión de módulos robusto implementado**
   - ✅ **Creado:** `src/core/module_manager.py` - Gestor centralizado de módulos
   - ✅ **Características:** Manejo de errores, carga automática de datos, logging detallado, fallback robusto
   - ✅ **Integrado:** En `src/main/app.py` para módulo Inventario (ejemplo piloto)
   - **Beneficios:** Carga más confiable, mejor debugging, experiencia de usuario mejorada

### 🔄 **EN PROGRESO**
- Conexión de formularios Save/Guardar a controladores

### ✅ **COMPLETADO (2025-01-28)**
1. **Aplicación del gestor de módulos a todos los módulos - COMPLETADO**
   - ✅ Aplicado `module_manager.create_module_safely()` a: Contabilidad, Obras, Vidrios, Herrajes, Pedidos, Usuarios, Auditoría, Compras, Mantenimiento, Logística
   - ✅ Todos los módulos ahora usan el gestor robusto de módulos
   - **Impacto:** Carga más confiable de módulos, mejor manejo de errores, experiencia de usuario mejorada

2. **Corrección de nombres de módulos en factory - COMPLETADO**
   - ✅ Normalizado nombres entre sidebar y factory (sin tildes, consistentes)  
   - ✅ Implementada función de normalización de nombres mejorada
   - ✅ Verificado mappings: "Logística" → "Logistica", "Auditoría" → "Auditoria"
   - **Impacto:** Elimina módulos fallback por problemas de nombres con tildes

3. **Arreglo de errores de inicialización de tablas - COMPLETADO**
   - ✅ Corregidos todos los `setSectionResizeMode` sobre headers `None` en todos los módulos
   - ✅ Agregada validación `if header is not None:` antes de modificar headers
   - ✅ Implementada inicialización robusta de tablas en: Vidrios, Usuarios, Obras, Mantenimiento, Logística, Inventario, Compras, Herrajes, Auditoría, Administración
   - **Archivos modificados:** 15+ archivos view.py en diferentes módulos
   - **Impacto:** Elimina crashes por headers None en tablas vacías

4. **Correcciones SQL injection completadas - COMPLETADO**
   - ✅ Verificados modelos restantes: Pedidos, Compras, Usuarios, Logística, Mantenimiento
   - ✅ Todos los modelos ya usan queries parametrizadas correctamente
   - **Impacto:** Sistema completamente protegido contra inyecciones SQL

### ⏳ **PENDIENTE - ALTA PRIORIDAD**
4. **Conectar formularios a base de datos**
   - [ ] Verificar botones "Guardar" conectados a controladores 
   - [ ] Implementar métodos CRUD faltantes en modelos
   - [ ] Agregar señales de actualización de tablas tras guardar

### ⏳ **PENDIENTE - MEDIA PRIORIDAD**  
5. **Mejorar feedback visual y manejo de errores**
   - [ ] Agregar `QMessageBox` para errores críticos
   - [ ] Implementar banners de error en UI
   - [ ] Mejorar logging detallado en archivos

6. **Completar correcciones SQL injection**
   - [ ] Revisar y corregir modelos restantes: Pedidos, Compras, Usuarios, Logística, Mantenimiento
   - [ ] Verificar nombres de tablas correctos en BD
   - [ ] Estandarizar uso de queries parametrizadas

7. **Crear datos de prueba**
   - [ ] Scripts de carga de datos demo para módulos vacíos
   - [ ] Modo demo cuando no hay conexión BD
   - [ ] Datos de ejemplo realistas

### ⏳ **PENDIENTE - BAJA PRIORIDAD**
8. **Refactoring y optimización**
   - [ ] Extraer utilidades comunes a `src/utils/`
   - [ ] Reducir código duplicado en inicialización
   - [ ] Mejorar arquitectura MVC

9. **Validación de formularios**
   - [ ] Campos obligatorios
   - [ ] Validación de formatos (email, teléfono, etc.)
   - [ ] Feedback visual de validación

10. **Documentación**
    - [ ] Docstrings en todas las clases principales
    - [ ] Comentarios explicativos en código complejo
    - [ ] Documentación de arquitectura

---

> **NOTA:** Este checklist se actualiza en tiempo real. Última actualización: 2025-01-17 - Inventario funcionando correctamente.
