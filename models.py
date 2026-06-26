from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from datetime import datetime
from database import Base

class Sucursal(Base):
    __tablename__ = "sucursales"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    direccion = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, default="")
    updated_by = Column(String, default="")
    updated_at = Column(DateTime, nullable=True)

class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    rol = Column(String, default="trabajador")
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True)
    nombre = Column(String)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=10)
    movimientos = Column(Integer, default=0)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    created_by = Column(String, default="")
    updated_by = Column(String, default="")

class Lote(Base):
    __tablename__ = "lotes"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True)
    numero_lote = Column(String)
    cantidad = Column(Integer, default=0)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    fecha_ingreso = Column(DateTime, default=datetime.utcnow)

class DespachoPendiente(Base):
    __tablename__ = "despachos_pendientes"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True)
    destino = Column(String)
    cantidad = Column(Integer)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    estado = Column(String, default="pendiente")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, default="")
    comprador_rut = Column(String, default="")
    comprador_nombre = Column(String, default="")
    comprador_direccion = Column(String, default="")
    comprador_telefono = Column(String, default="")
    comprador_email = Column(String, default="")

class Transaccion(Base):
    __tablename__ = "transacciones"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True)
    tipo = Column(String)
    cantidad = Column(Integer)
    stock_resultante = Column(Integer, default=0)
    lote = Column(String, default="")
    destino = Column(String, default="")
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, default="")
    proveedor_rut = Column(String, default="")
    proveedor_nombre = Column(String, default="")
    proveedor_direccion = Column(String, default="")
    proveedor_telefono = Column(String, default="")
    proveedor_email = Column(String, default="")
    comprador_rut = Column(String, default="")
    comprador_nombre = Column(String, default="")
    comprador_direccion = Column(String, default="")
    comprador_telefono = Column(String, default="")
    comprador_email = Column(String, default="")

class RegistroAlerta(Base):
    __tablename__ = "registro_alertas"
    id = Column(Integer, primary_key=True, index=True)
    sku_producto = Column(String)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    mensaje = Column(String)
    leida = Column(Boolean, default=False)
    created_by = Column(String, default="")
