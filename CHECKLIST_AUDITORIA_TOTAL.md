## 8. Usuarios y Seguridad
### Checklist
- [ ] Tests de login/logout (correcto e incorrecto)
- [ ] Tests de registro de usuario y validaciones
- [ ] Tests de recuperación de contraseña
- [ ] Tests de gestión de perfiles y permisos
- [ ] Tests de feedback visual ante errores de autenticación/autorización
- [ ] Tests de integración de roles y restricciones en la UI
- [ ] Tests de errores de seguridad y mensajes al usuario
- [ ] Estructura y documentación de tests

### Tests faltantes y ejemplos
- Test de login/logout (correcto e incorrecto) y feedback visual
- Test de registro de usuario y validaciones de campos obligatorios y duplicados
- Test de recuperación de contraseña y feedback visual
- Test de cambios de perfil y permisos, incluyendo restricciones de acceso
- Test de integración de roles y restricciones en la UI (botones, menús, acciones restringidas)
- Test de errores de autenticación/autorización y mensajes al usuario

---
# Auditoría de Tests y Checklist por Módulo - Rexus.app

Fecha: 20/08/2025

Este documento centraliza el checklist de auditoría y los tests faltantes para todos los módulos principales del sistema.

---

## Módulos cubiertos:
- Configuración
- Inventario
- Obras
- Compras
- Pedidos
- Vidrios
- Notificaciones

---


## 1. Configuración
### Checklist
- [x] Tests de inicialización de vista principal (Faltan tests de UI específicos)
- [ ] Tests de formularios y componentes visuales (No cubiertos)
- [ ] Flujos de usuario (llenado, envío, feedback visual) (No cubiertos)
- [ ] Mensajes de error y validaciones negativas (No cubiertos)
- [ ] Accesibilidad (contraste, teclado, focus) (Solo contraste general)
- [ ] Automatización UI (pytest-qt, qtbot, Selenium) (No implementado)
- [x] Métodos de negocio (guardar, cargar, validar) (Parcialmente cubiertos)
- [ ] Validaciones, persistencia, manejo de errores (Cobertura parcial)
- [ ] Casos límite y entradas inválidas (No cubiertos)
- [ ] Seguridad y control de acceso (No cubierto)
- [ ] Integración con otros módulos (No cubierto)
- [ ] Flujos completos multi-módulo (No cubierto)
- [ ] Errores de integración y recuperación (No cubierto)
- [x] Estructura de tests clara y modular (Aceptable)
- [ ] Tests reflejan comportamiento real (Parcial)
- [ ] Documentación suficiente (Mejorable)
- [ ] Feedback visual y notificaciones (No cubierto)
- [ ] Persistencia de configuraciones (No cubierto)
- [ ] Configuraciones avanzadas y restricciones (No cubierto)


### Tests faltantes y ejemplos
- Flujos de usuario completos en UI
	- Ejemplo: Simular cambio y guardado de configuración desde la UI, verificar feedback visual y persistencia.
- Pruebas de accesibilidad profunda
	- Ejemplo: Test de navegación por teclado y contraste en formularios de configuración.
- Integración con módulos dependientes (ej: Inventario, Usuarios)
	- Ejemplo: Cambiar una configuración y verificar su efecto en Inventario.
- Validaciones negativas y feedback visual de errores
	- Ejemplo: Intentar guardar una configuración inválida y verificar mensaje de error.
- Persistencia y recuperación de configuraciones
	- Ejemplo: Modificar configuración, reiniciar app y verificar que se mantenga el cambio.

---

---


## 2. Inventario
### Checklist
- [x] Tests de inicialización de vista principal (Cubierto en parte)
- [ ] Tests de formularios de alta, baja, modificación (No cubiertos)
- [ ] Flujos de usuario (input, submit, feedback) (No cubiertos)
- [ ] Validaciones de stock, errores y límites (Cobertura parcial)
- [ ] Accesibilidad y automatización UI (No implementado)
- [x] Métodos de negocio (agregar, quitar, actualizar stock) (Parcialmente cubiertos)
- [ ] Integración con Pedidos, Compras, Configuración (No cubierto)
- [x] Estructura y documentación de tests (Aceptable)


### Tests faltantes y ejemplos
- Pruebas de integración con Pedidos y Compras
	- Ejemplo: Registrar un pedido y verificar el descuento de stock en Inventario.
- Casos límite de stock y errores de concurrencia
	- Ejemplo: Intentar quitar más stock del disponible y verificar error.
- Feedback visual ante errores de inventario
	- Ejemplo: Simular error de stock y verificar mensaje en la UI.
- Flujos de usuario completos en UI
	- Ejemplo: Alta de producto desde la UI, validando feedback visual y actualización de tabla.

---

---


## 3. Obras
### Checklist
- [x] Tests de inicialización de vista y componentes (Cubierto)
- [ ] Formularios de creación y edición de obra (No cubiertos)
- [ ] Flujos de usuario y feedback visual (No cubiertos)
- [ ] Validaciones de datos de obra (Cobertura parcial)
- [ ] Accesibilidad y automatización UI (No implementado)
- [x] Métodos de negocio (crear, editar, eliminar obra) (Parcialmente cubiertos)
- [ ] Integración con módulos de Presupuestos, Inventario (No cubierto)
- [x] Estructura y documentación de tests (Aceptable)


### Tests faltantes y ejemplos
- Pruebas de integración con Presupuestos e Inventario
	- Ejemplo: Crear una obra y verificar su impacto en Presupuestos e Inventario.
- Casos límite de datos de obra
	- Ejemplo: Crear obra con datos incompletos o inválidos y verificar validaciones.
- Feedback visual y validaciones negativas
	- Ejemplo: Simular error al guardar obra y verificar mensaje en la UI.
