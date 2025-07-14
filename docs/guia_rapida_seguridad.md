# Guía Rápida de Utilidades de Seguridad

## Introducción

Esta guía ofrece ejemplos prácticos para utilizar las herramientas de seguridad implementadas en el proyecto. Aprenderás a:

- Proteger tus consultas SQL contra inyección
- Validar datos de entrada en formularios
- Detectar y prevenir ataques XSS
- Analizar tu código en busca de vulnerabilidades

## Consultas SQL Seguras

### Consulta básica con validación

```python
from core.database import ObrasDatabaseConnection
from utils.sql_seguro import validar_nombre_tabla, construir_select_seguro

db = ObrasDatabaseConnection()

# Validar el nombre de tabla (protección contra inyección SQL)
tabla = "users"  # Nombre que debe estar en la lista blanca
tabla_validada = validar_nombre_tabla(tabla)

# Construir consulta segura
query, _ = construir_select_seguro(
    tabla=tabla_validada,
    columnas=["id", "nombre", "email"],
    where="activo = ?"
)

# Ejecutar con parámetros (previene inyección SQL)
usuarios = db.ejecutar_query(query, [True])
```

### Insertar datos de forma segura

```python
from utils.sql_seguro import construir_insert_seguro

def crear_cliente(nombre, email, telefono):
    # Construir consulta INSERT segura
    query, _ = construir_insert_seguro(
        tabla="clientes",
        columnas=["nombre", "email", "telefono", "fecha_creacion"]
    )

    # Ejecutar con parámetros
    from datetime import datetime
    return db.ejecutar_query(
        query,
        [nombre, email, telefono, datetime.now()]
    )
```

### Actualizar datos de forma segura

```python
from utils.sql_seguro import construir_update_seguro

def actualizar_cliente(id_cliente, datos):
    # Determinar qué columnas actualizar (solo las proporcionadas)
    columnas = []
    valores = []

    for campo in ["nombre", "email", "telefono"]:
        if campo in datos:
            columnas.append(campo)
            valores.append(datos[campo])

    # Construir consulta UPDATE segura
    if columnas:
        query, _ = construir_update_seguro(
            tabla="clientes",
            columnas=columnas,
            where="id = ?"
        )

        # Añadir ID al final para la cláusula WHERE
        valores.append(id_cliente)

        # Ejecutar con parámetros
        return db.ejecutar_query(query, valores)

    return False
```

### Eliminar datos de forma segura

```python
from utils.sql_seguro import construir_delete_seguro

def eliminar_cliente(id_cliente):
    try:
        # Construir consulta DELETE segura (siempre requiere WHERE)
        query, _ = construir_delete_seguro(
            tabla="clientes",
            where="id = ?"
        )

        # Ejecutar con parámetros
        return db.ejecutar_query(query, [id_cliente])
    except SecurityError as e:
        # La función lanzará excepciones si intenta un DELETE sin WHERE
        logger.error(f"Error de seguridad: {e}")
        return False
```

## Validación de Datos de Formularios

### Validar un formulario completo

```python
from utils.validador_http import FormValidator

def procesar_formulario_usuario(datos_form):
    # Crear validator
    validator = FormValidator()

    # Definir reglas de validación
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
        'telefono': [
            {'funcion': 'validar_patron', 'params': {'tipo': 'telefono'}}
        ],
        'edad': [
            {'funcion': 'validar_rango_numerico', 'params': {'minimo': 18, 'maximo': 99, 'tipo': 'int'}}
        ]
    }

    # Validar formulario
    if validator.validar_formulario(datos_form, reglas):
        # Los datos son válidos
        datos_limpios = validator.obtener_datos_limpios()
        return True, datos_limpios
    else:
        # Hay errores de validación
        return False, validator.obtener_errores()
```

### Prevenir ataques XSS

