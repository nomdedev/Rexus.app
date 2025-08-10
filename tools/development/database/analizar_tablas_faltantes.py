"""
Analizador de Tablas Faltantes - Diagnostico Completo
Identifica qué tablas no existen y explica su propósito en el sistema
"""

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Definición de todas las tablas que el sistema necesita para funcionalidad completa
TABLAS_REQUERIDAS = {
    # TABLAS PRINCIPALES (Deberían existir)
    'obras': {
        'modulo': 'Obras',
        'proposito': 'Tabla central que almacena información de todas las obras/proyectos',
        'obligatoria': True,
        'descripcion': 'Contiene datos básicos de obras: nombre, cliente, estado, fechas, etc.',
        'usado_en': ['Todos los módulos como referencia central']
    },

    'inventario_perfiles': {
        'modulo': 'Inventario',
        'proposito': 'Catálogo de perfiles y materiales disponibles',
        'obligatoria': True,
        'descripcion': 'Lista de productos, códigos, precios, stock disponible',
        'usado_en': ['Módulo Inventario', 'Pedidos de material', 'Cotizaciones']
    },

    'users': {
        'modulo': 'Usuarios',
        'proposito': 'Gestión de usuarios y permisos del sistema',
        'obligatoria': True,
        'descripcion': 'Datos de login, roles, permisos por módulo',
        'usado_en': ['Sistema de autenticación', 'Control de acceso', 'Auditoría']
    },

    # TABLAS DE PEDIDOS (Para integración cruzada)
    'pedidos_material': {
        'modulo': 'Inventario',
        'proposito': 'Registrar pedidos de materiales por obra',
        'obligatoria': False,
        'descripcion': 'Almacena qué materiales se pidieron para cada obra, cantidades, estados',
        'usado_en': ['Módulo Inventario', 'Vista integrada de Obras', 'Logística'],
        'campos_principales': [
            'id (PK)',
            'obra_id (FK a obras)',
            'material_id (FK a inventario_perfiles)',
            'cantidad',
            'estado (pendiente/pedido/recibido/completado)',
            'fecha_pedido',
            'usuario_id',
            'observaciones'
        ]
    },

    'vidrios_por_obra': {
        'modulo': 'Vidrios',
        'proposito': 'Gestión unificada de vidrios por obra (TABLA PRINCIPAL DE VIDRIOS)',
        'obligatoria': False,
        'descripcion': 'ESTA ES LA TABLA PRINCIPAL para vidrios. Reemplaza la tabla "vidrios" que no existe.',
        'usado_en': ['Módulo Vidrios', 'Vista integrada de Obras', 'Producción', 'Logística'],
        'campos_principales': [
            'id (PK)',
            'obra_id (FK a obras)',
            'tipo_vidrio (ej: DVH, Laminado, Templado)',
            'medidas (ej: 120x80)',
            'cantidad',
            'estado (pendiente/en_produccion/listo/entregado)',
            'fecha_pedido',
            'fecha_entrega_estimada',
            'proveedor',
            'costo',
            'observaciones'
        ]
    },

    'pedidos_herrajes': {
        'modulo': 'Herrajes',
        'proposito': 'Registrar pedidos de herrajes por obra',
        'obligatoria': False,
        'descripcion': 'Almacena herrajes solicitados para cada obra (cerraduras, bisagras, etc.)',
        'usado_en': ['Módulo Herrajes', 'Vista integrada de Obras', 'Logística'],
        'campos_principales': [
            'id (PK)',
            'obra_id (FK a obras)',
            'herraje_id (FK a catálogo de herrajes)',
            'tipo_herraje (cerradura/bisagra/manija/etc)',
            'cantidad',
            'estado (pendiente/pedido/recibido/instalado)',
            'fecha_pedido',
            'proveedor',
            'costo'
        ]
    },

    'pagos_pedidos': {
        'modulo': 'Contabilidad',
        'proposito': 'Registro de pagos relacionados con pedidos por obra',
        'obligatoria': False,
        'descripcion': 'Controla qué se ha pagado de cada pedido (materiales, vidrios, herrajes)',
        'usado_en': ['Módulo Contabilidad', 'Vista integrada de Obras', 'Control financiero'],
        'campos_principales': [
            'id (PK)',
            'obra_id (FK a obras)',
            'modulo (inventario/vidrios/herrajes)',
            'tipo_pedido',
            'monto_total',
            'monto_pagado',
            'estado (pendiente/parcial/completado)',
            'fecha_vencimiento',
            'fecha_pago',
            'metodo_pago',
            'observaciones'
        ]
    },

    # TABLAS DE AUDITORÍA (Opcionales pero recomendadas)
    'auditoria': {
        'modulo': 'Auditoría',
        'proposito': 'Registro de todas las acciones del sistema',
        'obligatoria': False,
        'descripcion': 'Log de actividades: quién hizo qué, cuándo, desde dónde',
        'usado_en': ['Módulo Auditoría', 'Seguridad', 'Trazabilidad'],
        'campos_principales': [
            'id (PK)',
            'usuario_id',
            'modulo',
            'accion',
            'detalle',
            'ip_address',
            'fecha_hora'
        ]
    }
}

