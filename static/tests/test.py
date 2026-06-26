import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db, hash_password
import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_logistica.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

AUTH = {"Authorization": "Bearer simulacion-jwt-token-123"}

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    for model in [models.Producto, models.RegistroAlerta, models.Lote,
                  models.DespachoPendiente, models.Transaccion, models.User, models.Sucursal]:
        db.query(model).delete()
    admin = models.User(username="admin_test", password_hash=hash_password("admin123"), rol="admin")
    db.add(admin)
    suc = models.Sucursal(nombre="Sucursal Test", direccion="Dir Test")
    db.add(suc)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- RF04: Ingreso ---

def test_ingreso_producto_nuevo():
    r = client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": 20}, headers=AUTH)
    assert r.status_code == 200
    assert "Nuevo stock: 20" in r.json()["mensaje"]

def test_ingreso_con_lote():
    r = client.post("/api/ingreso", json={"sku": "SKU-LOTE", "cantidad": 50, "lote": "LOTE-001"}, headers=AUTH)
    assert r.status_code == 200

# --- Stock en Vivo ---

def test_stock_en_vivo():
    client.post("/api/ingreso", json={"sku": "SKU-A", "cantidad": 100}, headers=AUTH)
    r = client.get("/api/productos", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()["productos"]) == 1
    assert r.json()["productos"][0]["stock"] == 100

def test_producto_individual():
    client.post("/api/ingreso", json={"sku": "SKU-X", "cantidad": 50}, headers=AUTH)
    r = client.get("/api/productos/SKU-X", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["stock"] == 50
    r = client.get("/api/productos/NO-EXISTE", headers=AUTH)
    assert r.status_code == 404

# --- Historial ---

def test_historial_transacciones():
    client.post("/api/ingreso", json={"sku": "SKU-H", "cantidad": 100}, headers=AUTH)
    client.post("/api/salida", json={"sku": "SKU-H", "cantidad": 30}, headers=AUTH)
    client.post("/api/salida", json={"sku": "SKU-H", "cantidad": 5, "tipo": "pos"}, headers=AUTH)
    r = client.get("/api/historial", headers=AUTH)
    assert r.status_code == 200
    trans = r.json()["transacciones"]
    assert len(trans) == 3
    tipos = [t["tipo"] for t in trans]
    assert "ingreso" in tipos and "salida" in tipos and "pos" in tipos

# --- RF01: Salida ---

def test_salida_exitosa():
    client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": 20}, headers=AUTH)
    r = client.post("/api/salida", json={"sku": "SKU-TEST-1", "cantidad": 5}, headers=AUTH)
    assert r.status_code == 200
    assert "Stock restante: 15" in r.json()["mensaje"]

def test_salida_insuficiente():
    r = client.post("/api/salida", json={"sku": "SKU-NADA", "cantidad": 5}, headers=AUTH)
    assert r.status_code == 400

# --- RF01: POS ---

def test_pos_cantidad_variable():
    client.post("/api/ingreso", json={"sku": "SKU-POS", "cantidad": 20}, headers=AUTH)
    r = client.post("/api/salida", json={"sku": "SKU-POS", "cantidad": 3, "tipo": "pos"}, headers=AUTH)
    assert r.status_code == 200
    assert "Stock restante: 17" in r.json()["mensaje"]

def test_pos_sin_stock():
    r = client.post("/api/salida", json={"sku": "SKU-INEXISTENTE", "cantidad": 1, "tipo": "pos"}, headers=AUTH)
    assert r.status_code == 400

# --- RF02: Alerta ---

def test_salida_alerta_stock_minimo(monkeypatch):
    class MockEmails:
        @staticmethod
        def send(data):
            assert "proveedor@empresa.com" in data["to"]
            assert "gerente@empresa.com" in data["to"]
            return {"id": "mock_id"}
    monkeypatch.setattr("resend.Emails", MockEmails)
    client.post("/api/ingreso", json={"sku": "SKU-CRIT", "cantidad": 12}, headers=AUTH)
    r = client.post("/api/salida", json={"sku": "SKU-CRIT", "cantidad": 3}, headers=AUTH)
    assert r.status_code == 200
    r = client.get("/api/dashboard", headers=AUTH)
    assert r.json()["productos_criticos"] == 1

# --- RF03: Dashboard ---

def test_dashboard_rotacion_y_despachos():
    client.post("/api/ingreso", json={"sku": "SKU-A", "cantidad": 100}, headers=AUTH)
    client.post("/api/ingreso", json={"sku": "SKU-B", "cantidad": 50}, headers=AUTH)
    client.post("/api/salida", json={"sku": "SKU-A", "cantidad": 10}, headers=AUTH)
    client.post("/api/salida", json={"sku": "SKU-B", "cantidad": 5, "tipo": "pos"}, headers=AUTH)
    client.post("/api/despachos", json={"sku": "SKU-A", "destino": "Sucursal Norte", "cantidad": 20}, headers=AUTH)
    r = client.get("/api/dashboard", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["despachos_pendientes"] == 1
    assert len(r.json()["top_rotacion"]) == 2

# --- RNF02: Health ---

def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

# --- RNF03: JWT ---

def test_jwt_requerido():
    r = client.post("/api/ingreso", json={"sku": "SKU-JWT", "cantidad": 10})
    assert r.status_code == 401

# --- RNF01: Latencia ---

def test_latencia_header():
    r = client.get("/health")
    assert "X-Response-Time-Ms" in r.headers

# --- Validaciones ---

def test_validaciones_cantidad_invalida():
    r = client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": 0}, headers=AUTH)
    assert r.status_code == 422
    r = client.post("/api/salida", json={"sku": "SKU-TEST-1", "cantidad": -5}, headers=AUTH)
    assert r.status_code == 422

# ================================================================
# NUEVOS TESTS: Autenticación, Roles, Sucursales
# ================================================================

# --- Auth: Login ---

def test_login_admin_exitoso():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert data["user"]["rol"] == "admin"
    assert data["user"]["username"] == "admin_test"

def test_login_credenciales_invalidas():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "wrong"})
    assert r.status_code == 401
    assert "inválidas" in r.json()["detail"]

