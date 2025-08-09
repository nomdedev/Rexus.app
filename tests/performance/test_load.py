"""
Tests de Carga y Rendimiento para Rexus.app
Valida el comportamiento del sistema bajo alta carga y concurrencia

Ejecutar con: python -m pytest tests/performance/test_load.py -v
"""

import concurrent.futures
import hashlib
import os
import sqlite3
import statistics
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Agregar ruta al proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rexus.modules.inventario.model import InventarioModel
from rexus.modules.obras.model import ObrasModel
from rexus.modules.usuarios.model import UsuariosModel


class TestRendimiento:
    """Suite de tests de rendimiento y carga"""

    @pytest.fixture
    def db_connection(self):
        """Base de datos temporal para tests de rendimiento"""
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        db_file.close()

        connection = sqlite3.connect(db_file.name, check_same_thread=False)
        cursor = connection.cursor()

        # Crear tablas necesarias
        cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT,
            email TEXT UNIQUE,
            rol TEXT DEFAULT 'USER',
            activo INTEGER DEFAULT 1,
            intentos_fallidos INTEGER DEFAULT 0,
            ultimo_intento_fallido DATETIME,
            bloqueado_hasta DATETIME,
            configuracion_personal TEXT DEFAULT '{}'
        )
        """)

        cursor.execute("""
        CREATE TABLE inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER DEFAULT 0,
            precio DECIMAL(10,2) DEFAULT 0.00,
            categoria TEXT,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'PLANIFICADA',
            fecha_inicio DATE,
            fecha_fin DATE,
            presupuesto DECIMAL(12,2),
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Crear índices para mejorar rendimiento
        cursor.execute("CREATE INDEX idx_usuarios_usuario ON usuarios(usuario)")
        cursor.execute("CREATE INDEX idx_inventario_nombre ON inventario(nombre)")
        cursor.execute("CREATE INDEX idx_obras_estado ON obras(estado)")

        connection.commit()

        yield connection

        connection.close()
        os.unlink(db_file.name)

    @pytest.fixture
    def usuarios_model(self, db_connection):
        """Modelo de usuarios configurado para tests"""
        return UsuariosModel(db_connection)

    @pytest.fixture
    def inventario_model(self, db_connection):
        """Modelo de inventario configurado para tests"""
        return InventarioModel(db_connection)

    @pytest.fixture
    def obras_model(self, db_connection):
        """Modelo de obras configurado para tests"""
        return ObrasModel(db_connection)