def verificar_tablas_existentes():
    """Verifica qué tablas existen realmente en la base de datos"""

    print("🔍 VERIFICANDO TABLAS EXISTENTES EN LA BASE DE DATOS")
    print("=" * 60)

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        # Conectar a la base de datos
        db = ObrasDatabaseConnection()
        db.conectar()
        print(f"[CHECK] Conectado a base de datos: {db.database}")
        print(f"📍 Servidor: {db.server}\n")

        # Obtener lista de todas las tablas existentes
        query_tablas = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """

        try:
            resultado = db.ejecutar_query(query_tablas)
            if resultado:
                tablas_existentes = [row[0] for row in resultado]
                print(f"[CHART] TABLAS ENCONTRADAS EN LA BASE DE DATOS ({len(tablas_existentes)}):")
                for tabla in tablas_existentes:
                    print(f"   [CHECK] {tabla}")
            else:
                print("[ERROR] No se pudieron obtener las tablas de la base de datos")
                return []

        except Exception as e:
            print(f"[ERROR] Error consultando tablas: {e}")
            return []

        print(f"\n🔍 ANÁLISIS DE TABLAS REQUERIDAS:")
        print("-" * 60)

        tablas_faltantes = []
        tablas_existentes_requeridas = []

        for nombre_tabla, info in TABLAS_REQUERIDAS.items():
            if nombre_tabla in tablas_existentes:
                tablas_existentes_requeridas.append(nombre_tabla)
                status = "[CHECK] EXISTE"
                if info['obligatoria']:
                    status += " (OBLIGATORIA)"
                print(f"\n📋 {nombre_tabla}: {status}")
                print(f"   Módulo: {info['modulo']}")
                print(f"   Propósito: {info['proposito']}")
            else:
                tablas_faltantes.append(nombre_tabla)
                status = "[ERROR] FALTANTE"
                if info['obligatoria']:
                    status += " ([WARN] CRÍTICA)"
                else:
                    status += " (🔧 OPCIONAL)"

                print(f"\n📋 {nombre_tabla}: {status}")
                print(f"   Módulo: {info['modulo']}")
                print(f"   Propósito: {info['proposito']}")
                print(f"   Descripción: {info['descripcion']}")
                print(f"   Usado en: {', '.join(info['usado_en'])}")

                if 'campos_principales' in info:
                    print(f"   Campos principales:")
                    for campo in info['campos_principales']:
                        print(f"     • {campo}")

        # Resumen final
        print(f"\n" + "=" * 60)
        print(f"[CHART] RESUMEN DE ANÁLISIS")
        print("=" * 60)
        print(f"🗄️  Total de tablas en BD: {len(tablas_existentes)}")
        print(f"[CHECK] Tablas requeridas existentes: {len(tablas_existentes_requeridas)}")
        print(f"[ERROR] Tablas faltantes: {len(tablas_faltantes)}")

        # Clasificar faltantes por criticidad
        faltantes_criticas = [t for t in tablas_faltantes if TABLAS_REQUERIDAS[t]['obligatoria']]
        faltantes_opcionales = [t for t in tablas_faltantes if not TABLAS_REQUERIDAS[t]['obligatoria']]

        if faltantes_criticas:
            print(f"\n🚨 TABLAS CRÍTICAS FALTANTES ({len(faltantes_criticas)}):")
            for tabla in faltantes_criticas:
                print(f"   [WARN]  {tabla} - {TABLAS_REQUERIDAS[tabla]['proposito']}")

        if faltantes_opcionales:
            print(f"\n🔧 TABLAS OPCIONALES FALTANTES ({len(faltantes_opcionales)}):")
            for tabla in faltantes_opcionales:
                print(f"   📋 {tabla} - {TABLAS_REQUERIDAS[tabla]['proposito']}")

        # Evaluación del estado
        print(f"\n🎯 EVALUACIÓN DEL SISTEMA:")
        if len(faltantes_criticas) == 0:
            if len(faltantes_opcionales) == 0:
                print("🎉 ESTADO: [CHECK] PERFECTO - Todas las tablas están presentes")
            elif len(faltantes_opcionales) <= 2:
                print("[CHECK] ESTADO: EXCELENTE - Sistema completamente funcional")
                print("💡 Las tablas faltantes son opcionales y no afectan la funcionalidad básica")
            else:
                print("🔧 ESTADO: BUENO - Sistema funcional con limitaciones")
                print("💡 Considera crear las tablas opcionales para funcionalidad completa")
        else:
            print("🚨 ESTADO: REQUIERE ATENCIÓN - Faltan tablas críticas")
            print("[WARN]  El sistema puede tener problemas sin las tablas obligatorias")

        # Explicación de los errores SQL
        print(f"\n" + "=" * 60)
        print("🔍 EXPLICACIÓN DE LOS ERRORES SQL QUE VES")
        print("=" * 60)

        if 'pedidos_material' in tablas_faltantes:
            print("[ERROR] Error 'pedidos_material no es válido':")
            print("   • El módulo Inventario intenta consultar esta tabla")
            print("   • La tabla no existe, por eso SQL devuelve error 42S02")
            print("   • El sistema está diseñado para manejar este error gracefully")
            print("   • Sin la tabla: devuelve estado 'pendiente' por defecto")
            print("   • Con la tabla: podría rastrear pedidos reales por obra")

        if 'vidrios_por_obra' in tablas_faltantes:
            print("\n[ERROR] Error 'vidrios_por_obra no es válido':")
            print("   • El módulo Vidrios (unificado) busca esta tabla")
            print("   • Esta es la tabla PRINCIPAL para gestión de vidrios")
            print("   • Reemplaza la antigua tabla 'vidrios' que no existía")
            print("   • Sin la tabla: estado por defecto")
            print("   • Con la tabla: gestión completa de vidrios por obra")

        if 'pedidos_herrajes' in tablas_faltantes:
            print("\n[ERROR] Error 'pedidos_herrajes no es válido':")
            print("   • El módulo Herrajes intenta consultar esta tabla")
            print("   • Para rastrear herrajes pedidos por obra")
            print("   • Sin la tabla: funcionalidad limitada")

        if 'pagos_pedidos' in tablas_faltantes:
            print("\n[ERROR] Error 'pagos_pedidos no es válido':")
            print("   • El módulo Contabilidad busca esta tabla")
            print("   • Para rastrear pagos por módulo y obra")
            print("   • Sin la tabla: no hay tracking de pagos")

        print(f"\n💡 IMPORTANTE:")
        print("   • Los errores SQL son NORMALES en instalaciones nuevas")
        print("   • El sistema está diseñado para funcionar sin estas tablas")
        print("   • Cuando faltan tablas, devuelve estados por defecto")
        print("   • La integración visual funciona correctamente")
        print("   • Puedes usar el sistema inmediatamente")

        # Generar scripts de creación si es necesario
        if tablas_faltantes:
            print(f"\n" + "=" * 60)
            print("🛠️  SCRIPTS DE CREACIÓN DE TABLAS FALTANTES")
            print("=" * 60)
            print("Si quieres funcionalidad completa, ejecuta estos comandos SQL:\n")

            generar_scripts_creacion(tablas_faltantes)

        # Cerrar conexión
        if db.connection:
            db.connection.close()

        return {
            'existentes': tablas_existentes_requeridas,
            'faltantes': tablas_faltantes,
            'criticas_faltantes': faltantes_criticas,
            'opcionales_faltantes': faltantes_opcionales
        }

    except Exception as e:
        print(f"[ERROR] Error durante la verificación: {e}")
        traceback.print_exc()
        return None

def generar_scripts_creacion(tablas_faltantes):
    """Genera los scripts SQL para crear las tablas faltantes"""
import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication

from core.database import ObrasDatabaseConnection

    scripts = {
        'pedidos_material': """
