import os
from pathlib import Path
import resend
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database import engine, SessionLocal, Base
import models

# 1. Configuración de Rutas Absolutas (SOLUCIÓN al error TemplateNotFound)
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Inicializar Base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Motor API - Logística")

# 2. Montar estáticos y plantillas usando rutas absolutas
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Configuración de Resend
resend.api_key = os.getenv("RESEND_API_KEY", "re_tu_llave_de_prueba")

# Dependencia de Base de datos
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class TransaccionBodega(BaseModel):
    sku: str
    cantidad: int = Field(gt=0, description="La cantidad debe ser mayor a cero")

# --- RUTA DE LA VISTA ---
@app.get("/", response_class=HTMLResponse)
async def leer_interfaz(request: Request):
    # Corrección: Sintaxis compatible con versiones recientes de Starlette/FastAPI
    return templates.TemplateResponse(request=request, name="index.html")

# --- ENDPOINTS (API REST) ---

@app.get("/api/dashboard")
def obtener_dashboard(db: Session = Depends(get_db)):
    productos = db.query(models.Producto).all()
    alertas = db.query(models.RegistroAlerta).order_by(models.RegistroAlerta.fecha.desc()).limit(5).all()
    
    criticos = [p for p in productos if p.stock <= p.stock_minimo]
    return {
        "total_productos": len(productos),
        "productos_criticos": len(criticos),
        "alertas_recientes": alertas
    }

@app.post("/api/ingreso")
def registrar_ingreso(trx: TransaccionBodega, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.sku == trx.sku).first()
    if not prod:
        prod = models.Producto(sku=trx.sku, nombre=f"Producto {trx.sku}", stock=trx.cantidad)
        db.add(prod)
    else:
        prod.stock += trx.cantidad
    db.commit()
    return {"status": "ok", "mensaje": f"Ingreso registrado. Nuevo stock: {prod.stock}"}

@app.post("/api/salida")
def procesar_salida(trx: TransaccionBodega, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.sku == trx.sku).first()
    if not prod or prod.stock < trx.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente o producto no encontrado")

    prod.stock -= trx.cantidad
    db.commit()

    if prod.stock <= prod.stock_minimo:
        mensaje_alerta = f"ALERTA: El SKU {prod.sku} ha caído a {prod.stock} unidades."
        nueva_alerta = models.RegistroAlerta(sku_producto=prod.sku, mensaje=mensaje_alerta)
        db.add(nueva_alerta)
        db.commit()

        try:
            resend.Emails.send({
                "from": "onboarding@resend.dev", # Cambiado al dominio sandbox de prueba
                "to": "gerente@empresa.com",
                "subject": f"Reposición Urgente: {prod.sku}",
                "html": f"<strong>{mensaje_alerta}</strong><br>Favor emitir orden de compra."
            })
        except Exception as e:
            print(f"Error enviando correo: {e}")

    return {"status": "ok", "mensaje": f"Salida exitosa. Stock restante: {prod.stock}"}