class TestRendimientoUsuarios:
    """Tests de rendimiento del módulo de usuarios"""

    def test_creacion_masiva_usuarios(self, usuarios_model):
        """Test rendimiento creando múltiples usuarios"""
        num_usuarios = 100
        start_time = time.time()

        usuarios_creados = 0
        for i in range(num_usuarios):
            try:
                password_hash = hashlib.sha256(f"password{i}".encode()).hexdigest()
                cursor = usuarios_model.db_connection.cursor()
                cursor.execute(
                    """
                INSERT INTO usuarios (usuario, password_hash, nombre_completo, email)
                VALUES (?, ?, ?, ?)
                """,
                    (f"user{i}", password_hash, f"User {i}", f"user{i}@test.com"),
                )
                usuarios_model.db_connection.commit()
                usuarios_creados += 1
            except Exception as e:
                print(f"Error creando usuario {i}: {e}")

        end_time = time.time()
        tiempo_total = end_time - start_time

        print(f"\n[CHART] Creación de {usuarios_creados} usuarios:")
        print(f"   Tiempo total: {tiempo_total:.2f} segundos")
        print(f"   Usuarios por segundo: {usuarios_creados / tiempo_total:.2f}")

        # Debe crear al menos 50 usuarios por segundo
        assert usuarios_creados / tiempo_total >= 50, (
            "Rendimiento de creación muy lento"
        )

    def test_autenticacion_concurrente(self, usuarios_model):
        """Test autenticación concurrente de múltiples usuarios"""
        # Crear usuarios de prueba
        num_usuarios = 50
        for i in range(num_usuarios):
            password_hash = hashlib.sha256(f"password{i}".encode()).hexdigest()
            cursor = usuarios_model.db_connection.cursor()
            cursor.execute(
                """
            INSERT INTO usuarios (usuario, password_hash, nombre_completo, email)
            VALUES (?, ?, ?, ?)
            """,
                (f"testuser{i}", password_hash, f"Test User {i}", f"test{i}@test.com"),
            )
            usuarios_model.db_connection.commit()

        def autenticar_usuario(user_id):
            """Función para autenticar un usuario específico"""
            start = time.time()
            resultado = usuarios_model.autenticar_usuario_seguro(
                f"testuser{user_id}", f"password{user_id}"
            )
            end = time.time()
            return {
                "user_id": user_id,
                "success": resultado["success"],
                "time": end - start,
            }

        start_time = time.time()

        # Ejecutar autenticaciones concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(autenticar_usuario, i) for i in range(num_usuarios)
            ]
            resultados = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        end_time = time.time()
        tiempo_total = end_time - start_time

        # Analizar resultados
        autenticaciones_exitosas = sum(1 for r in resultados if r["success"])
        tiempos_respuesta = [r["time"] for r in resultados]
        tiempo_promedio = statistics.mean(tiempos_respuesta)
        tiempo_max = max(tiempos_respuesta)

        print(f"\n[CHART] Autenticación concurrente:")
        print(f"   Total de usuarios: {num_usuarios}")
        print(f"   Autenticaciones exitosas: {autenticaciones_exitosas}")
        print(f"   Tiempo total: {tiempo_total:.2f} segundos")
        print(f"   Tiempo promedio por auth: {tiempo_promedio:.3f} segundos")
        print(f"   Tiempo máximo: {tiempo_max:.3f} segundos")
        print(
            f"   Autenticaciones por segundo: {autenticaciones_exitosas / tiempo_total:.2f}"
        )

        # Verificaciones de rendimiento
        assert autenticaciones_exitosas >= num_usuarios * 0.95, (
            "Demasiadas autenticaciones fallidas"
        )
        assert tiempo_promedio < 0.1, "Tiempo de respuesta muy lento"
        assert tiempo_max < 0.5, "Tiempo máximo inaceptable"

    def test_consultas_masivas_usuarios(self, usuarios_model):
        """Test rendimiento en consultas masivas de usuarios"""
        # Crear usuarios de prueba
        num_usuarios = 200
        for i in range(num_usuarios):
            password_hash = hashlib.sha256(f"password{i}".encode()).hexdigest()
            cursor = usuarios_model.db_connection.cursor()
            cursor.execute(
                """
            INSERT INTO usuarios (usuario, password_hash, nombre_completo, email)
            VALUES (?, ?, ?, ?)
            """,
                (
                    f"queryuser{i}",
                    password_hash,
                    f"Query User {i}",
                    f"query{i}@test.com",
                ),
            )
            usuarios_model.db_connection.commit()

        # Test consultas individuales
        start_time = time.time()
        usuarios_encontrados = 0

        for i in range(0, num_usuarios, 10):  # Consultar cada 10 usuarios
            usuario = usuarios_model.obtener_usuario_por_nombre(f"queryuser{i}")
            if usuario:
                usuarios_encontrados += 1

        end_time = time.time()
        tiempo_consultas = end_time - start_time

        # Test obtener todos los usuarios
        start_time = time.time()
        todos_usuarios = usuarios_model.obtener_todos_usuarios()
        end_time = time.time()
        tiempo_todos = end_time - start_time

        print(f"\n[CHART] Consultas masivas de usuarios:")
        print(
            f"   Consultas individuales: {usuarios_encontrados} en {tiempo_consultas:.2f}s"
        )
        print(
            f"   Consultas por segundo: {usuarios_encontrados / tiempo_consultas:.2f}"
        )
        print(f"   Obtener todos ({len(todos_usuarios)} usuarios): {tiempo_todos:.2f}s")

        # Verificaciones
        assert usuarios_encontrados >= 15, "No se encontraron suficientes usuarios"
        assert tiempo_consultas < 2.0, "Consultas individuales muy lentas"
        assert tiempo_todos < 1.0, "Consulta masiva muy lenta"


