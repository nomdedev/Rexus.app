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
- [ ] Tests de inicialización de vista principal
- [ ] Tests de formularios y componentes visuales
- [ ] Flujos de usuario (llenado, envío, feedback visual)
- [ ] Mensajes de error y validaciones negativas
- [ ] Accesibilidad (contraste, teclado, focus)
- [ ] Automatización UI (pytest-qt, qtbot, Selenium)
- [ ] Métodos de negocio (guardar, cargar, validar)
- [ ] Validaciones, persistencia, manejo de errores
- [ ] Casos límite y entradas inválidas
- [ ] Seguridad y control de acceso
- [ ] Integración con otros módulos
- [ ] Flujos completos multi-módulo
- [ ] Errores de integración y recuperación
- [ ] Estructura de tests clara y modular
- [ ] Tests reflejan comportamiento real
- [ ] Documentación suficiente
- [ ] Feedback visual y notificaciones
- [ ] Persistencia de configuraciones
- [ ] Configuraciones avanzadas y restricciones

### Tests faltantes
- Flujos de usuario completos en UI
- Pruebas de accesibilidad profunda
- Integración con módulos dependientes (ej: Inventario, Usuarios)
- Validaciones negativas y feedback visual de errores

---

## 2. Inventario
### Checklist
- [ ] Tests de inicialización de vista principal
- [ ] Tests de formularios de alta, baja, modificación
- [ ] Flujos de usuario (input, submit, feedback)
- [ ] Validaciones de stock, errores y límites
- [ ] Accesibilidad y automatización UI
- [ ] Métodos de negocio (agregar, quitar, actualizar stock)
- [ ] Integración con Pedidos, Compras, Configuración
- [ ] Estructura y documentación de tests

### Tests faltantes
- Pruebas de integración con Pedidos y Compras
- Casos límite de stock y errores de concurrencia
- Feedback visual ante errores de inventario

---

## 3. Obras
### Checklist
- [ ] Tests de inicialización de vista y componentes
- [ ] Formularios de creación y edición de obra
- [ ] Flujos de usuario y feedback visual
- [ ] Validaciones de datos de obra
- [ ] Accesibilidad y automatización UI
- [ ] Métodos de negocio (crear, editar, eliminar obra)
- [ ] Integración con módulos de Presupuestos, Inventario
- [ ] Estructura y documentación de tests

### Tests faltantes
- Pruebas de integración con Presupuestos e Inventario
- Casos límite de datos de obra
- Feedback visual y validaciones negativas

---

## 4. Compras
### Checklist
- [ ] Tests de vista principal y formularios
- [ ] Flujos de usuario (alta, modificación, cancelación)
- [ ] Validaciones de datos de compra
- [ ] Accesibilidad y automatización UI
- [ ] Métodos de negocio (registrar, modificar, eliminar compra)
- [ ] Integración con Inventario y Proveedores
- [ ] Estructura y documentación de tests

### Tests faltantes
- Pruebas de integración con Inventario y Proveedores
- Casos límite y errores de validación
- Feedback visual y mensajes de error

---

## 5. Pedidos
### Checklist
- [ ] Tests de vista principal y formularios
- [ ] Flujos de usuario (crear, modificar, cancelar pedido)
- [ ] Validaciones de datos de pedido
- [ ] Accesibilidad y automatización UI
- [ ] Métodos de negocio (gestión de pedidos)
- [ ] Integración con Inventario, Obras, Notificaciones
- [ ] Estructura y documentación de tests

### Tests faltantes
- Pruebas de integración con Inventario y Obras
- Casos límite de gestión de pedidos
- Feedback visual y validaciones negativas

---

## 6. Vidrios
### Checklist
- [ ] Tests de vista y formularios de gestión de vidrios
- [ ] Flujos de usuario y feedback visual
- [ ] Validaciones de datos de vidrio
- [ ] Accesibilidad y automatización UI
- [ ] Métodos de negocio (alta, baja, modificación)
- [ ] Integración con Compras y Pedidos
- [ ] Estructura y documentación de tests

### Tests faltantes
- Pruebas de integración con Compras y Pedidos
- Casos límite y errores de validación
- Feedback visual y mensajes de error

---

## 7. Notificaciones
### Checklist
- [ ] Tests de vista y componentes de notificaciones
- [ ] Flujos de usuario (recepción, lectura, eliminación)
- [ ] Validaciones de datos de notificación
- [ ] Accesibilidad y automatización UI
- [ ] Métodos de negocio (enviar, recibir, eliminar notificación)
- [ ] Integración con todos los módulos emisores
- [ ] Estructura y documentación de tests

### Tests faltantes
- Pruebas de integración con módulos emisores (Pedidos, Obras, etc.)
- Casos límite de envío y recepción
- Feedback visual y validaciones negativas

---

**Este documento debe actualizarse tras cada ciclo de desarrollo y testing.**
