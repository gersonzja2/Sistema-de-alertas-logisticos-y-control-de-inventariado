import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db
import models

# Configuración de base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_logistica.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Limpiar tablas antes de cada test
    db.query(models.Producto).delete()
    db.query(models.RegistroAlerta).delete()
    db.commit()
    db.close()
    yield
    # Destruir tablas después de cada test
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sobrescribir dependencia get_db
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_ingreso_producto_nuevo():
    response = client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": 20})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "Nuevo stock: 20" in response.json()["mensaje"]
    
    # Verificar en dashboard
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.json()["total_productos"] == 1
    assert response.json()["productos_criticos"] == 0

def test_ingreso_producto_existente():
    # Primer ingreso
    client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": 10})
    # Segundo ingreso
    response = client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": 15})
    assert response.status_code == 200
    assert "Nuevo stock: 25" in response.json()["mensaje"]

def test_salida_exitosa():
    client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": 20})
    response = client.post("/api/salida", json={"sku": "SKU-TEST-1", "cantidad": 5})
    assert response.status_code == 200
    assert "Stock restante: 15" in response.json()["mensaje"]

def test_salida_insuficiente_o_inexistente():
    # Producto no existente
    response = client.post("/api/salida", json={"sku": "SKU-TEST-1", "cantidad": 5})
    assert response.status_code == 400
    assert "Stock insuficiente o producto no encontrado" in response.json()["detail"]

    # Stock insuficiente
    client.post("/api/ingreso", json={"sku": "SKU-TEST-2", "cantidad": 10})
    response = client.post("/api/salida", json={"sku": "SKU-TEST-2", "cantidad": 15})
    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]

def test_salida_alerta_stock_minimo(monkeypatch):
    # Mockear Resend para evitar peticiones externas en test
    class MockEmails:
        @staticmethod
        def send(data):
            return {"id": "mock_id"}
    monkeypatch.setattr("resend.Emails", MockEmails)

    # El stock mínimo por defecto es 10.
    # Ingresamos 12 unidades.
    client.post("/api/ingreso", json={"sku": "SKU-CRITICO", "cantidad": 12})
    
    # Retiramos 3 unidades. Quedan 9 (lo cual es <= 10).
    response = client.post("/api/salida", json={"sku": "SKU-CRITICO", "cantidad": 3})
    assert response.status_code == 200
    
    # Verificar que el dashboard reporte 1 producto crítico y la alerta correspondiente
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.json()["productos_criticos"] == 1
    assert len(response.json()["alertas_recientes"]) == 1
    assert "El SKU SKU-CRITICO ha caído a 9 unidades" in response.json()["alertas_recientes"][0]["mensaje"]

def test_validaciones_cantidad_invalida():
    # Cantidad igual a cero
    response = client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": 0})
    assert response.status_code == 422
    
    # Cantidad negativa
    response = client.post("/api/ingreso", json={"sku": "SKU-TEST-1", "cantidad": -5})
    assert response.status_code == 422

    # Cantidad igual a cero en salida
    response = client.post("/api/salida", json={"sku": "SKU-TEST-1", "cantidad": 0})
    assert response.status_code == 422