-- Tabla para pedidos de materiales por obra
CREATE TABLE pedidos_material (
    id INT PRIMARY KEY IDENTITY(1,1),
    obra_id INT NOT NULL,
    material_id INT NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'pendiente',
    fecha_pedido DATETIME DEFAULT GETDATE(),
    fecha_entrega_estimada DATETIME NULL,
    usuario_id INT NULL,
    proveedor VARCHAR(100) NULL,
    costo DECIMAL(10,2) NULL,
    observaciones TEXT NULL,
    FOREIGN KEY (obra_id) REFERENCES obras(id)
);
""",

        'vidrios_por_obra': """
-- Tabla PRINCIPAL para gestión unificada de vidrios
CREATE TABLE vidrios_por_obra (
    id INT PRIMARY KEY IDENTITY(1,1),
    obra_id INT NOT NULL,
    tipo_vidrio VARCHAR(100) NOT NULL,
    medidas VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    estado VARCHAR(50) DEFAULT 'pendiente',
    fecha_pedido DATETIME DEFAULT GETDATE(),
    fecha_entrega_estimada DATETIME NULL,
    fecha_entrega_real DATETIME NULL,
    proveedor VARCHAR(100) NULL,
    costo DECIMAL(10,2) NULL,
    ubicacion_instalacion VARCHAR(200) NULL,
    observaciones TEXT NULL,
    FOREIGN KEY (obra_id) REFERENCES obras(id)
);
""",

        'pedidos_herrajes': """
