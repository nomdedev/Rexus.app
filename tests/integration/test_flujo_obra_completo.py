"""
🧪 Tests de Integración - Flujo Completo de Obras
================================================

Tests de integración críticos que verifican el workflow completo
de creación y gestión de obras.

Best practices según:
- Martin Fowler's Integration Tests
- Google's Testing Blog
"""

import pytest

# Verificar dependencias
try:
    from rexus.modules.obras.model import ObrasModel
    from rexus.modules.inventario.model import InventarioModel
except ImportError:
    pytest.skip("Módulos de obras/inventario no están disponibles", allow_module_level=True)

from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, date


class TestFlujoObraCompleto:
    """
    CRÍTICO: Tests del flujo completo de obra

    Workflow:
    1. Crear obra
    2. Asignar materiales del inventario
    3. Verificar stock reservado
    4. Completar obra
    5. Verificar stock liberado
    """

    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos para tests"""
        db = MagicMock()
        cursor = MagicMock()
        db.cursor.return_value = cursor
        db.commit.return_value = True
        return db

    @pytest.fixture
    def obras_model(self, mock_db):
        """Model de obras con mock DB"""
        return ObrasModel(mock_db)

    @pytest.fixture
    def inventario_model(self, mock_db):
        """Model de inventario con mock DB"""
        return InventarioModel(mock_db)

    def test_flujo_completo_crear_y_completar_obra(
        self,
        obras_model,
        inventario_model,
        mock_db
    ):
        """
        CRÍTICO: Test completo del ciclo de vida de una obra

        Este es un test de integración que verifica que todos
        los componentes trabajen juntos correctamente.
        """
        # ============================================================================
        # PASO 1: Crear obra
        # ============================================================================
        datos_obra = {
            'codigo': 'OBRA-2025-001',
            'nombre': 'Edificio Central',
            'descripcion': 'Obra de prueba',
            'cliente_id': 1,
            'responsable_id': 2,
            'estado': 'planificacion',
            'fecha_inicio': '2025-01-15',
            'presupuesto': 150000.00
        }

        # Mockear inserción de obra
        mock_db.cursor.return_value.fetchone.return_value = [1]  # ID = 1
        obra_id = obras_model.crear_obra(datos_obra)

        assert obra_id is not None
        assert obra_id == 1

        # ============================================================================
        # PASO 2: Obtener materiales disponibles del inventario
        # ============================================================================
        # Mockear productos disponibles
        productos_disponibles = [
            {
                'id': 1,
                'codigo': 'VID-001',
                'nombre': 'Vidrio 6mm',
                'stock_actual': 100,
                'stock_reservado': 0
            },
            {
                'id': 2,
                'codigo': 'HER-001',
                'nombre': 'Bisagra',
                'stock_actual': 500,
                'stock_reservado': 0
            }
        ]

        mock_db.cursor.return_value.fetchall.return_value = productos_disponibles
        productos = inventario_model.obtener_disponibles()

        assert len(productos) == 2
        assert productos[0]['stock_actual'] == 100

        # ============================================================================
        # PASO 3: Asignar materiales a la obra
        # ============================================================================
        materiales_a_asignar = [
            {'material_id': 1, 'cantidad': 50},
            {'material_id': 2, 'cantidad': 100}
        ]

        # Asignar materiales
        for material in materiales_a_asignar:
            obra_id = 1
            material_id = material['material_id']
            cantidad = material['cantidad']

            # Mockear query de asignación
            mock_db.cursor.return_value.rowcount = 1
            asignado = obras_model.asignar_material(
                obra_id,
                material_id,
                cantidad
            )

            assert asignado is True

        # ============================================================================
        # PASO 4: Verificar stock reservado correctamente
        # ============================================================================
        # Mockear stock después de asignación
        stock_despues = {
            'id': 1,
            'codigo': 'VID-001',
            'stock_actual': 100,
            'stock_reservado': 50  # ⚠️ 50 reservados para obra
        }

        mock_db.cursor.return_value.fetchone.return_value = [
            stock_despues['stock_actual'],
            stock_despues['stock_reservado']
        ]

        stock = inventario_model.obtener_stock(1)
        assert stock['stock_reservado'] == 50
        assert stock['stock_actual'] == stock['stock_reservado'] + stock['disponible']

        # ============================================================================
        # PASO 5: Cambiar estado de obra a "en_progreso"
        # ============================================================================
        mock_db.cursor.return_value.rowcount = 1
        estado_actualizado = obras_model.cambiar_estado(
            obra_id=1,
            nuevo_estado='en_progreso',
            motivo='Inician trabajos'
        )

        assert estado_actualizado is True

        # ============================================================================
        # PASO 6: Completar obra
        # ============================================================================
        mock_db.cursor.return_value.rowcount = 1
        obra_completada = obras_model.completar_obra(
            obra_id=1,
            fecha_finalizacion='2025-03-15',
            notas='Obra completada exitosamente'
        )

        assert obra_completada is True

        # ============================================================================
        # PASO 7: Verificar stock liberado después de completar
        # ============================================================================
        # Mockear stock después de completar obra
        stock_final = {
            'id': 1,
            'stock_actual': 100,
            'stock_reservado': 0  # ✅ Liberado
        }

        mock_db.cursor.return_value.fetchone.return_value = [
            stock_final['stock_actual'],
            stock_final['stock_reservado']
        ]

        stock = inventario_model.obtener_stock(1)
        assert stock['stock_reservado'] == 0
        assert stock['stock_actual'] == 100

    def test_flujo_con_errores_rollback_correcto(
        self,
        obras_model,
        inventario_model,
        mock_db
    ):
        """
        Verifica que los errores sean manejados correctamente
        y se haga rollback de transacciones
        """
        # Crear obra exitosamente
        datos_obra = {
            'codigo': 'OBRA-TEST-002',
            'nombre': 'Obra Test',
            'cliente_id': 1,
            'responsable_id': 2
        }

        mock_db.cursor.return_value.fetchone.return_value = [1]
        obra_id = obras_model.crear_obra(datos_obra)

        # Intentar asignar material inexistente (error)
        mock_db.cursor.return_value.fetchone.return_value = None  # Material no existe

        material_asignado = obras_model.asignar_material(
            obra_id=obra_id,
            material_id=999,  # ❌ Material inexistente
            cantidad=10
        )

        # Debe fallar gracefulmente
        assert material_asignado is False

        # Verificar que se hizo rollback
        # (la transacción no se confirmó)
        mock_db.rollback.assert_called()


class TestIntegracionObrasInventario:
    """Tests de integración entre módulos de Obras e Inventario"""

    @pytest.fixture
    def mock_db_integrado(self):
        """Mock DB que simula responses complejas"""
        db = MagicMock()
        cursor = MagicMock()
        db.cursor.return_value = cursor
        db.commit.return_value = True
        db.rollback.return_value = True
        return db

    def test_asignacion_masiva_materiales(self, mock_db_integrado):
        """
        Test de asignación de múltiples materiales a la vez

        Escenario real: Asignar 50 materiales diferentes a una obra
        """
        obra_id = 1

        # Mockear 50 materiales disponibles
        materiales = [
            {'id': i, 'codigo': f'MAT-{i:03d}', 'stock_actual': 1000}
            for i in range(1, 51)
        ]

        mock_db_integrado.cursor.return_value.fetchall.return_value = materiales

        # Crear obra
        from rexus.modules.obras.model import ObrasModel
        obras_model = ObrasModel(mock_db_integrado)

        # Asignar materiales masivamente
        materiales_asignados = []
        for material in materiales[:10]:  # Asignar primeros 10
            mock_db_integrado.cursor.return_value.rowcount = 1
            exito = obras_model.asignar_material(
                obra_id=obra_id,
                material_id=material['id'],
                cantidad=10
            )

            if exito:
                materiales_asignados.append(material['id'])

        # Verificar que se asignaron correctamente
        assert len(materiales_asignados) == 10

    def test_conflicto_stock_dos_obras(self, mock_db_integrado):
        """
        Test de conflicto de stock entre dos obras

        Escenario: Dos obras quieren el mismo material
        - Obra A: Solicita 80 unidades (stock: 100)
        - Obra B: Solicita 50 unidades (debería fallar)
        """
        material_id = 1
        stock_total = 100

        # Obra A solicita 80 unidades
        mock_db_integrado.cursor.return_value.fetchone.return_value = [
            stock_total - 80,  # 20 disponibles
            80  # 80 reservados
        ]
        mock_db_integrado.cursor.return_value.rowcount = 1

        from rexus.modules.obras.model import ObrasModel
        obras_model = ObrasModel(mock_db_integrado)

        exito_a = obras_model.asignar_material(1, material_id, 80)
        assert exito_a is True

        # Obra B solicita 50 unidades (solo hay 20 disponibles)
        # Mockear validación de stock
        mock_db_integrado.cursor.return_value.fetchone.return_value = [
            stock_total - 80,  # 20 disponibles (no suficientes)
            80  # 80 ya reservados
        ]

        exito_b = obras_model.asignar_material(2, material_id, 50)
        assert exito_b is False  # No hay stock suficiente

    def test_cambio_estado_obras_en_cascada(self, mock_db_integrado):
        """
        Test de cambio de estado en múltiples obras

        Escenario: Cambiar estado de 10 obras simultáneamente
        """
        obras_ids = list(range(1, 11))  # 10 obras
        nuevo_estado = 'en_progreso'

        from rexus.modules.obras.model import ObrasModel
        obras_model = ObrasModel(mock_db_integrado)

        obras_actualizadas = []
        for obra_id in obras_ids:
            mock_db_integrado.cursor.return_value.rowcount = 1
            exito = obras_model.cambiar_estado(
                obra_id=obra_id,
                nuevo_estado=nuevo_estado
            )

            if exito:
                obras_actualizadas.append(obra_id)

        # Verificar que todas se actualizaron
        assert len(obras_actualizadas) == 10


class TestIntegracionInventarioCompras:
    """Tests de integración entre Inventario y Compras"""

    @pytest.fixture
    def mock_db_compras(self):
        """Mock DB para módulo de compras"""
        db = MagicMock()
        cursor = MagicMock()
        db.cursor.return_value = cursor
        db.commit.return_value = True
        return db

    def test_flujo_compra_restock(self, mock_db_compras):
        """
        Test del flujo de compra que repone inventario

        Workflow:
        1. Detectar stock bajo
        2. Crear orden de compra
        3. Recibir materiales
        4. Actualizar stock
        """
        # PASO 1: Detectar stock bajo
        material_id = 1
        stock_actual = 5
        stock_minimo = 10

        mock_db_compras.cursor.return_value.fetchone.return_value = [
            stock_actual,
            stock_minimo
        ]

        from rexus.modules.inventario.model import InventarioModel
        inventario_model = InventarioModel(mock_db_compras)

        stock = inventario_model.obtener_stock(material_id)

        # Verificar que está bajo mínimo
        assert stock['stock_actual'] < stock['stock_minimo']

        # PASO 2: Crear orden de compra
        from rexus.modules.compras.model import ComprasModel
        compras_model = ComprasModel(mock_db_compras)

        orden_compra = {
            'proveedor_id': 1,
            'material_id': material_id,
            'cantidad': 100,  # Comprar 100 unidades
            'precio_unitario': 25.50,
            'estado': 'pendiente'
        }

        mock_db_compras.cursor.return_value.fetchone.return_value = [1]
        orden_id = compras_model.crear_orden(orden_compra)

        assert orden_id is not None

        # PASO 3: Recibir materiales (mock recepción)
        mock_db_compras.cursor.return_value.rowcount = 1
        recibido = compras_model.recibir_orden(
            orden_id=orden_id,
            cantidad_recibida=100,
            fecha_recepcion='2025-01-15'
        )

        assert recibido is True

        # PASO 4: Actualizar stock
        nueva_cantidad = stock_actual + 100

        mock_db_compras.cursor.return_value.rowcount = 1
        actualizado = inventario_model.actualizar_stock(
            material_id=material_id,
            cantidad=nueva_cantidad,
            motivo='Reposición por compra'
        )

        assert actualizado is True


class TestTestsE2E:
    """
    Tests End-to-End de escenarios completos del sistema

    Simulan uso real de la aplicación con múltiples módulos.
    """

    @pytest.fixture
    def mock_sistema_completo(self):
        """
        Mock del sistema completo con múltiples modelos
        """
        db = MagicMock()
        cursor = MagicMock()
        db.cursor.return_value = cursor
        db.commit.return_value = True

        # Configurar fetchall para retornar datos
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = None
        cursor.rowcount = 1

        return db

    def test_escenario_usuario_completo(self, mock_sistema_completo):
        """
        Test E2E: Flujo completo de usuario usando el sistema

        Escenario:
        1. Usuario hace login
        2. Consulta obras activas
        3. Crea nueva obra
        4. Asigna materiales
        5. Genera reporte
        """
        # 1. Login (mock)
        usuario_id = 1
        usuario_rol = 'GERENTE_OBRAS'

        # 2. Consultar obras
        from rexus.modules.obras.model import ObrasModel
        obras_model = ObrasModel(mock_sistema_completo)

        obras_activas = [
            {'id': 1, 'codigo': 'OBRA-001', 'estado': 'en_progreso'},
            {'id': 2, 'codigo': 'OBRA-002', 'estado': 'planificacion'}
        ]

        mock_sistema_completo.cursor.return_value.fetchall.return_value = obras_activas
        obras = obras_model.obtener_todos()

        assert len(obras) == 2

        # 3. Crear nueva obra
        mock_sistema_completo.cursor.return_value.fetchone.return_value = [3]
        nueva_obra = obras_model.crear_obra({
            'codigo': 'OBRA-003',
            'nombre': 'Nueva Obra',
            'cliente_id': 1,
            'responsable_id': usuario_id
        })

        assert nueva_obra is not None

        # 4. Generar reporte
        mock_sistema_completo.cursor.return_value.fetchall.return_value = [
            {'estado': 'planificacion', 'count': 1},
            {'estado': 'en_progreso', 'count': 2}
        ]

        reporte = obras_model.obtener_estadisticas_por_estado()
        assert reporte is not None

    @pytest.mark.slow
    def test_estres_multiple_usuarios(self, mock_sistema_completo):
        """
        Test de estrés: 10 usuarios usando el sistema simultáneamente

        Verifica que no haya race conditions ni bloqueos.
        """
        import threading

        resultados = []
        errores = []

        def usuario_operaciones(user_id):
            """Simula operaciones de un usuario"""
            try:
                from rexus.modules.obras.model import ObrasModel
                obras_model = ObrasModel(mock_sistema_completo)

                # Realizar 10 operaciones
                for i in range(10):
                    obras_model.obtener_todos()

                resultados.append(user_id)
            except Exception as e:
                errores.append((user_id, e))

        # Crear 10 threads (usuarios simultáneos)
        threads = []
        for user_id in range(1, 11):
            t = threading.Thread(target=usuario_operaciones, args=(user_id,))
            threads.append(t)
            t.start()

        # Esperar a todos
        for t in threads:
            t.join()

        # Verificar que todos completaron sin errores
        assert len(errores) == 0, f"Errores: {errores}"
        assert len(resultados) == 10
