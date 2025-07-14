# Checklist de Uso de Utilidades SQL Seguras

Este checklist guía la implementación y uso de las utilidades SQL seguras en diferentes partes de la aplicación.

## Requisitos Previos

- [ ] Revisar la documentación de utilidades de seguridad
- [ ] Instalar todas las dependencias necesarias
- [ ] Verificar que `utils/sql_seguro.py` y `utils/sanitizador_sql.py` estén disponibles
- [ ] Ejecutar las pruebas unitarias para verificar funcionamiento correcto

## Implementación por Módulo

### Módulo de Usuarios (modules/usuarios)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por `construir_select_seguro`
  - [ ] Implementar `validar_nombre_tabla` para 'users'
  - [ ] Parametrizar consultas de autenticación
  - [ ] Sanitizar entrada de usuario en búsquedas

- [ ] Archivo: `controller.py`
  - [ ] Implementar `FormValidator` para validación
  - [ ] Sanitizar datos de perfil con `sanitizar_html`
  - [ ] Validar y sanitizar correos electrónicos

### Módulo de Obras (modules/obras)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Validar nombres de columnas en ordenamientos
  - [ ] Parametrizar búsquedas y filtros
  - [ ] Implementar `validar_nombre_tabla` para 'obras'

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de obras con `FormValidator`
  - [ ] Sanitizar campos de descripción
  - [ ] Validar códigos y datos numéricos

### Módulo de Inventario (modules/inventario)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Parametrizar consultas de búsqueda
  - [ ] Implementar `validar_nombre_tabla` para 'Inventario'
  - [ ] Asegurar que DELETE siempre tenga WHERE

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de inventario con `FormValidator`
  - [ ] Sanitizar campos de descripción
  - [ ] Validar códigos de producto

### Módulo de Herrajes (modules/herrajes)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Parametrizar consultas de búsqueda
  - [ ] Implementar validación de columnas para ordenamiento
  - [ ] Sanitizar parámetros de filtros

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de entrada con `FormValidator`
  - [ ] Sanitizar descripciones con `sanitizar_html`
  - [ ] Validar precios y cantidades

### Módulo de Vidrios (modules/vidrios)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Validar nombres de tablas y columnas
  - [ ] Parametrizar búsquedas por especificaciones
  - [ ] Sanitizar parámetros de dimensiones

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de vidrios con `FormValidator`
  - [ ] Sanitizar descripciones de producto
  - [ ] Validar medidas y cantidades

### Módulo de Pedidos (modules/pedidos)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Parametrizar consultas de búsqueda por fechas
  - [ ] Validar nombres de tablas relacionadas
  - [ ] Asegurar que UPDATE siempre tenga WHERE

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de pedidos con `FormValidator`
  - [ ] Sanitizar notas y comentarios
  - [ ] Validar fechas y datos numéricos

## Configuraciones y Actualizaciones

- [ ] Actualizar `TABLAS_PERMITIDAS` con nuevas tablas cuando se creen
- [ ] Actualizar `COLUMNAS_PERMITIDAS` cuando se modifique el esquema
- [ ] Documentar excepciones a la validación estricta (si aplica)
- [ ] Revisar y actualizar pruebas unitarias tras cambios

## Pruebas de Seguridad

- [ ] Ejecutar `analizar_seguridad_sql_codigo.py` después de cambios importantes
- [ ] Verificar que no haya construcción dinámica de SQL
- [ ] Probar casos límite con datos especiales (comillas, caracteres UTF-8, etc.)
- [ ] Verificar que los errores de seguridad se registren correctamente

## Revisión de Código

- [ ] Confirmar que no hay consultas SQL construidas con concatenación
- [ ] Verificar uso correcto de parámetros en consultas
- [ ] Asegurar que no hay SQL en línea hardcodeado
- [ ] Revisar el manejo de errores de seguridad

## Consideraciones Especiales

- [ ] Consultas complejas (JOIN múltiples)
  - [ ] Documentar por qué no se usan los constructores si aplica
  - [ ] Asegurar que los parámetros se pasan correctamente

- [ ] Reportes y consultas analíticas
  - [ ] Validar nombres de columnas en cláusulas ORDER BY y GROUP BY
  - [ ] Parametrizar filtros en consultas de reporte

- [ ] Procedimientos almacenados
  - [ ] Validar parámetros antes de llamar a SP
  - [ ] Sanitizar resultados si es necesario

---

## Registro de Implementación

| Fecha | Módulo | Archivos Modificados | Responsable | Observaciones |
|-------|--------|----------------------|------------|---------------|
|       |        |                      |            |               |
|       |        |                      |            |               |

## Versión del Checklist: 1.0.0
Fecha de creación: 25 de junio de 2025
