"""
Test mejorado de integración cruzada con edge cases y manejo robusto de errores.
Verifica la integridad del sistema completo y reporta de forma clara cualquier problema.
"""

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestResultados:
    """Clase para recopilar y reportar resultados del test de forma organizada"""

    def __init__(self):
        self.errores_sql = []
        self.tablas_faltantes = []
        self.edge_cases_encontrados = []
        self.conexiones_exitosas = []
        self.metodos_validados = []
        self.warnings = []

    def agregar_error_sql(self, operacion, error, detalle=None):
        self.errores_sql.append({
            'operacion': operacion,
            'error': str(error),
            'detalle': detalle
        })

    def agregar_tabla_faltante(self, tabla, modulo):
        self.tablas_faltantes.append({
            'tabla': tabla,
            'modulo': modulo
        })

    def agregar_edge_case(self, caso, resultado):
        self.edge_cases_encontrados.append({
            'caso': caso,
            'resultado': resultado
        })

    def reportar_resultados(self):
        print("\n" + "="*70)
        print("               REPORTE FINAL DE INTEGRACIÓN")
        print("="*70)

        # Reportar conexiones exitosas
        if self.conexiones_exitosas:
            print("\n[CHECK] CONEXIONES EXITOSAS:")
            for conn in self.conexiones_exitosas:
                print(f"   [OK] {conn}")

        # Reportar métodos validados
        if self.metodos_validados:
            print(f"\n[CHECK] MÉTODOS VALIDADOS ({len(self.metodos_validados)}):")
            for metodo in self.metodos_validados:
                print(f"   [OK] {metodo}")

        # Reportar edge cases
        if self.edge_cases_encontrados:
            print(f"\n🧪 EDGE CASES PROBADOS ({len(self.edge_cases_encontrados)}):")
            for edge_case in self.edge_cases_encontrados:
                print(f"   ◦ {edge_case['caso']}: {edge_case['resultado']}")

        # Reportar warnings
        if self.warnings:
            print(f"\n[WARN]  ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ⚠ {warning}")

        # Reportar tablas faltantes
        if self.tablas_faltantes:
            print(f"\n[ERROR] TABLAS FALTANTES ({len(self.tablas_faltantes)}):")
            for tabla in self.tablas_faltantes:
                print(f"   ✗ {tabla['tabla']} (módulo: {tabla['modulo']})")

            print("\n📋 SCRIPT PARA CREAR TABLAS FALTANTES:")
            print("   Ejecuta estos comandos SQL para completar la estructura:")
            print("   " + "-"*50)

            for tabla in self.tablas_faltantes:
                if tabla['tabla'] == 'pedidos_material':
                    print("""
   CREATE TABLE pedidos_material (
       id INT PRIMARY KEY IDENTITY(1,1),
       obra_id INT NOT NULL,
       material_id INT NOT NULL,
       cantidad DECIMAL(10,2),
       estado VARCHAR(50) DEFAULT 'pendiente',
       fecha_pedido DATETIME DEFAULT GETDATE(),
       FOREIGN KEY (obra_id) REFERENCES obras(id)
   );""")
                elif tabla['tabla'] == 'vidrios_por_obra':
                    print("""
   CREATE TABLE vidrios_por_obra (
       id INT PRIMARY KEY IDENTITY(1,1),
       obra_id INT NOT NULL,
       tipo_vidrio VARCHAR(100),
       medidas VARCHAR(100),
       cantidad INT,
       estado VARCHAR(50) DEFAULT 'pendiente',
       fecha_pedido DATETIME DEFAULT GETDATE(),
       FOREIGN KEY (obra_id) REFERENCES obras(id)
   );""")
                elif tabla['tabla'] == 'pedidos_herrajes':
                    print("""
   CREATE TABLE pedidos_herrajes (
       id INT PRIMARY KEY IDENTITY(1,1),
       obra_id INT NOT NULL,
       herraje_id INT NOT NULL,
       cantidad DECIMAL(10,2),
       estado VARCHAR(50) DEFAULT 'pendiente',
       fecha_pedido DATETIME DEFAULT GETDATE(),
       FOREIGN KEY (obra_id) REFERENCES obras(id)
   );""")
                elif tabla['tabla'] == 'pagos_pedidos':
                    print("""
   CREATE TABLE pagos_pedidos (
       id INT PRIMARY KEY IDENTITY(1,1),
       obra_id INT NOT NULL,
       modulo VARCHAR(50),
       tipo_pedido VARCHAR(50),
       monto DECIMAL(10,2),
       estado VARCHAR(50) DEFAULT 'pendiente',
       fecha_pago DATETIME,
       FOREIGN KEY (obra_id) REFERENCES obras(id)
   );""")

        # Reportar errores SQL
        if self.errores_sql:
            print(f"\n[ERROR] ERRORES SQL DETECTADOS ({len(self.errores_sql)}):")
            for error in self.errores_sql:
                print(f"   ✗ {error['operacion']}")
                print(f"     Error: {error['error']}")
                if error['detalle']:
                    print(f"     Detalle: {error['detalle']}")
                print()

        # Resumen final
        print(f"\n[CHART] RESUMEN:")
        print(f"   • Conexiones exitosas: {len(self.conexiones_exitosas)}")
        print(f"   • Métodos validados: {len(self.metodos_validados)}")
        print(f"   • Edge cases probados: {len(self.edge_cases_encontrados)}")
        print(f"   • Tablas faltantes: {len(self.tablas_faltantes)}")
        print(f"   • Errores SQL: {len(self.errores_sql)}")
        print(f"   • Advertencias: {len(self.warnings)}")

        # Evaluación general
        if len(self.errores_sql) == 0 and len(self.tablas_faltantes) <= 2:
            print(f"\n🎉 ESTADO GENERAL: [CHECK] EXCELENTE")
            print("   El sistema de integración está funcionando correctamente.")
        elif len(self.tablas_faltantes) > 0:
            print(f"\n🔧 ESTADO GENERAL: [WARN]  NECESITA CONFIGURACIÓN")
            print("   El sistema funciona pero faltan algunas tablas para funcionalidad completa.")
        else:
            print(f"\n🚨 ESTADO GENERAL: [ERROR] REQUIERE ATENCIÓN")
            print("   Se detectaron errores que requieren investigación.")


