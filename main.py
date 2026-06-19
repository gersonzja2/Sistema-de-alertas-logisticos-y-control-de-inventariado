import os
import resend
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models

Base.metadata.create_all(bind=engine)
app = FastAPI()
resend.api_key = os.getenv("RESEND_API_KEY")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/actualizar-stock/{prod_id}/{nueva_cantidad}")
def actualizar(prod_id: int, nueva_cantidad: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == prod_id).first()
    prod.stock = nueva_cantidad
    db.commit()
    
    # Lógica de Alerta (Regla de negocio)
    if prod.stock < prod.stock_minimo:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": "gerente@empresa.com",
            "subject": f"ALERTA: Stock Crítico de {prod.nombre}",
            "html": f"<p>El producto {prod.nombre} tiene solo {prod.stock} unidades.</p>"
        })
    return {"status": "actualizado"}