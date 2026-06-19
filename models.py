from sqlalchemy import Column, Integer, String
from database import Base

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    stock = Column(Integer)
    stock_minimo = Column(Integer) # Límite para disparar la alerta