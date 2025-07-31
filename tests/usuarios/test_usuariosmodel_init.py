# --- TESTS DE USUARIOSMODEL INIT: USO SEGURO Y AISLADO, SIN CREDENCIALES REALES ---
# Este test no debe usar DatabaseConnection real. Se usa un mock para cumplir la política de aislamiento.
# --- FIN DE NOTA DE SEGURIDAD ---

class MockDBConnection:
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import pytest

from rexus.modules.usuarios.model import UsuariosModel
    pass

def test_usuariosmodel_init_requires_db_connection():
    with pytest.raises(TypeError):
        UsuariosModel()  # Debe fallar si no se pasa db_connection
    # Debe funcionar si se pasa un mock de db_connection
    db = MockDBConnection()
    model = UsuariosModel(db_connection=db)
    assert model is not None
