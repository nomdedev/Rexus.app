# Checklist de Validación y Sanitización de Datos de Entrada

Este checklist guía la implementación de validaciones de datos de entrada para prevenir XSS, inyección y otros ataques.

## Requisitos Previos

- [ ] Revisar la documentación de `utils/validador_http.py`
- [ ] Conocer los tipos de datos esperados en cada campo
- [ ] Identificar campos de alto riesgo (campos libres, URLs, código)
- [ ] Ejecutar pruebas unitarias para verificar utilidades de validación

## Implementación por Tipo de Formulario

### Formularios de Autenticación

- [ ] Formulario de Login
  - [ ] Validar longitud de nombre de usuario/email
  - [ ] Detectar patrones XSS en campos
  - [ ] Proteger contra inyección SQL
  - [ ] Limitar intentos de login fallidos

- [ ] Formulario de Registro de Usuario
  - [ ] Validar formato de email
  - [ ] Validar complejidad de contraseña
  - [ ] Sanitizar nombre y apellido
  - [ ] Validar unicidad de nombre de usuario/email

- [ ] Restablecimiento de Contraseña
  - [ ] Validar tokens de restablecimiento
  - [ ] Sanitizar entradas
  - [ ] Validar complejidad de nueva contraseña

### Formularios de Datos Maestros

- [ ] Clientes
  - [ ] Validar formato de email
  - [ ] Validar formato de teléfono
  - [ ] Sanitizar nombre y dirección
  - [ ] Validar código postal

- [ ] Proveedores
  - [ ] Validar formato de email
  - [ ] Validar formato de teléfono
  - [ ] Sanitizar nombres y descripciones
  - [ ] Validar formato de NIF/CIF

- [ ] Productos/Inventario
  - [ ] Validar códigos de producto
  - [ ] Sanitizar descripciones
  - [ ] Validar precios (rango, formato)
  - [ ] Validar existencias y cantidades mínimas

### Formularios de Transacciones

- [ ] Pedidos
  - [ ] Validar cantidades y precios
  - [ ] Sanitizar notas y comentarios
  - [ ] Validar fechas (entrega, producción)
  - [ ] Validar relaciones (cliente, productos)

- [ ] Obras
  - [ ] Validar información de contacto
  - [ ] Sanitizar direcciones y notas
  - [ ] Validar fechas de inicio/fin
  - [ ] Validar presupuestos y costos

- [ ] Pagos
  - [ ] Validar importes
  - [ ] Sanitizar conceptos y referencias
  - [ ] Validar fechas
  - [ ] Validar métodos de pago

### Formularios de Configuración

- [ ] Configuración de Sistema
  - [ ] Validar estrictamente todos los campos
  - [ ] Detectar patrones XSS en valores
  - [ ] Sanitizar todos los textos
  - [ ] Validar URLs y rutas

- [ ] Perfiles de Usuario
  - [ ] Sanitizar campos de perfil
  - [ ] Validar imágenes (tamaño, tipo)
  - [ ] Detectar patrones XSS en biografías
  - [ ] Validar preferencias y configuraciones

## Implementación de Validaciones por Tipo de Dato

### Texto

- [ ] Campos de texto corto
  - [ ] Validar longitud mínima y máxima
  - [ ] Sanitizar HTML si se muestra en UI
  - [ ] Validar patrones específicos si aplica

- [ ] Campos de texto largo
  - [ ] Detectar patrones XSS
  - [ ] Sanitizar HTML completamente
  - [ ] Limitar longitud máxima
  - [ ] Validar formato si aplica (Markdown, etc.)

### Números

- [ ] Enteros
  - [ ] Validar rango permitido
  - [ ] Validar tipo (entero vs decimal)
  - [ ] Sanitizar entrada antes de conversión

- [ ] Decimales
  - [ ] Validar precisión y escala
  - [ ] Validar rango permitido
  - [ ] Sanitizar formato según localización
  - [ ] Validar tipo de dato

### Fechas y Horas

- [ ] Fechas
  - [ ] Validar formato (YYYY-MM-DD)
  - [ ] Validar rango permitido
  - [ ] Validar lógica de negocio (ej: fecha futura/pasada)

- [ ] Horas
  - [ ] Validar formato (HH:MM:SS)
  - [ ] Validar rango permitido
  - [ ] Validar lógica horaria específica

- [ ] Rangos de Fechas
  - [ ] Validar que fecha inicial < fecha final
  - [ ] Validar límites máximos de rango
  - [ ] Sanitizar formatos antes de uso

### Datos Especiales

- [ ] Correos electrónicos
  - [ ] Validar formato según RFC
  - [ ] Validar dominio (opcional)
  - [ ] Sanitizar antes de almacenar

- [ ] URLs
  - [ ] Validar formato
  - [ ] Sanitizar para prevenir ataques de redirección
  - [ ] Validar esquema (http, https)
  - [ ] Validar dominios permitidos si aplica

- [ ] Teléfonos
  - [ ] Validar formato según país
  - [ ] Sanitizar caracteres no numéricos
  - [ ] Validar longitud según formato

- [ ] Documentos de identidad
  - [ ] Validar formato (DNI, NIF, otros)
  - [ ] Validar dígito de control si aplica
  - [ ] Sanitizar formato (espacios, guiones)

## Implementación Técnica

- [ ] Implementar `FormValidator` en todos los controladores
  - [ ] Crear reglas de validación para cada formulario
  - [ ] Definir campos requeridos adecuadamente
  - [ ] Utilizar funciones de validación existentes
  - [ ] Crear funciones de validación personalizadas si es necesario

- [ ] Sanitización
  - [ ] Sanitizar HTML en datos de texto libre
  - [ ] Sanitizar URLs en enlaces
  - [ ] Sanitizar datos JSON en APIs

- [ ] Manejo de Errores
  - [ ] Mostrar errores específicos por campo
  - [ ] Mantener valores válidos al reportar errores
  - [ ] Registrar intentos sospechosos (posibles ataques)
  - [ ] Implementar throttling en APIs y formularios

## Pruebas de Validación

- [ ] Crear casos de prueba con datos válidos
- [ ] Crear casos de prueba con datos inválidos
- [ ] Probar ataques XSS comunes
- [ ] Probar inyección SQL a través de formularios
- [ ] Probar valores límite y casos borde
- [ ] Probar caracteres especiales y codificaciones

## Revisión y Mantenimiento

- [ ] Revisar validaciones después de cambios en modelos de datos
- [ ] Actualizar patrones de validación cuando sea necesario
- [ ] Documentar reglas de validación específicas del negocio
- [ ] Revisar regularmente logs de errores de validación

---

## Registro de Implementación

| Fecha | Formulario | Validaciones Implementadas | Responsable | Observaciones |
|-------|------------|---------------------------|------------|---------------|
|       |            |                           |            |               |
|       |            |                           |            |               |

## Versión del Checklist: 1.0.0
Fecha de creación: 25 de junio de 2025