class TestRendimientoInventario:
    """Tests de rendimiento del módulo de inventario"""

    def test_insercion_masiva_inventario(self, inventario_model):
        """Test rendimiento insertando múltiples productos"""
        num_productos = 500
        start_time = time.time()

        productos_creados = 0
        for i in range(num_productos):
            try:
                cursor = inventario_model.db_connection.cursor()
                cursor.execute(
                    """
                INSERT INTO inventario (nombre, descripcion, cantidad, precio, categoria)
                VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        f"Producto {i}",
                        f"Descripción del producto {i}",
                        i % 100,
                        round(10.0 + (i % 1000), 2),
                        f"Categoria{i % 10}",
                    ),
                )
                inventario_model.db_connection.commit()
                productos_creados += 1
            except Exception as e:
                print(f"Error creando producto {i}: {e}")

        end_time = time.time()
        tiempo_total = end_time - start_time

        print(f"\n[CHART] Inserción masiva de inventario:")
        print(f"   Productos creados: {productos_creados}")
        print(f"   Tiempo total: {tiempo_total:.2f} segundos")
        print(f"   Productos por segundo: {productos_creados / tiempo_total:.2f}")

        # Debe insertar al menos 100 productos por segundo
        assert productos_creados / tiempo_total >= 100, "Inserción muy lenta"

    def test_busqueda_concurrente_inventario(self, inventario_model):
        """Test búsquedas concurrentes en inventario"""
        # Crear productos de prueba
        num_productos = 100
        for i in range(num_productos):
            cursor = inventario_model.db_connection.cursor()
            cursor.execute(
                """
            INSERT INTO inventario (nombre, descripcion, cantidad, precio, categoria)
            VALUES (?, ?, ?, ?, ?)
            """,
                (
                    f"TestProd{i}",
                    f"Descripción {i}",
                    i % 50,
                    round(5.0 + i, 2),
                    f"Cat{i % 5}",
                ),
            )
            inventario_model.db_connection.commit()

        def buscar_producto(producto_id):
            """Función para buscar un producto específico"""
            start = time.time()
            cursor = inventario_model.db_connection.cursor()
            cursor.execute(
                "SELECT * FROM inventario WHERE nombre = ?", (f"TestProd{producto_id}",)
            )
            resultado = cursor.fetchone()
            end = time.time()
            return {
                "producto_id": producto_id,
                "found": resultado is not None,
                "time": end - start,
            }

        start_time = time.time()

        # Ejecutar búsquedas concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [
                executor.submit(buscar_producto, i) for i in range(0, num_productos, 2)
            ]
            resultados = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        end_time = time.time()
        tiempo_total = end_time - start_time

        # Analizar resultados
        productos_encontrados = sum(1 for r in resultados if r["found"])
        tiempos_busqueda = [r["time"] for r in resultados]
        tiempo_promedio = statistics.mean(tiempos_busqueda)

        print(f"\n[CHART] Búsqueda concurrente en inventario:")
        print(f"   Búsquedas realizadas: {len(resultados)}")
        print(f"   Productos encontrados: {productos_encontrados}")
        print(f"   Tiempo total: {tiempo_total:.2f} segundos")
        print(f"   Tiempo promedio por búsqueda: {tiempo_promedio:.3f} segundos")
        print(f"   Búsquedas por segundo: {len(resultados) / tiempo_total:.2f}")

        # Verificaciones
        assert productos_encontrados >= len(resultados) * 0.9, (
            "Muchos productos no encontrados"
        )
        assert tiempo_promedio < 0.05, "Búsquedas muy lentas"


class TestRendimientoObras:
    """Tests de rendimiento del módulo de obras"""

    def test_creacion_masiva_obras(self, obras_model):
        """Test rendimiento creando múltiples obras"""
        num_obras = 200
        start_time = time.time()

        obras_creadas = 0
        for i in range(num_obras):
            try:
                cursor = obras_model.db_connection.cursor()
                cursor.execute(
                    """
                INSERT INTO obras (nombre, descripcion, estado, presupuesto)
                VALUES (?, ?, ?, ?)
                """,
                    (
                        f"Obra {i}",
                        f"Descripción de la obra {i}",
                        "PLANIFICADA" if i % 2 == 0 else "EN_PROGRESO",
                        round(10000.0 + (i * 500), 2),
                    ),
                )
                obras_model.db_connection.commit()
                obras_creadas += 1
            except Exception as e:
                print(f"Error creando obra {i}: {e}")

        end_time = time.time()
        tiempo_total = end_time - start_time

        print(f"\n[CHART] Creación masiva de obras:")
        print(f"   Obras creadas: {obras_creadas}")
        print(f"   Tiempo total: {tiempo_total:.2f} segundos")
        print(f"   Obras por segundo: {obras_creadas / tiempo_total:.2f}")

        # Debe crear al menos 50 obras por segundo
        assert obras_creadas / tiempo_total >= 50, "Creación de obras muy lenta"


class TestRendimientoGeneral:
    """Tests de rendimiento general del sistema"""

    def test_operaciones_mixtas_concurrentes(
        self, usuarios_model, inventario_model, obras_model
    ):
        """Test operaciones mixtas concurrentes en todos los módulos"""
        # Preparar datos
        for i in range(20):
            # Usuarios
            password_hash = hashlib.sha256(f"pass{i}".encode()).hexdigest()
            cursor = usuarios_model.db_connection.cursor()
            cursor.execute(
                """
            INSERT INTO usuarios (usuario, password_hash, nombre_completo, email)
            VALUES (?, ?, ?, ?)
            """,
                (f"mixuser{i}", password_hash, f"Mix User {i}", f"mix{i}@test.com"),
            )
            usuarios_model.db_connection.commit()

            # Inventario
            cursor = inventario_model.db_connection.cursor()
            cursor.execute(
                """
            INSERT INTO inventario (nombre, descripcion, cantidad, precio)
            VALUES (?, ?, ?, ?)
            """,
                (f"MixProd{i}", f"Desc {i}", i * 2, 10.0 + i),
            )
            inventario_model.db_connection.commit()

            # Obras
            cursor = obras_model.db_connection.cursor()
            cursor.execute(
                """
            INSERT INTO obras (nombre, descripcion, estado, presupuesto)
            VALUES (?, ?, ?, ?)
            """,
                (f"MixObra{i}", f"Desc obra {i}", "PLANIFICADA", 5000.0 + i * 100),
            )
            obras_model.db_connection.commit()

        def operacion_usuario(user_id):
            """Operación de usuario (autenticación)"""
            return usuarios_model.autenticar_usuario_seguro(
                f"mixuser{user_id}", f"pass{user_id}"
            )

        def operacion_inventario(prod_id):
            """Operación de inventario (búsqueda)"""
            cursor = inventario_model.db_connection.cursor()
            cursor.execute(
                "SELECT * FROM inventario WHERE nombre = ?", (f"MixProd{prod_id}",)
            )
            return cursor.fetchone()

        def operacion_obra(obra_id):
            """Operación de obra (consulta)"""
            cursor = obras_model.db_connection.cursor()
            cursor.execute(
                "SELECT * FROM obras WHERE nombre = ?", (f"MixObra{obra_id}",)
            )
            return cursor.fetchone()

        start_time = time.time()

        # Ejecutar operaciones mixtas concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = []

            # Mezclar diferentes tipos de operaciones
            for i in range(15):
                futures.append(executor.submit(operacion_usuario, i % 20))
                futures.append(executor.submit(operacion_inventario, i % 20))
                futures.append(executor.submit(operacion_obra, i % 20))

            resultados = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        end_time = time.time()
        tiempo_total = end_time - start_time

        print(f"\n[CHART] Operaciones mixtas concurrentes:")
        print(f"   Total operaciones: {len(futures)}")
        print(f"   Tiempo total: {tiempo_total:.2f} segundos")
        print(f"   Operaciones por segundo: {len(futures) / tiempo_total:.2f}")

        # Verificaciones
        assert len(resultados) == len(futures), (
            "No se completaron todas las operaciones"
        )
        assert tiempo_total < 10.0, "Operaciones mixtas muy lentas"
        assert len(futures) / tiempo_total >= 10, "Throughput muy bajo"

    def test_stress_bajo_carga_sostenida(self, usuarios_model):
        """Test de estrés con carga sostenida"""
        duration_seconds = 10  # 10 segundos de carga sostenida
        operations_per_second = 20

        # Crear usuarios de prueba
        for i in range(50):
            password_hash = hashlib.sha256(f"stresspass{i}".encode()).hexdigest()
            cursor = usuarios_model.db_connection.cursor()
            cursor.execute(
                """
            INSERT INTO usuarios (usuario, password_hash, nombre_completo, email)
            VALUES (?, ?, ?, ?)
            """,
                (
                    f"stress{i}",
                    password_hash,
                    f"Stress User {i}",
                    f"stress{i}@test.com",
                ),
            )
            usuarios_model.db_connection.commit()

        resultados = []
        start_time = time.time()
        end_test_time = start_time + duration_seconds

        operation_count = 0
        while time.time() < end_test_time:
            cycle_start = time.time()

            # Realizar operaciones durante 1 segundo
            for _ in range(operations_per_second):
                if time.time() >= end_test_time:
                    break

                user_id = operation_count % 50
                op_start = time.time()

                try:
                    resultado = usuarios_model.autenticar_usuario_seguro(
                        f"stress{user_id}", f"stresspass{user_id}"
                    )
                    success = resultado["success"]
                except Exception as e:
                    success = False

                op_end = time.time()
                resultados.append(
                    {"success": success, "time": op_end - op_start, "timestamp": op_end}
                )
                operation_count += 1

            # Esperar hasta completar el segundo
            cycle_time = time.time() - cycle_start
            if cycle_time < 1.0:
                time.sleep(1.0 - cycle_time)

        test_duration = time.time() - start_time

        # Analizar resultados
        total_ops = len(resultados)
        successful_ops = sum(1 for r in resultados if r["success"])
        failed_ops = total_ops - successful_ops
        avg_response_time = statistics.mean([r["time"] for r in resultados])
        max_response_time = max([r["time"] for r in resultados])

        success_rate = (successful_ops / total_ops) * 100 if total_ops > 0 else 0
        actual_ops_per_second = total_ops / test_duration

        print(f"\n[CHART] Test de estrés - Carga sostenida:")
        print(f"   Duración: {test_duration:.1f} segundos")
        print(f"   Total operaciones: {total_ops}")
        print(f"   Operaciones exitosas: {successful_ops}")
        print(f"   Operaciones fallidas: {failed_ops}")
        print(f"   Tasa de éxito: {success_rate:.1f}%")
        print(f"   Ops/segundo objetivo: {operations_per_second}")
        print(f"   Ops/segundo real: {actual_ops_per_second:.1f}")
        print(f"   Tiempo respuesta promedio: {avg_response_time:.3f}s")
        print(f"   Tiempo respuesta máximo: {max_response_time:.3f}s")

        # Verificaciones de rendimiento bajo estrés
        assert success_rate >= 95.0, f"Tasa de éxito muy baja: {success_rate:.1f}%"
        assert avg_response_time < 0.1, (
            f"Tiempo de respuesta muy alto: {avg_response_time:.3f}s"
        )
        assert max_response_time < 0.5, (
            f"Tiempo máximo inaceptable: {max_response_time:.3f}s"
        )
        assert actual_ops_per_second >= operations_per_second * 0.8, (
            "Throughput muy bajo"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
