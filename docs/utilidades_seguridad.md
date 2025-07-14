# Documentación de Utilidades de Seguridad

## Introducción

Este documento describe las nuevas utilidades de seguridad implementadas para mejorar la protección contra vulnerabilidades comunes en la aplicación. Estas herramientas proporcionan mecanismos para prevenir inyección SQL, ataques XSS, fuga de información sensible y otros problemas de seguridad.

## Índice

1. [Utilidades SQL Seguro](#1-utilidades-sql-seguro)
2. [Sanitizador SQL](#2-sanitizador-sql)
3. [Validador HTTP](#3-validador-http)
4. [Herramientas de Análisis](#4-herramientas-de-análisis)
5. [Integración con el Sistema](#5-integración-con-el-sistema)
6. [Buenas Prácticas](#6-buenas-prácticas)
7. [Referencias](#7-referencias)

---

## 1. Utilidades SQL Seguro

### Descripción

El módulo `utils.sql_seguro` proporciona funciones para trabajar de manera segura con SQL, validando nombres de tablas y columnas contra listas blancas y construyendo consultas parametrizadas.

### Componentes Principales

#### Listas Blancas

- `TABLAS_PERMITIDAS`: Conjunto de nombres de tablas permitidos en el sistema.
- `COLUMNAS_PERMITIDAS`: Diccionario con columnas permitidas por cada tabla.

#### Funciones de Validación

- `validar_nombre_tabla(tabla)`: Valida que el nombre de tabla pertenezca a la lista blanca.
- `validar_nombre_columna(tabla, columna)`: Valida que el nombre de columna esté en la lista blanca para la tabla.
- `validar_nombres_columnas(tabla, columnas)`: Valida una lista de nombres de columnas.

#### Constructores de Consultas

- `construir_select_seguro(tabla, columnas=None, where=None)`: Crea consultas SELECT seguras.
- `construir_update_seguro(tabla, columnas, where=None)`: Crea consultas UPDATE seguras.
- `construir_insert_seguro(tabla, columnas)`: Crea consultas INSERT seguras.
- `construir_delete_seguro(tabla, where=None)`: Crea consultas DELETE seguras (requiere siempre WHERE).

### Ejemplo de Uso

```python
from utils.sql_seguro import construir_select_seguro

# Consulta segura para buscar usuarios por email
query, _ = construir_select_seguro(
    tabla='users',
    columnas=['id', 'nombre', 'email'],
    where='email = ?'
)

# Uso con conexión
resultado = db.ejecutar_query(query, ['usuario@example.com'])
```

---

## 2. Sanitizador SQL

### Descripción

El módulo `utils.sanitizador_sql` complementa a `sql_seguro` con funciones adicionales para sanitizar parámetros SQL y detectar patrones peligrosos en las consultas.

### Componentes Principales

#### Patrones Peligrosos

- `PATRONES_PELIGROSOS`: Lista de expresiones regulares que identifican patrones SQL potencialmente peligrosos.

#### Funciones de Sanitización

- `escapar_string_sql(texto)`: Escapa un string para uso seguro en SQL.
- `sanitizar_numerico(valor, tipo='int')`: Sanitiza un valor numérico.
- `sanitizar_fecha_sql(fecha)`: Sanitiza una fecha para SQL.
- `sanitizar_datetime_sql(fecha_hora)`: Sanitiza un datetime para SQL.
- `sanitizar_bool_sql(valor)`: Sanitiza un valor booleano para SQL.
- `sanitizar_lista_valores(valores, tipo='str')`: Sanitiza una lista de valores para uso en cláusula IN().

#### Funciones de Validación

- `validar_consulta_sql(consulta)`: Valida una consulta SQL para detectar patrones peligrosos.
- `detectar_vulnerabilidades_consulta(consulta)`: Detecta vulnerabilidades sin lanzar excepciones.
- `parametrizar_consulta(base_consulta, parametros)`: Prepara consultas parametrizadas.

### Ejemplo de Uso

```python
from utils.sanitizador_sql import sanitizar_numerico, escapar_string_sql

# Sanitizar valores antes de usar en consultas
id_seguro = sanitizar_numerico(id_usuario, 'int')
nombre_seguro = escapar_string_sql(nombre_usuario)

# Verificar si una consulta es segura
try:
    validar_consulta_sql("SELECT * FROM users WHERE username = 'admin' OR 1=1")
except SecurityError as e:
    print(f"Consulta insegura: {e}")
```

---

## 3. Validador HTTP

### Descripción

El módulo `utils.validador_http` proporciona funciones para validar y sanitizar datos de entrada en formularios y peticiones HTTP, ayudando a prevenir ataques XSS y otras vulnerabilidades.

### Componentes Principales

#### Patrones de Validación

- `PATRONES`: Diccionario con expresiones regulares para validar formatos comunes (email, teléfono, etc.)
- `PATRONES_XSS`: Lista de patrones que identifican posibles ataques XSS.

#### Funciones de Validación

- `validar_patron(valor, tipo)`: Valida que un valor cumpla con un patrón predefinido.
- `validar_longitud(valor, min_len=None, max_len=None)`: Valida la longitud de un valor.
- `validar_rango_numerico(valor, minimo=None, maximo=None)`: Valida que un número esté en un rango.
- `validar_fecha(valor, formato='%Y-%m-%d', min_fecha=None, max_fecha=None)`: Valida fechas.
- `validar_opciones(valor, opciones_permitidas)`: Valida que un valor esté entre opciones permitidas.
- `detectar_xss(valor)`: Detecta posibles ataques XSS en una cadena.

#### Funciones de Sanitización

- `sanitizar_html(valor)`: Escapa caracteres HTML para prevenir XSS.
- `sanitizar_url(url)`: Sanitiza una URL para prevenir ataques de redirección.
- `sanitizar_json(datos_json)`: Sanitiza datos JSON para prevenir inyecciones.

#### Validador de Formularios

La clase `FormValidator` permite validar formularios completos con múltiples campos y reglas.

### Ejemplo de Uso

```python
from utils.validador_http import FormValidator

# Crear validador
validator = FormValidator()

# Definir reglas
reglas = {
    'nombre': [
        {'requerido': True},
        {'funcion': 'validar_longitud', 'params': {'min_len': 2, 'max_len': 50}},
        {'funcion': 'validar_patron', 'params': {'tipo': 'nombre'}}
    ],
    'email': [
        {'requerido': True},
        {'funcion': 'validar_patron', 'params': {'tipo': 'email'}}
    ],
    'edad': [
        {'funcion': 'validar_rango_numerico', 'params': {'minimo': 18, 'maximo': 120, 'tipo': 'int'}}
    ]
}

# Validar formulario
datos = request.form # ejemplo con Flask
if validator.validar_formulario(datos, reglas):
    # Procesamiento con datos válidos
    datos_limpios = validator.obtener_datos_limpios()
else:
    # Manejo de errores
    errores = validator.obtener_errores()
```

---

## 4. Herramientas de Análisis

### Descripción

Se han implementado herramientas para analizar la seguridad del código y la base de datos, detectando vulnerabilidades y generando informes.

### Componentes Principales

#### Analizador de Código SQL

El script `scripts/verificacion/analizar_seguridad_sql_codigo.py` busca patrones inseguros de SQL en el código fuente.

Características:
- Detección de consultas SQL construidas inseguramente (concatenación, f-strings)
- Detección de patrones vulnerables a inyección SQL
- Generación de informes HTML y JSON
- Recomendaciones para mejorar seguridad

#### Escáner de Vulnerabilidades

El script `scripts/verificacion/escanear_vulnerabilidades.py` ejecuta análisis completos:

Características:
- Escaneo de vulnerabilidades SQL en el código
- Diagnóstico de seguridad de la BD
- Verificación de archivos con información sensible
- Análisis de dependencias con problemas de seguridad

### Uso de las Herramientas

```bash
# Análisis de código SQL
python scripts/verificacion/analizar_seguridad_sql_codigo.py --dir ./modules --output informes/seguridad_sql.html

# Escaneo completo de vulnerabilidades
python scripts/verificacion/escanear_vulnerabilidades.py --output informes_seguridad
```

---

## 5. Integración con el Sistema

### Integración con Módulos Existentes

Las nuevas utilidades se integran con los módulos existentes:

1. **Database**: Usar los constructores de consultas seguras en vez de construir SQL directamente
   ```python
   from utils.sql_seguro import construir_select_seguro

   def obtener_usuario(id):
       query, _ = construir_select_seguro('users', ['id', 'nombre', 'email'], 'id = ?')
       return self.ejecutar_query(query, [id])
   ```

2. **Controladores**: Utilizar el validador de formularios
   ```python
   from utils.validador_http import FormValidator

   def guardar_usuario(self, datos_form):
       validator = FormValidator()
       reglas = {...}  # Definir reglas

       if validator.validar_formulario(datos_form, reglas):
           datos_limpios = validator.obtener_datos_limpios()
           # Procesar datos validados
       else:
           return {'error': validator.obtener_errores()}
   ```

3. **Análisis de Seguridad**: Incorporar al flujo de CI/CD
   ```bash
   # Integrar en scripts de pre-commit o CI/CD
   python scripts/verificacion/escanear_vulnerabilidades.py --skip-bd
   ```

### Excepciones de Seguridad

Es importante manejar adecuadamente las excepciones de seguridad:

```python
try:
    # Código que usa utilidades de seguridad
    validar_consulta_sql(consulta)
except SecurityError as e:
    # Registrar incidente de seguridad
    logger.security_warning(f"Intento de consulta insegura: {e}")
    # Devolver error genérico al usuario
    return {'error': 'Error de seguridad, contacte al administrador'}
except InputValidationError as e:
    # Error de validación (no necesariamente un ataque)
    return {'error': str(e)}
```

---

## 6. Buenas Prácticas

### Consultas SQL Seguras

1. **Siempre usar consultas parametrizadas** - Nunca concatenar directamente valores en SQL
   ```python
   # MAL
   query = f"SELECT * FROM users WHERE username = '{username}'"

   # BIEN
   query = "SELECT * FROM users WHERE username = ?"
   db.ejecutar_query(query, [username])
   ```

2. **Validar nombres de tablas y columnas** - Usar siempre las funciones de validación
   ```python
   # BIEN
   tabla = validar_nombre_tabla(nombre_tabla)
   columnas = validar_nombres_columnas(tabla, lista_columnas)
   ```

3. **Usar constructores de consulta** - Preferir los constructores de sql_seguro.py
   ```python
   query, _ = construir_select_seguro('users', ['id', 'nombre'], 'activo = ?')
   ```

### Prevención de XSS

1. **Sanitizar siempre datos de entrada** - Especialmente en formularios y APIs
   ```python
   datos_limpios = sanitizar_html(datos_usuario)
   ```

2. **Validar siempre antes de procesar** - Usar el validador de formularios
   ```python
   if not validator.validar_formulario(datos, reglas):
       return {'error': validator.obtener_errores()}
   ```

3. **Validar URL y redirecciones** - Prevenir redirecciones maliciosas
   ```python
   url_destino = sanitizar_url(url_param)
   ```

### Análisis de Seguridad

1. **Ejecutar análisis regularmente** - Programar escaneos periódicos

2. **Revisar y corregir vulnerabilidades** - Priorizar según gravedad

3. **Documentar excepciones y decisiones** - Si se decide ignorar una alerta, documentar el motivo

---

## 7. Referencias

- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-79: Cross-site Scripting](https://cwe.mitre.org/data/definitions/79.html)
- [Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

---

## Anexo: Lista de Archivos Nuevos

1. `utils/sanitizador_sql.py` - Funciones para sanitizar y validar consultas SQL
2. `utils/validador_http.py` - Validador para datos de formularios y peticiones HTTP
3. `scripts/verificacion/analizar_seguridad_sql_codigo.py` - Analizador de código SQL
4. `scripts/verificacion/escanear_vulnerabilidades.py` - Escáner completo de vulnerabilidades
5. `tests/utils/test_sql_utils.py` - Tests para utils.sql_seguro y utils.sanitizador_sql
6. `tests/utils/test_validador_http.py` - Tests para utils.validador_http