- Flujos de usuario completos en UI
	- Ejemplo: Crear y editar obra desde la UI, validando feedback visual.

---

---


## 4. Compras
### Checklist
- [ ] Tests de vista principal y formularios (No cubiertos)
- [ ] Flujos de usuario (alta, modificación, cancelación) (No cubiertos)
- [ ] Validaciones de datos de compra (No cubiertos)
- [ ] Accesibilidad y automatización UI (No implementado)
- [ ] Métodos de negocio (registrar, modificar, eliminar compra) (No cubiertos)
- [ ] Integración con Inventario y Proveedores (No cubierto)
- [ ] Estructura y documentación de tests (Mejorable)


### Tests faltantes y ejemplos
- Pruebas de integración con Inventario y Proveedores
	- Ejemplo: Registrar compra y verificar actualización de stock e interacción con proveedores.
- Casos límite y errores de validación
	- Ejemplo: Intentar registrar compra con datos inválidos y verificar error.
- Feedback visual y mensajes de error
	- Ejemplo: Simular error de compra y verificar mensaje en la UI.
- Flujos de usuario completos en UI
	- Ejemplo: Alta y modificación de compra desde la UI, validando feedback visual.

---

---


## 5. Pedidos
### Checklist
- [ ] Tests de vista principal y formularios (No cubiertos)
- [ ] Flujos de usuario (crear, modificar, cancelar pedido) (No cubiertos)
- [ ] Validaciones de datos de pedido (No cubiertos)
- [ ] Accesibilidad y automatización UI (No implementado)
- [ ] Métodos de negocio (gestión de pedidos) (No cubiertos)
- [ ] Integración con Inventario, Obras, Notificaciones (No cubierto)
- [ ] Estructura y documentación de tests (Mejorable)


### Tests faltantes y ejemplos
- Pruebas de integración con Inventario y Obras
	- Ejemplo: Crear pedido y verificar su impacto en Inventario y Obras.
- Casos límite de gestión de pedidos
	- Ejemplo: Cancelar pedido en estado no permitido y verificar error.
- Feedback visual y validaciones negativas
	- Ejemplo: Simular error al crear/modificar pedido y verificar mensaje en la UI.
- Flujos de usuario completos en UI
	- Ejemplo: Crear, modificar y cancelar pedido desde la UI, validando feedback visual.

---

---


## 6. Vidrios
### Checklist
- [ ] Tests de vista y formularios de gestión de vidrios (No cubiertos)
- [ ] Flujos de usuario y feedback visual (No cubiertos)
- [ ] Validaciones de datos de vidrio (No cubiertos)
- [ ] Accesibilidad y automatización UI (No implementado)
- [ ] Métodos de negocio (alta, baja, modificación) (No cubiertos)
- [ ] Integración con Compras y Pedidos (No cubierto)
- [ ] Estructura y documentación de tests (Mejorable)


### Tests faltantes y ejemplos
- Pruebas de integración con Compras y Pedidos
	- Ejemplo: Registrar vidrio en una compra y verificar su disponibilidad en Pedidos.
- Casos límite y errores de validación
	- Ejemplo: Intentar registrar vidrio con datos inválidos y verificar error.
- Feedback visual y mensajes de error
	- Ejemplo: Simular error de gestión de vidrio y verificar mensaje en la UI.
- Flujos de usuario completos en UI
	- Ejemplo: Alta y modificación de vidrio desde la UI, validando feedback visual.

---

---


## 7. Notificaciones
### Checklist
- [ ] Tests de vista y componentes de notificaciones (No cubiertos)
- [ ] Flujos de usuario (recepción, lectura, eliminación) (No cubiertos)
- [ ] Validaciones de datos de notificación (No cubiertos)
- [ ] Accesibilidad y automatización UI (No implementado)
- [ ] Métodos de negocio (enviar, recibir, eliminar notificación) (No cubiertos)
- [ ] Integración con todos los módulos emisores (No cubierto)
- [ ] Estructura y documentación de tests (Mejorable)


### Tests faltantes y ejemplos
- Pruebas de integración con módulos emisores (Pedidos, Obras, etc.)
	- Ejemplo: Generar notificación desde Pedido y verificar recepción y visualización.
- Casos límite de envío y recepción
	- Ejemplo: Enviar notificación a usuario inexistente y verificar manejo de error.
- Feedback visual y validaciones negativas
	- Ejemplo: Simular error al eliminar notificación y verificar mensaje en la UI.
- Flujos de usuario completos en UI
	- Ejemplo: Recibir, leer y eliminar notificación desde la UI, validando feedback visual.

---

---

**Este documento debe actualizarse tras cada ciclo de desarrollo y testing.**

---

## 9. Reportes (Inventario y Generales)
### Checklist
- [ ] Tests de generación de reportes de stock
- [ ] Tests de reportes de movimientos
- [ ] Tests de dashboard de KPIs
- [ ] Tests de análisis ABC y valoración
- [ ] Tests de exportación (DICT, JSON, CSV)
- [ ] Tests de casos límite (filtros, datos vacíos, errores de conexión)
- [ ] Tests de integración (impacto de operaciones en reportes)
- [ ] Estructura y documentación de tests

### Tests faltantes y ejemplos
- Test de generación de reporte de stock con filtros y validación de estructura
- Test de error de conexión y manejo de excepción en reportes
- Test de exportación a CSV y JSON y validación de formato
- Test de integración: registrar un movimiento y verificar su reflejo en el reporte de stock
- Test de generación de dashboard de KPIs y validación de métricas clave

**Recomendación:** Crear un archivo de test específico para reportes de inventario (`test_inventario_reportes.py` o similar) y cubrir todos los flujos críticos de generación, exportación e integración de reportes.
