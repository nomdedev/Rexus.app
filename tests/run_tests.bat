@echo off
echo === EJECUTANDO TESTS ===
cd /d "c:\Users\Oficina\Documents\Proyectos\stock.app"

echo.
echo 1. Test basico de Python:
python -c "print('Python funcionando')"

echo.
echo 2. Test de pytest:
python -c "import pytest; print('pytest disponible')"

echo.
echo 3. Test de imports:
python -c "from tests.test_pedidos_controller import DummyModel; print('Imports OK')"

echo.
echo 4. Test simple de pedidos:
python -c "from tests.test_pedidos_controller import DummyModel; m = DummyModel(); print('Pedido:', m.generar_pedido(1))"

echo.
echo 5. Ejecutar pytest simple:
python -m pytest tests/test_pedidos_controller.py::test_generar_pedido_con_faltantes -v

echo.
echo === TESTS COMPLETADOS ===
pause
