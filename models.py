from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    nombre = Column(String)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=10)

class RegistroAlerta(Base):
    __tablename__ = "registro_alertas"
    id = Column(Integer, primary_key=True, index=True)
    sku_producto = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)
    mensaje = Column(String)