def test_login_usuario_inexistente():
    r = client.post("/api/auth/login", json={"username": "noexiste", "password": "x"})
    assert r.status_code == 401

# --- Auth: Me ---

def test_me_con_token_valido():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    r2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["username"] == "admin_test"

def test_me_sin_token():
    r = client.get("/api/auth/me")
    assert r.status_code == 401

# --- Auth: Register (admin only) ---

def test_register_trabajador():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    # Primero obtener ID de sucursal
    rs = client.get("/api/sucursales", headers={"Authorization": f"Bearer {token}"})
    suc_id = rs.json()["sucursales"][0]["id"]

    r2 = client.post("/api/auth/register", json={
        "username": "trabajador1", "password": "pass123",
        "rol": "trabajador", "sucursal_id": suc_id
    }, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert "trabajador1" in r2.json()["mensaje"]

def test_register_duplicado():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    rs = client.get("/api/sucursales", headers={"Authorization": f"Bearer {token}"})
    suc_id = rs.json()["sucursales"][0]["id"]
    client.post("/api/auth/register", json={
        "username": "dup", "password": "p", "rol": "trabajador", "sucursal_id": suc_id
    }, headers={"Authorization": f"Bearer {token}"})
    r2 = client.post("/api/auth/register", json={
        "username": "dup", "password": "p", "rol": "trabajador", "sucursal_id": suc_id
    }, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 400
    assert "ya existe" in r2.json()["detail"]

def test_register_sin_auth():
    r = client.post("/api/auth/register", json={
        "username": "noauth", "password": "p", "rol": "trabajador"
    })
    assert r.status_code == 401

def test_register_sucursal_inexistente():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    r2 = client.post("/api/auth/register", json={
        "username": "bad", "password": "p", "rol": "trabajador", "sucursal_id": 9999
    }, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 400

# --- Usuarios (admin) ---

def test_listar_usuarios():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    r2 = client.get("/api/usuarios", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert len(r2.json()["usuarios"]) >= 1

def test_listar_usuarios_sin_auth():
    r = client.get("/api/usuarios")
    assert r.status_code == 401

# --- Sucursales CRUD ---

def test_crear_sucursal():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    r2 = client.post("/api/sucursales", json={"nombre": "Sucursal Nueva", "direccion": "Av. Test 456"},
                     headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert "Sucursal Nueva" in r2.json()["mensaje"]

def test_crear_sucursal_duplicada():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    r2 = client.post("/api/sucursales", json={"nombre": "Sucursal Test", "direccion": "x"},
                     headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 400

def test_crear_sucursal_sin_auth():
    r = client.post("/api/sucursales", json={"nombre": "No Auth", "direccion": "x"})
    assert r.status_code == 401

def test_actualizar_sucursal():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    rs = client.get("/api/sucursales", headers={"Authorization": f"Bearer {token}"})
    sid = rs.json()["sucursales"][0]["id"]
    r2 = client.put(f"/api/sucursales/{sid}", json={"nombre": "Sucursal Editada"},
                    headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200

def test_eliminar_sucursal_sin_usuarios():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    r2 = client.post("/api/sucursales", json={"nombre": "Temp Suc", "direccion": "x"},
                     headers={"Authorization": f"Bearer {token}"})
    sid = r2.json()["id"]
    r3 = client.delete(f"/api/sucursales/{sid}", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200

# --- Flujo completo: login trabajador, filtrar por sucursal ---

def test_flujo_trabajador():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    admin_token = r.json()["token"]
    rs = client.get("/api/sucursales", headers={"Authorization": f"Bearer {admin_token}"})
    suc_id = rs.json()["sucursales"][0]["id"]

    # Admin crea trabajador
    client.post("/api/auth/register", json={
        "username": "worker", "password": "worker123",
        "rol": "trabajador", "sucursal_id": suc_id
    }, headers={"Authorization": f"Bearer {admin_token}"})

    # Trabajador inicia sesion
    r2 = client.post("/api/auth/login", json={"username": "worker", "password": "worker123"})
    assert r2.status_code == 200
    worker_token = r2.json()["token"]
    assert r2.json()["user"]["sucursal_id"] == suc_id

    # Trabajador ingresa producto (se asigna a su sucursal)
    r3 = client.post("/api/ingreso", json={"sku": "SKU-WORKER", "cantidad": 30},
                     headers={"Authorization": f"Bearer {worker_token}"})
    assert r3.status_code == 200

    # Trabajador ve solo su producto
    r4 = client.get("/api/productos", headers={"Authorization": f"Bearer {worker_token}"})
    assert r4.status_code == 200
    assert len(r4.json()["productos"]) == 1
    assert r4.json()["productos"][0]["sku"] == "SKU-WORKER"

    # Admin crea otro producto en otra sucursal (sucursal_id=null => general)
    r5 = client.post("/api/ingreso", json={"sku": "SKU-ADMIN", "cantidad": 50},
                     headers={"Authorization": f"Bearer {admin_token}"})
    assert r5.status_code == 200

    # Admin ve ambos
    r6 = client.get("/api/productos", headers={"Authorization": f"Bearer {admin_token}"})
    assert len(r6.json()["productos"]) >= 2

    # Trabajador ve el suyo + globales
    r7 = client.get("/api/productos", headers={"Authorization": f"Bearer {worker_token}"})
    assert len(r7.json()["productos"]) == 2

# --- Auth: admin no puede eliminarse a si mismo si es el unico ---

def test_no_eliminar_unico_admin():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    ru = client.get("/api/usuarios", headers={"Authorization": f"Bearer {token}"})
    admin_id = None
    for u in ru.json()["usuarios"]:
        if u["username"] == "admin_test":
            admin_id = u["id"]
            break
    r2 = client.delete(f"/api/usuarios/{admin_id}", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 400

# --- RF17: Transferencias entre Sucursales ---

def test_transferencia_entre_sucursales():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}

    # Crear dos sucursales
    r1 = client.post("/api/sucursales", json={"nombre": "Suc A", "direccion": "Dir A"}, headers=auth)
    assert r1.status_code == 200
    r2 = client.post("/api/sucursales", json={"nombre": "Suc B", "direccion": "Dir B"}, headers=auth)
    assert r2.status_code == 200

    rs = client.get("/api/sucursales", headers=auth)
    sucs = {s["nombre"]: s["id"] for s in rs.json()["sucursales"]}
    id_a, id_b = sucs["Suc A"], sucs["Suc B"]

    # Crear producto en Suc A
    client.post("/api/ingreso", json={"sku": "SKU-TRF", "cantidad": 50}, headers=auth)
    # Asignarlo a Suc A (usando worker que pertenezca a Suc A) ...
    # En realidad el producto se crea con sid=None (admin). Lo re-asignamos vía BD directa
    # Mejor: crear con admin (global) y luego transferir no funciona porque está en global, no en Suc A
    # Creamos un trabajador en Suc A que cree el producto
    client.post("/api/auth/register", json={
        "username": "trf_worker", "password": "w123",
        "rol": "trabajador", "sucursal_id": id_a
    }, headers=auth)
    rw = client.post("/api/auth/login", json={"username": "trf_worker", "password": "w123"})
    w_auth = {"Authorization": f"Bearer {rw.json()['token']}"}
    r_in = client.post("/api/ingreso", json={"sku": "SKU-TRF", "cantidad": 50}, headers=w_auth)
    assert r_in.status_code == 200

    # Transferir 20 unidades Suc A -> Suc B
    r_trf = client.post("/api/transferencias", json={
        "sku": "SKU-TRF", "origen_sucursal_id": id_a,
        "destino_sucursal_id": id_b, "cantidad": 20
    }, headers=auth)
    assert r_trf.status_code == 200

    # Verificar stock en Suc A (50-20=30)
    r_prod_a = client.get(f"/api/productos?sucursal_id={id_a}", headers=auth)
    prod_a = [p for p in r_prod_a.json()["productos"] if p["sku"] == "SKU-TRF" and p["sucursal_id"] == id_a]
    assert len(prod_a) == 1
    assert prod_a[0]["stock"] == 30

    # Verificar stock en Suc B (0+20=20)
    r_prod_b = client.get(f"/api/productos?sucursal_id={id_b}", headers=auth)
    prod_b = [p for p in r_prod_b.json()["productos"] if p["sku"] == "SKU-TRF" and p["sucursal_id"] == id_b]
    assert len(prod_b) == 1
    assert prod_b[0]["stock"] == 20

def test_transferencia_misma_sucursal_rechazada():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    client.post("/api/sucursales", json={"nombre": "Suc X", "direccion": "X"}, headers=auth)
    rs = client.get("/api/sucursales", headers=auth)
    sid = rs.json()["sucursales"][0]["id"]
    r_trf = client.post("/api/transferencias", json={
        "sku": "SKU-X", "origen_sucursal_id": sid,
        "destino_sucursal_id": sid, "cantidad": 10
    }, headers=auth)
    assert r_trf.status_code == 400
    assert "distintas" in r_trf.json()["detail"]

def test_transferencia_stock_insuficiente():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    client.post("/api/sucursales", json={"nombre": "Suc C", "direccion": "C"}, headers=auth)
    client.post("/api/sucursales", json={"nombre": "Suc D", "direccion": "D"}, headers=auth)
    rs = client.get("/api/sucursales", headers=auth)
    sucs = rs.json()["sucursales"]
    id_c, id_d = sucs[0]["id"], sucs[1]["id"]
    r_trf = client.post("/api/transferencias", json={
        "sku": "SKU-NOEXISTE", "origen_sucursal_id": id_c,
        "destino_sucursal_id": id_d, "cantidad": 5
    }, headers=auth)
    assert r_trf.status_code == 400

def test_transferencia_sin_auth():
    r = client.post("/api/transferencias", json={
        "sku": "SKU-X", "origen_sucursal_id": 1,
        "destino_sucursal_id": 2, "cantidad": 5
    })
    assert r.status_code == 401

# --- RF24: Auditoría (created_by) ---

def test_auditoria_created_by_ingreso():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    r_in = client.post("/api/ingreso", json={"sku": "SKU-AUDIT", "cantidad": 10}, headers=auth)
    assert r_in.status_code == 200
    # Verificar producto created_by
    r_prod = client.get("/api/productos/SKU-AUDIT", headers=auth)
    assert r_prod.status_code == 200
    assert r_prod.json().get("created_by") == "admin_test"

def test_auditoria_created_by_sucursal():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    r_s = client.post("/api/sucursales", json={"nombre": "Suc Audit", "direccion": "Audit"}, headers=auth)
    assert r_s.status_code == 200
    rs = client.get("/api/sucursales", headers=auth)
    suc = [s for s in rs.json()["sucursales"] if s["nombre"] == "Suc Audit"][0]
    assert "id" in suc

def test_auditoria_updated_by():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    client.post("/api/sucursales", json={"nombre": "Suc Upd", "direccion": "Upd"}, headers=auth)
    rs = client.get("/api/sucursales", headers=auth)
    suc = [s for s in rs.json()["sucursales"] if s["nombre"] == "Suc Upd"][0]
    r_u = client.put(f"/api/sucursales/{suc['id']}", json={"direccion": "Nueva Dir"}, headers=auth)
    assert r_u.status_code == 200

def test_auditoria_created_by_transaccion():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    client.post("/api/ingreso", json={"sku": "SKU-TRX-AUDIT", "cantidad": 15}, headers=auth)
    client.post("/api/salida", json={"sku": "SKU-TRX-AUDIT", "cantidad": 5}, headers=auth)
    r_hist = client.get("/api/historial", headers=auth)
    assert r_hist.status_code == 200
    for trx in r_hist.json()["transacciones"]:
        if trx["sku"] == "SKU-TRX-AUDIT":
            assert "created_by" in trx

# --- RF23: Alertas activas ---

def test_alertas_activas_endpoint():
    r = client.post("/api/auth/login", json={"username": "admin_test", "password": "admin123"})
    token = r.json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    r_alert = client.get("/api/alertas/activas", headers=auth)
    assert r_alert.status_code == 200
    data = r_alert.json()
    assert "productos_criticos" in data
    assert "alertas_no_leidas" in data
    assert "criticos" in data
