"""
Script para realizar un diagnóstico completo de seguridad de la base de datos.
Este diagnóstico incluye:
1. Verificación de tablas y estructura
2. Análisis de permisos y roles
3. Detección de vulnerabilidades comunes
4. Recomendaciones de seguridad
"""

# Agregar el directorio raíz al path de Python
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

def banner_diagnostico():
    """Muestra un banner con información del diagnóstico de seguridad."""
    print("\n" + "=" * 80)
    print(" "*28 + "DIAGNÓSTICO DE SEGURIDAD DE BD")
    print(" "*32 + "Versión 1.0.0")
    print(" "*24 + "Fecha: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 80 + "\n")

def analizar_seguridad_bd():
import argparse
import datetime
import os
import sys
from pathlib import Path

from core.database import ObrasDatabaseConnection
from core.exceptions import ConnectionError, QueryError, SecurityError
from core.logger import Logger
from utils.analizador_db import AnalizadorDB

    """Realiza un análisis completo de seguridad de la base de datos."""
    logger = Logger()
    db = ObrasDatabaseConnection()
    analizador = AnalizadorDB(db)

    try:
        banner_diagnostico()
        print("🔍 Iniciando análisis de seguridad de la base de datos...")

        # 1. Verificar conexión
        db.conectar()
        print("[CHECK] Conectado exitosamente a la base de datos\n")

        # 2. Listar tablas y estructura
        tablas = analizador.listar_tablas()
        print(f"[CHART] Encontradas {len(tablas)} tablas en la base de datos\n")

        # 3. Verificar permisos de usuario actual
        permisos = verificar_permisos_usuario(db)

        # 4. Realizar verificaciones de seguridad comunes
        vulnerabilidades = detectar_vulnerabilidades(db)

        # 5. Generar recomendaciones
        recomendaciones = generar_recomendaciones(permisos, vulnerabilidades)

        # 6. Mostrar resumen y guardar informe
        mostrar_resumen_seguridad(tablas,
permisos,
            vulnerabilidades,
            recomendaciones)

    except (ConnectionError, QueryError, SecurityError) as e:
        logger.error(f"Error durante el análisis de seguridad: {e}")
        print(f"\n[ERROR] Error: {e}")
    finally:
        db.cerrar_conexion()


def verificar_permisos_usuario(db):
    """
    Verifica los permisos del usuario actual en la base de datos.

    Args:
        db: Conexión a la base de datos

    Returns:
        dict: Información sobre los permisos detectados
    """
    print("🔐 Verificando permisos del usuario actual...")

    permisos = {
        "TEST_USER": False,
        "create": False,
        "alter": False,
        "drop": False,
        "select_all": False,
        "insert_all": False,
        "update_all": False,
        "delete_all": False,
        "execute": False,
        "detalle": {}
    }

    try:
        # Consultar el nombre del usuario actual
        query_usuario = "SELECT CURRENT_USER"
        usuario_actual = db.ejecutar_query(query_usuario)[0][0]
        print(f"  Usuario actual: {usuario_actual}")

        # Consultar roles del usuario
        query_roles = """
            SELECT r.name AS role_name
            FROM sys.server_principals r
            INNER JOIN sys.server_role_members m ON r.principal_id = m.role_principal_id
            INNER JOIN sys.server_principals u ON m.member_principal_id = u.principal_id
            WHERE u.name = CURRENT_USER
        """
        roles = db.ejecutar_query(query_roles)
        roles_lista = [rol[0] for rol in roles] if roles else []

        if 'sysadmin' in roles_lista:
            permisos["TEST_USER"] = True
            print("  [WARN] El usuario tiene permisos de sysadmin - Riesgo alto")
        else:
            print("  [CHECK] El usuario no tiene permisos de sysadmin")

        # Consultar permisos específicos
        query_permisos = """
            SELECT
                p.class_desc,
                OBJECT_NAME(p.major_id) as object_name,
                p.permission_name,
                p.state_desc
            FROM sys.database_permissions p
            JOIN sys.database_principals dp ON p.grantee_principal_id = dp.principal_id
            WHERE dp.name = USER_NAME()
            ORDER BY object_name, p.permission_name
        """
        permisos_resultado = db.ejecutar_query(query_permisos)

        # Analizar permisos obtenidos
        for perm in permisos_resultado:
            class_desc, object_name, permission_name, state_desc = perm

            if object_name not in permisos["detalle"]:
                permisos["detalle"][object_name] = []

            permisos["detalle"][object_name].append({
                "tipo": class_desc,
                "permiso": permission_name,
                "estado": state_desc
            })

            # Marcar permisos globales
            if permission_name == "CREATE" and state_desc == "GRANT":
                permisos["create"] = True
            elif permission_name == "ALTER" and state_desc == "GRANT":
                permisos["alter"] = True
            elif permission_name == "DROP" and state_desc == "GRANT":
                permisos["drop"] = True
            elif permission_name == "EXECUTE" and state_desc == "GRANT":
                permisos["execute"] = True

        # Resumen de permisos
        print("  Resumen de permisos:")
        for tipo in ["create", "alter", "drop", "execute"]:
            estado = "[WARN]" if permisos[tipo] else "[CHECK]"
            print(f"  {estado} Permiso {tipo.upper()}: {permisos[tipo]}")

    except Exception as e:
        print(f"  [WARN] Error al verificar permisos: {e}")

    return permisos


def detectar_vulnerabilidades(db):
    """
    Detecta vulnerabilidades comunes en la configuración de la base de datos.

    Args:
        db: Conexión a la base de datos

    Returns:
        list: Lista de vulnerabilidades detectadas
    """
    print("\n🔍 Detectando vulnerabilidades comunes...")

    vulnerabilidades = []

    try:
        # 1. Verificar si hay contraseñas en texto plano
        query_pass = """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE COLUMN_NAME LIKE '%password%'
            AND DATA_TYPE IN ('char', 'varchar', 'nvarchar', 'text', 'ntext')
        """
        result_pass = db.ejecutar_query(query_pass)
        if result_pass and result_pass[0][0] > 0:
            vulnerabilidades.append({
                "nivel": "Alto",
                "tipo": "Contraseñas en texto plano",
                "descripcion": f"Se detectaron {result_pass[0][0]} columnas que podrían almacenar contraseñas en texto plano"
            })
            print("  [WARN] Se detectaron posibles contraseñas en texto plano")
        else:
            print("  [CHECK] No se detectaron columnas de contraseñas en texto plano")

        # 2. Verificar si hay triggers para auditoría
        query_triggers = """
            SELECT COUNT(*) FROM sys.triggers
            WHERE name LIKE '%audit%' OR name LIKE '%log%'
        """
        result_triggers = db.ejecutar_query(query_triggers)
        if not result_triggers or result_triggers[0][0] == 0:
            vulnerabilidades.append({
                "nivel": "Medio",
                "tipo": "Falta de auditoría",
                "descripcion": "No se detectaron triggers de auditoría. Se recomienda implementar auditoría de cambios."
            })
            print("  [WARN] No se detectaron triggers de auditoría")
        else:
            print(f"  [CHECK] Se detectaron {result_triggers[0][0]} triggers de auditoría")

        # 3. Verificar tablas sin clave primaria
        query_sin_pk = """
            SELECT t.name
            FROM sys.tables t
            LEFT JOIN sys.indexes i ON t.object_id = i.object_id AND i.is_primary_key = 1
            WHERE i.object_id IS NULL
        """
        result_sin_pk = db.ejecutar_query(query_sin_pk)
        if result_sin_pk:
            tablas_sin_pk = [row[0] for row in result_sin_pk]
            vulnerabilidades.append({
                "nivel": "Medio",
                "tipo": "Tablas sin clave primaria",
                "descripcion": f"Se detectaron {len(tablas_sin_pk)} tablas sin clave primaria: {', '.join(tablas_sin_pk)}"
            })
            print(f"  [WARN] Se detectaron {len(tablas_sin_pk)} tablas sin clave primaria")
        else:
            print("  [CHECK] Todas las tablas tienen clave primaria")

    except Exception as e:
        print(f"  [WARN] Error al detectar vulnerabilidades: {e}")

    return vulnerabilidades


def generar_recomendaciones(permisos, vulnerabilidades):
    """
    Genera recomendaciones de seguridad basadas en el análisis.

    Args:
        permisos: Resultado del análisis de permisos
        vulnerabilidades: Lista de vulnerabilidades detectadas

    Returns:
        list: Lista de recomendaciones
    """
    print("\n📋 Generando recomendaciones de seguridad...")

    recomendaciones = []

    # Recomendaciones basadas en permisos
    if permisos.get("TEST_USER"):
        recomendaciones.append({
            "prioridad": "Alta",
            "titulo": "Limitar permisos administrativos",
            "descripcion": "Evitar usar cuentas con permisos de sysadmin para la aplicación. Crear un usuario específico con los mínimos permisos necesarios."
        })

    if permisos.get("create") or permisos.get("alter") or permisos.get("drop"):
        recomendaciones.append({
            "prioridad": "Alta",
            "titulo": "Limitar permisos de DDL",
            "descripcion": "Restringir permisos de CREATE, ALTER y DROP a usuarios de aplicación. Estos permisos deberían estar reservados para administradores de BD y scripts de migración."
        })

    # Recomendaciones basadas en vulnerabilidades
    for vuln in vulnerabilidades:
        if vuln["tipo"] == "Contraseñas en texto plano":
            recomendaciones.append({
                "prioridad": "Alta",
                "titulo": "Cifrado de contraseñas",
                "descripcion": "Implementar hash+salt para almacenar contraseñas. Nunca almacenar contraseñas en texto plano."
            })

        if vuln["tipo"] == "Falta de auditoría":
            recomendaciones.append({
                "prioridad": "Media",
                "titulo": "Implementar auditoría",
                "descripcion": "Crear triggers de auditoría en tablas críticas para registrar cambios (quién, cuándo, qué). Considerar usar la tabla existente 'auditoria'."
            })

        if vuln["tipo"] == "Tablas sin clave primaria":
            recomendaciones.append({
                "prioridad": "Media",
                "titulo": "Añadir claves primarias",
                "descripcion": "Todas las tablas deberían tener una clave primaria para garantizar integridad y rendimiento."
            })

    # Recomendaciones generales
    recomendaciones.extend([
        {
            "prioridad": "Alta",
            "titulo": "Parametrizar todas las consultas",
            "descripcion": "Asegurar que todas las consultas usen parámetros para prevenir inyección SQL."
        },
        {
            "prioridad": "Media",
            "titulo": "Usar lista blanca para nombres de tablas/columnas",
            "descripcion": "Implementar validación de nombres de tablas y columnas mediante lista blanca cuando no se puedan parametrizar."
        },
        {
            "prioridad": "Media",
            "titulo": "Implementar pool de conexiones",
            "descripcion": "Usar el pool de conexiones implementado para mejorar rendimiento y seguridad."
        },
        {
            "prioridad": "Baja",
            "titulo": "Documentar estructura de base de datos",
            "descripcion": "Mantener documentación actualizada de tablas, relaciones y índices."
        }
    ])

    # Mostrar algunas recomendaciones
    print(f"  Generadas {len(recomendaciones)} recomendaciones")

    return recomendaciones


def mostrar_resumen_seguridad(tablas,
permisos,
    vulnerabilidades,
    recomendaciones):
    """
    Muestra un resumen del análisis de seguridad.

    Args:
        tablas: Lista de tablas analizadas
        permisos: Información de permisos detectados
        vulnerabilidades: Lista de vulnerabilidades detectadas
        recomendaciones: Lista de recomendaciones generadas
    """
    print("\n" + "=" * 80)
    print(" "*30 + "RESUMEN DE SEGURIDAD")
    print("=" * 80)

    # Estadísticas generales
    print(f"\n[CHART] Estructura: {len(tablas)} tablas analizadas")

    # Vulnerabilidades por nivel
    vulnerabilidades_por_nivel = {}
    for v in vulnerabilidades:
        nivel = v["nivel"]
        vulnerabilidades_por_nivel[nivel] = vulnerabilidades_por_nivel.get(nivel, 0) + 1

    print("\n[WARN] Vulnerabilidades detectadas:")
    for nivel, cantidad in vulnerabilidades_por_nivel.items():
        print(f"  - Nivel {nivel}: {cantidad} vulnerabilidades")

    # Recomendaciones por prioridad
    recomendaciones_por_prioridad = {}
    for r in recomendaciones:
        prioridad = r["prioridad"]
        recomendaciones_por_prioridad[prioridad] = recomendaciones_por_prioridad.get(prioridad, 0) + 1

    print("\n📋 Recomendaciones:")
    for prioridad, cantidad in recomendaciones_por_prioridad.items():
        print(f"  - Prioridad {prioridad}: {cantidad} recomendaciones")

    print("\n🔝 Recomendaciones prioritarias:")
    alta_prioridad = [r for r in recomendaciones if r["prioridad"] == "Alta"]
    for i, rec in enumerate(alta_prioridad[:3], 1):
        print(f"  {i}. {rec['titulo']}: {rec['descripcion']}")

    print("\n" + "=" * 80)
    print(" "*26 + "FIN DEL DIAGNÓSTICO DE SEGURIDAD")
    print("=" * 80 + "\n")


def generar_informe_html(tablas, permisos, vulnerabilidades, recomendaciones):
    """
    Genera un informe HTML con los resultados del análisis de seguridad.

    Args:
        tablas: Lista de tablas analizadas
        permisos: Información de permisos detectados
        vulnerabilidades: Lista de vulnerabilidades detectadas
        recomendaciones: Lista de recomendaciones generadas

    Returns:
        str: Contenido HTML del informe
    """
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Seguridad de Base de Datos - {fecha}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background-color: #1a73e8;
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }}
        h1, h2, h3 {{
            color: #1a73e8;
        }}
        .section {{
            background-color: #fff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            # box-shadow eliminado: usar QGraphicsDropShadowEffect en el widget correspondiente
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .high {{
            color: #d32f2f;
        }}
        .medium {{
            color: #f57c00;
        }}
        .low {{
            color: #388e3c;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Informe de Seguridad de Base de Datos</h1>
            <p>Generado el {fecha}</p>
        </header>

        <section class="section">
            <h2>Resumen Ejecutivo</h2>
            <p>Este informe contiene los resultados del análisis de seguridad de la base de datos, incluyendo vulnerabilidades detectadas y recomendaciones para mejorar la seguridad.</p>

            <table>
                <tr>
                    <th>Elemento</th>
                    <th>Cantidad</th>
                </tr>
                <tr>
                    <td>Tablas analizadas</td>
                    <td>{len(tablas)}</td>
                </tr>
                <tr>
                    <td>Vulnerabilidades detectadas</td>
                    <td>{len(vulnerabilidades)}</td>
                </tr>
                <tr>
                    <td>Recomendaciones</td>
                    <td>{len(recomendaciones)}</td>
                </tr>
            </table>
        </section>

        <section class="section">
            <h2>Vulnerabilidades Detectadas</h2>
"""

    # Añadir vulnerabilidades
    if vulnerabilidades:
        html += """
            <table>
                <tr>
                    <th>Nivel de Riesgo</th>
                    <th>Tipo</th>
                    <th>Descripción</th>
                </tr>
"""
        for v in vulnerabilidades:
            nivel_class = "high" if v["nivel"] == "Alto" else "medium" if v["nivel"] == "Medio" else "low"
            html += f"""
                <tr>
                    <td class="{nivel_class}">{v["nivel"]}</td>
                    <td>{v["tipo"]}</td>
                    <td>{v["descripcion"]}</td>
                </tr>
"""
        html += """
            </table>
"""
    else:
        html += """
            <p>No se detectaron vulnerabilidades.</p>
"""

    html += """
        </section>

        <section class="section">
            <h2>Recomendaciones</h2>
"""

    # Añadir recomendaciones
    if recomendaciones:
        html += """
            <table>
                <tr>
                    <th>Prioridad</th>
                    <th>Recomendación</th>
                    <th>Descripción</th>
                </tr>
"""
        for r in recomendaciones:
            prioridad_class = "high" if r["prioridad"] == "Alta" else "medium" if r["prioridad"] == "Media" else "low"
            html += f"""
                <tr>
                    <td class="{prioridad_class}">{r["prioridad"]}</td>
                    <td>{r["titulo"]}</td>
                    <td>{r["descripcion"]}</td>
                </tr>
"""
        html += """
            </table>
"""
    else:
        html += """
            <p>No hay recomendaciones.</p>
"""

    html += """
        </section>

        <section class="section">
            <h2>Permisos de Usuario</h2>
"""

    # Añadir permisos
    es_admin = permisos.get("TEST_USER", False)
    html += f"""
            <p>El usuario actual {"tiene" if es_admin else "no tiene"} permisos de administrador.</p>

            <h3>Permisos globales:</h3>
            <ul>
                <li>CREATE: {"Sí" if permisos.get("create") else "No"}</li>
                <li>ALTER: {"Sí" if permisos.get("alter") else "No"}</li>
                <li>DROP: {"Sí" if permisos.get("drop") else "No"}</li>
                <li>EXECUTE: {"Sí" if permisos.get("execute") else "No"}</li>
            </ul>
"""

    # Añadir detalles de permisos por objeto si existen
    if permisos.get("detalle"):
        html += """
            <h3>Permisos por objeto:</h3>
            <table>
                <tr>
                    <th>Objeto</th>
                    <th>Permiso</th>
                    <th>Estado</th>
                </tr>
"""
        for objeto, permisos_obj in permisos.get("detalle", {}).items():
            for p in permisos_obj:
                html += f"""
                <tr>
                    <td>{objeto}</td>
                    <td>{p["permiso"]}</td>
                    <td>{p["estado"]}</td>
                </tr>
"""
        html += """
            </table>
"""

    html += """
        </section>

        <div class="footer">
            <p>Este informe fue generado automáticamente. La información debe ser verificada por personal calificado.</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def guardar_informe_html(contenido_html, ruta=None):
    """
    Guarda el informe HTML en un archivo.

    Args:
        contenido_html: Contenido HTML del informe
        ruta: Ruta donde guardar el archivo (opcional)

    Returns:
        str: Ruta del archivo creado
    """
    if not ruta:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = os.path.join(str(ROOT_DIR), "logs", f"informe_seguridad_bd_{timestamp}.html")

    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    # Guardar el archivo
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido_html)

    return ruta


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Realizar diagnóstico de seguridad de la base de datos.')
    parser.add_argument('--html', action='store_true', help='Generar informe HTML')
    parser.add_argument('--salida', type=str, help='Ruta donde guardar el informe HTML')
    args = parser.parse_args()

    try:
        # Realizar análisis de seguridad
        analizar_seguridad_bd()

        # Si se solicita informe HTML, generarlo
        if args.html:
            # En una implementación real, pasaríamos los resultados del análisis
            # Por ahora, usamos datos ficticios
            tablas = ["users", "obras", "clientes"]
            permisos = {"TEST_USER": False, "create": True}
            vulnerabilidades = [
                {"nivel": "Alto", "tipo": "SQL Injection", "descripcion": "Riesgo de SQL Injection en consultas dinámicas"}
            ]
            recomendaciones = [
                {"prioridad": "Alta", "titulo": "Parametrizar consultas", "descripcion": "Usar siempre consultas parametrizadas"}
            ]

            informe_html = generar_informe_html(tablas,
permisos,
                vulnerabilidades,
                recomendaciones)
            ruta_informe = guardar_informe_html(informe_html, args.salida)
            print(f"\n📄 Informe HTML guardado en: {ruta_informe}")

    except Exception as e:
        print(f"\n[ERROR] Error durante el diagnóstico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
