class DummyModel:
    def __init__(self):
import pytest

from modules.usuarios import controller as usuarios_controller
from unittest.mock import MagicMock, patch
        self.usuarios = []
    def crear_usuario(self, username, password, rol):
        if any(u["username"] == username for u in self.usuarios):
            raise ValueError("Usuario duplicado")
        if username == "TEST_USER":
            raise ValueError("No se puede crear usuario de prueba")
        if len(password) < 8:
            raise ValueError("Password débil")
        usuario = {"id": len(self.usuarios)+1, "username": username, "rol": rol}
        self.usuarios.append(usuario)
        return usuario["id"]
    def editar_usuario(self, id_usuario, datos):
        for u in self.usuarios:
            if u["id"] == id_usuario:
                if u["username"] == "TEST_USER":
                    raise ValueError("No se puede editar admin")
                u.update(datos)
                return True
        raise ValueError("Usuario no encontrado")
    def eliminar_usuario(self, id_usuario):
        for u in self.usuarios:
            if u["id"] == id_usuario:
                if u["username"] == "TEST_USER":
                    raise ValueError("No se puede eliminar admin")
                self.usuarios.remove(u)
                return True
        raise ValueError("Usuario no encontrado")
    def login(self, username, password):
        for u in self.usuarios:
            if u["username"] == username:
                if password == "correcta":
                    return u
                else:
                    raise ValueError("Credenciales inválidas")
        raise ValueError("Usuario no encontrado")

class DummyView:
    def __init__(self):
        self.mensajes = []
    def mostrar_mensaje(self, mensaje, tipo=None, **kwargs):
        self.mensajes.append((mensaje, tipo))
    def refrescar_permisos(self):
        self.mensajes.append(("Permisos refrescados", "info"))

@pytest.fixture
def controller():
    model = DummyModel()
    view = DummyView()
    auditoria = MagicMock()
    usuario_actual = {"id": 1, "username": "testuser", "ip": "127.0.0.1"}
    controller = usuarios_controller.UsuariosController(model, view, None, usuario_actual)
    controller.auditoria_model = auditoria
    return controller

def test_crear_usuario_valido(controller):
    id_usuario = controller.crear_usuario("nuevo", "passwordfuerte", "operador")
    assert id_usuario == 1

def test_crear_usuario_duplicado(controller):
    controller.crear_usuario("nuevo", "passwordfuerte", "operador")
    with pytest.raises(ValueError):
        controller.crear_usuario("nuevo", "passwordfuerte", "operador")

def test_crear_usuario_test(controller):
    with pytest.raises(ValueError):
        controller.crear_usuario("TEST_USER", "passwordfuerte", "TEST_USER")

def test_crear_usuario_password_debil(controller):
    with pytest.raises(ValueError):
        controller.crear_usuario("otro", "123", "operador")

def test_editar_usuario(controller):
    id_usuario = controller.crear_usuario("nuevo", "passwordfuerte", "operador")
    controller.editar_usuario_test(id_usuario, {"rol": "TEST_USER"})
    assert controller.model.usuarios[0]["rol"] == "TEST_USER"

def test_editar_usuario_test(controller):
    controller.model.usuarios.append({"id": 99, "username": "TEST_USER", "rol": "TEST_USER"})
    with pytest.raises(ValueError):
        controller.editar_usuario_test(99, {"rol": "operador"})

def test_eliminar_usuario(controller):
    id_usuario = controller.crear_usuario("nuevo", "passwordfuerte", "operador")
    controller.eliminar_usuario(id_usuario)
    assert len(controller.model.usuarios) == 0

def test_eliminar_usuario_test(controller):
    controller.model.usuarios.append({"id": 99, "username": "TEST_USER", "rol": "TEST_USER"})
    with pytest.raises(ValueError):
        controller.eliminar_usuario(99)

def test_login_valido(controller):
    controller.crear_usuario("nuevo", "passwordfuerte", "operador")
    usuario = controller.login("nuevo", "correcta")
    assert usuario["username"] == "nuevo"

def test_login_invalido(controller):
    controller.crear_usuario("nuevo", "passwordfuerte", "operador")
    with pytest.raises(ValueError):
        controller.login("nuevo", "incorrecta")

def test_refresco_permisos_ui(controller):
    controller.view.refrescar_permisos()
    assert ("Permisos refrescados", "info") in controller.view.mensajes

def test_auditoria_en_creacion(controller):
    controller.crear_usuario("nuevo2", "passwordfuerte", "operador")
    assert controller.auditoria_model.registrar_evento.called

def test_auditoria_en_edicion(controller):
    id_usuario = controller.crear_usuario("nuevo3", "passwordfuerte", "operador")
    controller.editar_usuario(id_usuario, {"rol": "TEST_USER"})
    assert controller.auditoria_model.registrar_evento.called

def test_auditoria_en_eliminacion(controller):
    id_usuario = controller.crear_usuario("nuevo4", "passwordfuerte", "operador")
    controller.eliminar_usuario(id_usuario)
    assert controller.auditoria_model.registrar_evento.called
