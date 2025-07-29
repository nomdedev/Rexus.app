# Checklist de Correcciones Rexus.app

## Errores detectados en ejecución (29/07/2025)

### Inventario
- [ ] El controlador de inventario no tiene el método `filtrar_inventario`. La vista lo llama y genera `AttributeError`. 
- [ ] Verificar que todos los métodos requeridos por la vista estén implementados en el controlador.

### Herrajes
- [ ] Error: `'QCursor' object has no attribute 'execute'` al verificar tablas.
- [ ] Error: `'function' object has no attribute 'connect'` al crear el controlador.
- [ ] Revisar la inicialización del modelo y controlador, y el uso de cursores/conexiones.

### Obras
- [ ] Error SQL: faltan columnas en la tabla 'obras' (`codigo`, `responsable`, `fecha_inicio`, `fecha_fin_estimada`, `presupuesto_total`, `progreso`, `descripcion`, `ubicacion`, `created_at`, `updated_at`).
- [ ] Error obteniendo estadísticas: columna `presupuesto_total` no existe.
- [ ] Revisar y actualizar la estructura de la tabla en la base de datos.

### Logística
- [ ] Error importando mapa interactivo: `QtWebEngineWidgets must be imported or Qt.AA_ShareOpenGLContexts must be set before a QCoreApplication instance is created`.
- [ ] Método `cargar_logistica` no encontrado en el controlador.
- [ ] Error SQL: `Syntax error, permission violation, or other nonspecific error` al obtener entregas.
- [ ] Revisar inicialización de QtWebEngine y métodos del controlador.

### Vidrios
- [ ] Error: `'NoneType' object has no attribute 'cursor'` al verificar tablas y obtener datos.
- [ ] Revisar la conexión a la base de datos y la inicialización del modelo.

### Configuración
- [ ] Error: `'QCursor' object has no attribute 'execute'` al verificar tablas.
- [ ] Error creando configuración real: `'QCursor' object has no attribute 'execute'`.
- [ ] Revisar el uso de cursores y la lógica de acceso a la base de datos.

---

## Acciones sugeridas
- [ ] Implementar y testear todos los métodos requeridos por las vistas en los controladores.
- [ ] Revisar y corregir la estructura de las tablas en la base de datos.
- [ ] Validar la inicialización y uso de QtWebEngine en módulos con mapas.
- [ ] Corregir el uso de cursores y conexiones en los modelos/controladores.
- [ ] Documentar cada corrección aplicada en este checklist.

---

## Última actualización: 29/07/2025