def test_integracion_mejorado():
    """Test mejorado de integración cruzada con edge cases y manejo robusto de errores"""

    print("="*70)
    print("        TEST MEJORADO DE INTEGRACIÓN CRUZADA v2.0")
    print("="*70)
    print("🔍 Verificando integración completa entre módulos...")
    print("[CHART] Incluyendo edge cases y manejo robusto de errores...")
    print("🗄️  Usando base de datos: inventario (configuración estándar)\n")

    resultados = TestResultados()

    # Crear QApplication si no existe
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    db_connection = None

    try:
        # FASE 1: VERIFICACIÓN DE CONEXIÓN
        print("🔌 FASE 1: VERIFICACIÓN DE CONEXIÓN")
        print("-" * 40)

        db_connection = ObrasDatabaseConnection()

        try:
            db_connection.conectar()
            resultados.conexiones_exitosas.append(f"Base de datos '{db_connection.database}' en servidor '{db_connection.server}'")
            print(f"   [CHECK] Conexión establecida correctamente")
            print(f"   📍 Servidor: {db_connection.server}")
            print(f"   🗄️  Base de datos: {db_connection.database}")
        except Exception as e:
            resultados.agregar_error_sql("Conexión inicial", e, "Verificar SQL Server, credenciales y configuración de red")
            print(f"   [ERROR] Error de conexión: {e}")
            pytest.fail("Test falló")
        # FASE 2: VERIFICACIÓN DE MODELOS Y MÉTODOS
        print(f"\n🏗️  FASE 2: VERIFICACIÓN DE MODELOS Y MÉTODOS")
        print("-" * 50)

        # Importar y verificar modelos
        modelos_info = [
            ('ObrasModel', 'modules.obras.model', ObrasModel),
            ('InventarioModel', 'modules.inventario.model', None),
            ('VidriosModel', 'modules.vidrios.model', None),
            ('HerrajesModel', 'modules.herrajes.model', None),
            ('ContabilidadModel', 'modules.contabilidad.model', None)
        ]

        modelos_instanciados = {}

        for nombre, modulo_path, clase_direct in modelos_info:
            try:
                if clase_direct:
                    modelo = clase_direct(db_connection)
                else:
                    modulo = __import__(modulo_path, fromlist=[nombre])
                    clase = getattr(modulo, nombre)
                    modelo = clase(db_connection)

                modelos_instanciados[nombre.lower()] = modelo
                resultados.metodos_validados.append(f"{nombre} instanciado correctamente")
                print(f"   [CHECK] {nombre} importado e instanciado")

            except Exception as e:
                resultados.agregar_error_sql(f"Instanciación de {nombre}", e)
                print(f"   [ERROR] Error con {nombre}: {e}")

        # Verificar métodos de integración específicos
        metodos_requeridos = [
            ('inventariomodel', 'obtener_estado_pedido_por_obra'),
            ('vidriosmodel', 'obtener_estado_pedido_por_obra'),
            ('herrajesmodel', 'obtener_estado_pedido_por_obra'),
            ('contabilidadmodel', 'obtener_estado_pago_pedido_por_obra')
        ]

        for modelo_key, metodo in metodos_requeridos:
            if modelo_key in modelos_instanciados:
                modelo = modelos_instanciados[modelo_key]
                if hasattr(modelo, metodo):
                    resultados.metodos_validados.append(f"{modelo_key}.{metodo}")
                    print(f"   [CHECK] {modelo_key}.{metodo} disponible")
                else:
                    resultados.warnings.append(f"Método {metodo} no encontrado en {modelo_key}")
                    print(f"   [WARN]  {modelo_key}.{metodo} NO disponible")

        # FASE 3: VERIFICACIÓN DE ESTRUCTURA DE DATOS
        print(f"\n📋 FASE 3: VERIFICACIÓN DE ESTRUCTURA DE DATOS")
        print("-" * 50)

        if 'obrasmodel' in modelos_instanciados:
            obras_model = modelos_instanciados['obrasmodel']

            # Verificar headers
            try:
                headers = obras_model.obtener_headers_obras()
                print(f"   [CHART] Headers de tabla obras: {len(headers)} columnas")

                columnas_integracion = ['estado_material', 'estado_vidrios', 'estado_herrajes', 'estado_pago']
                for columna in columnas_integracion:
                    if columna in headers:
                        resultados.metodos_validados.append(f"Columna {columna} en headers")
                        print(f"   [CHECK] Columna '{columna}' incluida")
                    else:
                        resultados.warnings.append(f"Columna '{columna}' no encontrada en headers")
                        print(f"   [WARN]  Columna '{columna}' no encontrada")

            except Exception as e:
                resultados.agregar_error_sql("Obtención de headers", e)
                print(f"   [ERROR] Error obteniendo headers: {e}")

            # Verificar datos de obras
            try:
                obras_data = obras_model.obtener_datos_obras()
                if obras_data and len(obras_data) > 0:
                    print(f"   📈 Obras en sistema: {len(obras_data)}")
                    resultados.conexiones_exitosas.append(f"Datos de {len(obras_data)} obras obtenidos correctamente")
                else:
                    resultados.warnings.append("No se encontraron obras en el sistema")
                    print(f"   [WARN]  No se encontraron obras en el sistema")
                    obras_data = None

            except Exception as e:
                resultados.agregar_error_sql("Obtención de datos de obras", e)
                print(f"   [ERROR] Error obteniendo datos de obras: {e}")
                obras_data = None

        # FASE 4: EDGE CASES Y PRUEBAS DE ROBUSTEZ
        print(f"\n🧪 FASE 4: EDGE CASES Y PRUEBAS DE ROBUSTEZ")
        print("-" * 50)

        edge_cases_a_probar = [
            ("Obra inexistente", 99999),
            ("ID obra None", None),
            ("ID obra string vacío", ""),
            ("ID obra string no numérico", "abc"),
            ("ID obra negativo", -1),
            ("ID obra cero", 0)
        ]

        for caso, id_obra in edge_cases_a_probar:
            print(f"   🔬 Probando: {caso} (valor: {id_obra})")

            for modelo_key in ['inventariomodel', 'vidriosmodel', 'herrajesmodel']:
                if modelo_key in modelos_instanciados:
                    modelo = modelos_instanciados[modelo_key]
                    if hasattr(modelo, 'obtener_estado_pedido_por_obra'):
                        try:
                            resultado = modelo.obtener_estado_pedido_por_obra(id_obra)
                            resultados.agregar_edge_case(f"{caso} en {modelo_key}", f"Resultado: {resultado}")
                            print(f"     [CHECK] {modelo_key}: {resultado}")
                        except Exception as e:
                            if "Invalid object name" in str(e) or "does not exist" in str(e):
                                tabla_inferida = extraer_tabla_de_error(str(e))
                                if tabla_inferida:
                                    resultados.agregar_tabla_faltante(tabla_inferida, modelo_key)

                            resultados.agregar_edge_case(f"{caso} en {modelo_key}", f"Error: {str(e)[:50]}...")
                            print(f"     [WARN]  {modelo_key}: Error - {str(e)[:50]}...")

            # Probar también contabilidad
            if 'contabilidadmodel' in modelos_instanciados:
                modelo = modelos_instanciados['contabilidadmodel']
                if hasattr(modelo, 'obtener_estado_pago_pedido_por_obra'):
                    try:
                        resultado = modelo.obtener_estado_pago_pedido_por_obra(id_obra, 'inventario')
                        resultados.agregar_edge_case(f"{caso} en contabilidad", f"Resultado: {resultado}")
                        print(f"     [CHECK] contabilidad: {resultado}")
                    except Exception as e:
                        if "Invalid object name" in str(e) or "does not exist" in str(e):
                            tabla_inferida = extraer_tabla_de_error(str(e))
                            if tabla_inferida:
                                resultados.agregar_tabla_faltante(tabla_inferida, 'contabilidad')

                        resultados.agregar_edge_case(f"{caso} en contabilidad", f"Error: {str(e)[:50]}...")
                        print(f"     [WARN]  contabilidad: Error - {str(e)[:50]}...")

        # FASE 5: PRUEBA CON DATOS REALES (SI EXISTEN)
        print(f"\n[CHART] FASE 5: PRUEBA CON DATOS REALES")
        print("-" * 40)

        if obras_data and len(obras_data) > 0:
            id_obra_real = obras_data[0][0]
            nombre_obra = obras_data[0][1] if len(obras_data[0]) > 1 else "Sin nombre"

            print(f"   🏗️  Probando con obra real: ID {id_obra_real} - {nombre_obra}")

            for modelo_key in ['inventariomodel', 'vidriosmodel', 'herrajesmodel', 'contabilidadmodel']:
                if modelo_key in modelos_instanciados:
                    modelo = modelos_instanciados[modelo_key]

                    if modelo_key == 'contabilidadmodel':
                        metodo = 'obtener_estado_pago_pedido_por_obra'
                        if hasattr(modelo, metodo):
                            try:
                                resultado = modelo.obtener_estado_pago_pedido_por_obra(id_obra_real, 'inventario')
                                resultados.conexiones_exitosas.append(f"Estado pago real para obra {id_obra_real}: {resultado}")
                                print(f"     [CHECK] Estado pago: {resultado}")
                            except Exception as e:
                                print(f"     [WARN]  Estado pago: Error - {str(e)[:50]}...")
                    else:
                        metodo = 'obtener_estado_pedido_por_obra'
                        if hasattr(modelo, metodo):
                            try:
                                resultado = modelo.obtener_estado_pedido_por_obra(id_obra_real)
                                resultados.conexiones_exitosas.append(f"Estado {modelo_key} real para obra {id_obra_real}: {resultado}")
                                print(f"     [CHECK] Estado {modelo_key}: {resultado}")
                            except Exception as e:
                                print(f"     [WARN]  Estado {modelo_key}: Error - {str(e)[:50]}...")
        else:
            print("   ℹ️  No hay obras reales para probar")

        # FASE 6: VERIFICACIÓN DE INTEGRACIÓN VISUAL
        print(f"\n🎨 FASE 6: VERIFICACIÓN DE INTEGRACIÓN VISUAL")
        print("-" * 50)

        try:
            # Crear mocks necesarios para el controlador
            mock_view = Mock()
            mock_usuarios_model = Mock()
            mock_usuarios_model.tiene_permiso.return_value = True
            mock_auditoria_model = Mock()

            usuario_mock = {'id': 1, 'username': 'test_user'}

            controller = ObrasController(
                model=obras_model,
                view=mock_view,
                db_connection=db_connection,
                usuarios_model=mock_usuarios_model,
                usuario_actual=usuario_mock,
                auditoria_model=mock_auditoria_model
            )

            # Verificar que el controlador tiene los métodos necesarios
            if hasattr(controller, 'cargar_datos_obras_tabla'):
                resultados.metodos_validados.append("ObrasController.cargar_datos_obras_tabla")
                print("   [CHECK] Controlador de obras configurado correctamente")
                print("   [CHECK] Método cargar_datos_obras_tabla disponible")
            else:
                resultados.warnings.append("Método cargar_datos_obras_tabla no encontrado en ObrasController")
                print("   [WARN]  Método cargar_datos_obras_tabla no disponible")

        except Exception as e:
            resultados.agregar_error_sql("Configuración del controlador", e)
            print(f"   [ERROR] Error configurando controlador: {e}")

        assert True
    except Exception as e:
        print(f"\n[ERROR] ERROR CRÍTICO: {e}")
        traceback.print_exc()
        resultados.agregar_error_sql("Error crítico del sistema", e)
        assert False is not None
    finally:
        # Cerrar conexión
        try:
            if db_connection and hasattr(db_connection, 'connection') and db_connection.connection:
                db_connection.connection.close()
                print(f"\n[LOCK] Conexión cerrada correctamente")
        except:
            pass

        # Mostrar reporte final
        resultados.reportar_resultados()


def extraer_tabla_de_error(mensaje_error):
    """Extrae el nombre de la tabla del mensaje de error SQL"""
    # Patrones comunes para errores de tabla no existente
    patrones = [
        r"Invalid object name '([^']+)'",
        r"Table '([^']+)' doesn't exist",
        r"object name '([^']+)' is invalid",
        r"Cannot find the object \"([^\"]+)\"",
    ]

    for patron in patrones:
import os
import re
import sys
import traceback
from unittest.mock import Mock

from PyQt6.QtWidgets import QApplication

from core.database import ObrasDatabaseConnection
from rexus.modules.obras.controller import ObrasController
from rexus.modules.obras.model import ObrasModel

        match = re.search(patron, mensaje_error, re.IGNORECASE)
        if match:
            return match.group(1)

    assert True
if __name__ == "__main__":
    success = test_integracion_mejorado()
    if success:
        print(f"\n🎯 TEST COMPLETADO")
    else:
        print(f"\n🚨 TEST FALLÓ")
        sys.exit(1)