```python
from utils.validador_http import detectar_xss, sanitizar_html

def guardar_comentario(usuario_id, texto_comentario):
    try:
        # Detectar posibles ataques XSS
        detectar_xss(texto_comentario)

        # Sanitizar HTML (segunda defensa)
        comentario_seguro = sanitizar_html(texto_comentario)

        # Guardar el comentario sanitizado
        query, _ = construir_insert_seguro('comentarios', ['usuario_id', 'texto', 'fecha'])
        return db.ejecutar_query(query, [usuario_id, comentario_seguro, datetime.now()])

    except SecurityError as e:
        # Registrar intento de XSS
        logger.security_warning(f"Posible ataque XSS: {e}")
        return False
```

### Sanitizar URLs

```python
from utils.validador_http import sanitizar_url

def redireccionar_usuario(url_destino):
    try:
        # Sanitizar URL para prevenir redirecciones maliciosas
        url_segura = sanitizar_url(url_destino)

        # Solo permitir URLs dentro del dominio o rutas relativas
        if url_segura.startswith('https://nuestrodominio.com') or url_segura.startswith('/'):
            return redirect(url_segura)
        else:
            return redirect('/pagina_segura')

    except SecurityError:
        # URL potencialmente peligrosa
        return redirect('/pagina_segura')
```

## Análisis de Seguridad

### Analizar seguridad SQL en archivos

```bash
# Analizar un módulo específico
python scripts/verificacion/analizar_seguridad_sql_codigo.py --dir ./modules/usuarios

# Analizar toda la aplicación y guardar informe
python scripts/verificacion/analizar_seguridad_sql_codigo.py --dir . --output informes/seguridad_sql.html

# Excluir directorios específicos
python scripts/verificacion/analizar_seguridad_sql_codigo.py --dir . --exclude venv --exclude tests
```

### Escaneo completo de vulnerabilidades

```bash
# Escaneo completo
python scripts/verificacion/escanear_vulnerabilidades.py

# Escaneo específico (omitir análisis de base de datos)
python scripts/verificacion/escanear_vulnerabilidades.py --skip-bd

# Especificar directorio de salida para informes
python scripts/verificacion/escanear_vulnerabilidades.py --output ./informes_seguridad
```

## Integración en el Flujo de Desarrollo

### Pre-commit

Agrega estos comandos a tus script de pre-commit para verificar seguridad antes de cada commit:

```bash
# Verificar seguridad SQL en los archivos modificados
python scripts/verificacion/analizar_seguridad_sql_codigo.py --dir .

# Si falla, detener el commit
if [ $? -ne 0 ]; then
  echo "Se encontraron problemas de seguridad SQL. Por favor corrígelos antes de realizar el commit."
  exit 1
fi
```

### Integración Continua

Incluye estos pasos en tu pipeline de CI:

```yaml
# Ejemplo para GitHub Actions
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Analizar seguridad SQL
        run: python scripts/verificacion/analizar_seguridad_sql_codigo.py --dir .
      - name: Escaneo de vulnerabilidades
        run: python scripts/verificacion/escanear_vulnerabilidades.py --skip-bd
      - name: Archive security reports
        uses: actions/upload-artifact@v2
        with:
          name: security-reports
          path: informes_seguridad/
```

## Referencias Rápidas

### Patrones de Validación Disponibles

- **email**: Dirección de correo electrónico
- **nombre**: Nombres de persona (con acentos y espacios)
- **telefono**: Números de teléfono en varios formatos
- **codigo_postal**: Códigos postales (5 dígitos)
- **fecha**: Formato YYYY-MM-DD
- **url**: URLs HTTP/HTTPS
- **alfanumerico**: Solo letras y números
- **entero**: Números enteros
- **decimal**: Números decimales
- **dni**: DNI español
- **nif**: NIF español

### Funciones de Sanitización Comunes

- `sanitizar_html(valor)`: Escapa HTML para prevenir XSS
- `sanitizar_url(url)`: Sanitiza URLs para prevenir redirecciones maliciosas
- `sanitizar_json(datos_json)`: Sanitiza datos JSON anidados
- `escapar_string_sql(texto)`: Escapa strings para SQL
- `sanitizar_numerico(valor, tipo)`: Sanitiza valores numéricos
- `sanitizar_fecha_sql(fecha)`: Sanitiza fechas para SQL