-- Tabla para pedidos de herrajes por obra
CREATE TABLE pedidos_herrajes (
    id INT PRIMARY KEY IDENTITY(1,1),
    obra_id INT NOT NULL,
    tipo_herraje VARCHAR(100) NOT NULL,
    descripcion VARCHAR(200) NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'pendiente',
    fecha_pedido DATETIME DEFAULT GETDATE(),
    fecha_entrega_estimada DATETIME NULL,
    usuario_id INT NULL,
    proveedor VARCHAR(100) NULL,
    costo DECIMAL(10,2) NULL,
    observaciones TEXT NULL,
    FOREIGN KEY (obra_id) REFERENCES obras(id)
);
""",

        'pagos_pedidos': """
-- Tabla para tracking de pagos por módulo y obra
CREATE TABLE pagos_pedidos (
    id INT PRIMARY KEY IDENTITY(1,1),
    obra_id INT NOT NULL,
    modulo VARCHAR(50) NOT NULL, -- 'inventario', 'vidrios', 'herrajes'
    tipo_pedido VARCHAR(100) NULL,
    monto_total DECIMAL(10,2) NOT NULL,
    monto_pagado DECIMAL(10,2) DEFAULT 0,
    estado VARCHAR(50) DEFAULT 'pendiente',
    fecha_vencimiento DATETIME NULL,
    fecha_pago DATETIME NULL,
    metodo_pago VARCHAR(50) NULL,
    numero_comprobante VARCHAR(100) NULL,
    observaciones TEXT NULL,
    FOREIGN KEY (obra_id) REFERENCES obras(id)
);
""",

        'auditoria': """
-- Tabla para auditoría del sistema
CREATE TABLE auditoria (
    id INT PRIMARY KEY IDENTITY(1,1),
    usuario_id INT NULL,
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(100) NOT NULL,
    detalle TEXT NULL,
    ip_address VARCHAR(45) NULL,
    fecha DATETIME DEFAULT GETDATE()
);
"""
    }

    for tabla in tablas_faltantes:
        if tabla in scripts:
            print(f"-- ========================")
            print(f"-- SCRIPT PARA: {tabla}")
            print(f"-- ========================")
            print(scripts[tabla])

if __name__ == "__main__":
    print("[ROCKET] Iniciando análisis de tablas faltantes...")
    resultado = verificar_tablas_existentes()

    if resultado:
        print(f"\n[CHECK] Análisis completado exitosamente")
        if isinstance(resultado, dict) and len(resultado.get('criticas_faltantes', [])) == 0:
            print(f"🎉 Tu sistema está listo para usar!")
        else:
            print(f"[WARN]  Considera crear las tablas críticas para funcionalidad completa")
    else:
        print(f"\n[ERROR] Error durante el análisis")
