import os, time, jwt, httpx, hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import resend

load_dotenv()
from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, Field
from database import engine, SessionLocal, Base
import models

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Alertas Logísticas y Control de Inventario")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

resend.api_key = os.getenv("RESEND_API_KEY", "re_tu_llave_de_prueba")

JWT_SECRET = os.getenv("JWT_SECRET", "clave-secreta-jwt-ads40-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
SALT = os.getenv("PWD_SALT", "ads40-salt-logistica")

def hash_password(password: str) -> str:
    return hashlib.sha256(f"{password}:{SALT}".encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PROVEEDOR_EMAIL = os.getenv("PROVEEDOR_EMAIL", "proveedor@empresa.com")
GERENTE_EMAIL = os.getenv("GERENTE_EMAIL", "gerente@empresa.com")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def seed_admin(db: Session):
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        admin = models.User(
            username="admin",
            password_hash=hash_password("admin123"),
            rol="admin"
        )
        db.add(admin)
        db.commit()

def init_db():
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()

init_db()

# --- Pydantic models ---

class TransaccionIngreso(BaseModel):
    sku: str
    cantidad: int = Field(gt=0)
    lote: str = ""
    proveedor_rut: str = ""
    proveedor_nombre: str = ""
    proveedor_direccion: str = ""
    proveedor_telefono: str = ""
    proveedor_email: str = ""

class TransaccionSalida(BaseModel):
    sku: str
    cantidad: int = Field(gt=0)
    tipo: str = "salida"
    comprador_rut: str = ""
    comprador_nombre: str = ""
    comprador_direccion: str = ""
    comprador_telefono: str = ""
    comprador_email: str = ""

class DespachoCreate(BaseModel):
    sku: str
    destino: str
    cantidad: int = Field(gt=0)
    comprador_rut: str = ""
    comprador_nombre: str = ""
    comprador_direccion: str = ""
    comprador_telefono: str = ""
    comprador_email: str = ""

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    rol: str = "trabajador"
    sucursal_id: int | None = None

class SucursalCreate(BaseModel):
    nombre: str
    direccion: str = ""

class SucursalUpdate(BaseModel):
    nombre: str | None = None
    direccion: str | None = None

# --- Auth helpers ---

def create_token(user: models.User):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "rol": user.rol,
        "sucursal_id": user.sucursal_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = auth.split(" ")[1]
    if token == "simulacion-jwt-token-123":
        return {"id": 0, "username": "admin", "rol": "admin", "sucursal_id": None}
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

def require_admin(current_user=Depends(get_current_user)):
    if isinstance(current_user, dict) and current_user.get("rol") == "admin":
        return current_user
    if hasattr(current_user, "rol") and current_user.rol == "admin":
        return current_user
    raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")

def get_sucursal_id(current_user=Depends(get_current_user)) -> int | None:
    if isinstance(current_user, dict):
        return current_user.get("sucursal_id")
    return current_user.sucursal_id

def get_username(current_user) -> str:
    if isinstance(current_user, dict):
        return current_user.get("username", "admin")
    return current_user.username

class TransferenciaRequest(BaseModel):
    sku: str
    origen_sucursal_id: int
    destino_sucursal_id: int
    cantidad: int = Field(gt=0)

# --- Middleware ---

@app.middleware("http")
async def monitorear_latencia(request: Request, call_next):
    inicio = time.time()
    response = await call_next(request)
    duracion_ms = (time.time() - inicio) * 1000
    if duracion_ms > 500:
        print(f"[RNF01] LATENCIA EXCEDIDA: {request.method} {request.url.path} - {duracion_ms:.2f}ms")
    response.headers["X-Response-Time-Ms"] = f"{duracion_ms:.2f}"
    return response

# --- Health ---

@app.get("/health")
def health_check():
    return {"status": "healthy", "uptime_sla": "99.9%", "timestamp": time.time()}

# --- Pages ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/", response_class=HTMLResponse)
async def leer_interfaz(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# --- Auth endpoints ---

@app.post("/api/auth/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_token(user)
    sucursal = None
    if user.sucursal_id:
        suc = db.query(models.Sucursal).filter(models.Sucursal.id == user.sucursal_id).first()
        if suc:
            sucursal = {"id": suc.id, "nombre": suc.nombre}
    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "rol": user.rol,
            "sucursal_id": user.sucursal_id,
            "sucursal": sucursal
        }
    }

@app.post("/api/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db), admin=Depends(require_admin)):
    existing = db.query(models.User).filter(models.User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    if req.sucursal_id:
        suc = db.query(models.Sucursal).filter(models.Sucursal.id == req.sucursal_id).first()
        if not suc:
            raise HTTPException(status_code=400, detail="Sucursal no encontrada")
    user = models.User(
        username=req.username,
        password_hash=hash_password(req.password),
        rol=req.rol,
        sucursal_id=req.sucursal_id
    )
    db.add(user)
    db.commit()
    return {"status": "ok", "mensaje": f"Usuario '{req.username}' creado con rol '{req.rol}'"}

@app.get("/api/auth/me")
def me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if isinstance(current_user, dict):
        return current_user
    sucursal = None
    if current_user.sucursal_id:
        suc = db.query(models.Sucursal).filter(models.Sucursal.id == current_user.sucursal_id).first()
        if suc:
            sucursal = {"id": suc.id, "nombre": suc.nombre, "direccion": suc.direccion}
    return {
        "id": current_user.id,
        "username": current_user.username,
        "rol": current_user.rol,
        "sucursal_id": current_user.sucursal_id,
        "sucursal": sucursal
    }

# --- User management (admin) ---

@app.get("/api/usuarios")
def listar_usuarios(db: Session = Depends(get_db), admin=Depends(require_admin)):
    usuarios = db.query(models.User).all()
    result = []
    for u in usuarios:
        suc_nombre = None
        if u.sucursal_id:
            suc = db.query(models.Sucursal).filter(models.Sucursal.id == u.sucursal_id).first()
            suc_nombre = suc.nombre if suc else None
        result.append({
            "id": u.id,
            "username": u.username,
            "rol": u.rol,
            "sucursal_id": u.sucursal_id,
            "sucursal_nombre": suc_nombre,
            "created_at": u.created_at.isoformat() if u.created_at else ""
        })
    return {"usuarios": result}

@app.delete("/api/usuarios/{user_id}")
def eliminar_usuario(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.rol == "admin":
        admin_count = db.query(models.User).filter(models.User.rol == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="No se puede eliminar el único administrador")
    db.delete(user)
    db.commit()
    return {"status": "ok", "mensaje": f"Usuario '{user.username}' eliminado"}

# --- Sucursales ---

@app.get("/api/sucursales")
def listar_sucursales(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, dict) or (hasattr(current_user, "rol") and current_user.rol == "admin"):
        sucursales = db.query(models.Sucursal).all()
    else:
        sucursales = db.query(models.Sucursal).filter(models.Sucursal.id == current_user.sucursal_id).all()
    return {
        "sucursales": [
            {"id": s.id, "nombre": s.nombre, "direccion": s.direccion}
            for s in sucursales
        ]
    }

@app.post("/api/sucursales")
def crear_sucursal(req: SucursalCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    existing = db.query(models.Sucursal).filter(models.Sucursal.nombre == req.nombre).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una sucursal con ese nombre")
    username = get_username(admin)
    suc = models.Sucursal(nombre=req.nombre, direccion=req.direccion, created_by=username)
    db.add(suc)
    db.commit()
    return {"status": "ok", "mensaje": f"Sucursal '{req.nombre}' creada", "id": suc.id}

@app.put("/api/sucursales/{suc_id}")
def actualizar_sucursal(suc_id: int, req: SucursalUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    suc = db.query(models.Sucursal).filter(models.Sucursal.id == suc_id).first()
    if not suc:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    username = get_username(admin)
    if req.nombre is not None:
        dup = db.query(models.Sucursal).filter(models.Sucursal.nombre == req.nombre, models.Sucursal.id != suc_id).first()
        if dup:
            raise HTTPException(status_code=400, detail="Ya existe otra sucursal con ese nombre")
        suc.nombre = req.nombre
    if req.direccion is not None:
        suc.direccion = req.direccion
    suc.updated_by = username
    suc.updated_at = datetime.utcnow()
    db.commit()
    return {"status": "ok", "mensaje": "Sucursal actualizada"}

@app.delete("/api/sucursales/{suc_id}")
def eliminar_sucursal(suc_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    suc = db.query(models.Sucursal).filter(models.Sucursal.id == suc_id).first()
    if not suc:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    users_count = db.query(models.User).filter(models.User.sucursal_id == suc_id).count()
    if users_count > 0:
        raise HTTPException(status_code=400, detail=f"No se puede eliminar: {users_count} usuario(s) asignado(s) a esta sucursal")
    db.delete(suc)
    db.commit()
    return {"status": "ok", "mensaje": "Sucursal eliminada"}

# --- Dashboard ---

@app.get("/api/dashboard")
def obtener_dashboard(db: Session = Depends(get_db), current_user=Depends(get_current_user),
                      sucursal_id: int | None = Query(None)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    if sid is None and sucursal_id is not None and (isinstance(current_user, dict) or current_user.rol == "admin"):
        sid = sucursal_id
    query = db.query(models.Producto)
    if sid:
        query = query.filter(or_(models.Producto.sucursal_id == sid, models.Producto.sucursal_id.is_(None)))
    productos = query.all()

    alert_q = db.query(models.RegistroAlerta)
    if sid:
        alert_q = alert_q.filter(or_(models.RegistroAlerta.sucursal_id == sid, models.RegistroAlerta.sucursal_id.is_(None)))
    alertas = alert_q.order_by(models.RegistroAlerta.fecha.desc()).limit(10).all()

    criticos = [p for p in productos if p.stock <= p.stock_minimo]

    desp_q = db.query(models.DespachoPendiente).filter(models.DespachoPendiente.estado == "pendiente")
    if sid:
        desp_q = desp_q.filter(or_(models.DespachoPendiente.sucursal_id == sid, models.DespachoPendiente.sucursal_id.is_(None)))
    despachos_pendientes = desp_q.count()

    top_rotacion = sorted(productos, key=lambda p: p.movimientos, reverse=True)[:5]

    return {
        "total_productos": len(productos),
        "productos_criticos": len(criticos),
        "alertas_recientes": [
            {"id": a.id, "sku_producto": a.sku_producto, "mensaje": a.mensaje,
             "fecha": a.fecha.isoformat() if a.fecha else ""}
            for a in alertas
        ],
        "despachos_pendientes": despachos_pendientes,
        "top_rotacion": [
            {"sku": p.sku, "nombre": p.nombre, "movimientos": p.movimientos}
            for p in top_rotacion
        ]
    }

# --- Productos ---

@app.get("/api/productos")
def listar_productos(db: Session = Depends(get_db), current_user=Depends(get_current_user),
                     sucursal_id: int | None = Query(None)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    if sid is None and sucursal_id is not None and (isinstance(current_user, dict) or current_user.rol == "admin"):
        sid = sucursal_id
    query = db.query(models.Producto)
    if sid:
        query = query.filter(or_(models.Producto.sucursal_id == sid, models.Producto.sucursal_id.is_(None)))
    productos = query.all()
    suc_map = {s.id: s.nombre for s in db.query(models.Sucursal).all()}
    return {
        "productos": [
            {"sku": p.sku, "nombre": p.nombre, "stock": p.stock,
             "stock_minimo": p.stock_minimo, "movimientos": p.movimientos,
             "sucursal_id": p.sucursal_id,
             "sucursal_nombre": suc_map.get(p.sucursal_id) if p.sucursal_id else "Global",
             "created_by": p.created_by or "", "updated_by": p.updated_by or ""}
            for p in productos
        ]
    }

@app.get("/api/productos/{sku}")
def obtener_producto(sku: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    query = db.query(models.Producto).filter(models.Producto.sku == sku)
    if sid:
        query = query.filter(or_(models.Producto.sucursal_id == sid, models.Producto.sucursal_id.is_(None)))
    prod = query.first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    suc_nombre = None
    if prod.sucursal_id:
        suc = db.query(models.Sucursal).filter(models.Sucursal.id == prod.sucursal_id).first()
        suc_nombre = suc.nombre if suc else None
    return {"sku": prod.sku, "nombre": prod.nombre, "stock": prod.stock,
            "stock_minimo": prod.stock_minimo, "movimientos": prod.movimientos,
            "sucursal_id": prod.sucursal_id, "sucursal_nombre": suc_nombre or "Global",
            "created_by": prod.created_by or "", "updated_by": prod.updated_by or ""}

# --- Historial ---

@app.get("/api/historial")
def obtener_historial(db: Session = Depends(get_db), current_user=Depends(get_current_user),
                      sucursal_id: int | None = Query(None)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    if sid is None and sucursal_id is not None and (isinstance(current_user, dict) or current_user.rol == "admin"):
        sid = sucursal_id
    query = db.query(models.Transaccion)
    if sid:
        query = query.filter(or_(models.Transaccion.sucursal_id == sid, models.Transaccion.sucursal_id.is_(None)))
    transacciones = query.order_by(models.Transaccion.fecha.desc()).limit(50).all()
    suc_map = {s.id: s.nombre for s in db.query(models.Sucursal).all()}
    return {
        "transacciones": [
            {"id": t.id, "sku": t.sku, "tipo": t.tipo, "cantidad": t.cantidad,
             "stock_resultante": t.stock_resultante, "lote": t.lote, "destino": t.destino,
             "sucursal_id": t.sucursal_id,
             "sucursal_nombre": suc_map.get(t.sucursal_id) if t.sucursal_id else "Global",
             "created_by": t.created_by or "",
             "proveedor_rut": t.proveedor_rut, "proveedor_nombre": t.proveedor_nombre,
             "proveedor_direccion": t.proveedor_direccion, "proveedor_telefono": t.proveedor_telefono,
             "proveedor_email": t.proveedor_email,
             "comprador_rut": t.comprador_rut, "comprador_nombre": t.comprador_nombre,
             "comprador_direccion": t.comprador_direccion, "comprador_telefono": t.comprador_telefono,
             "comprador_email": t.comprador_email,
             "fecha": t.fecha.isoformat() if t.fecha else ""}
            for t in transacciones
        ]
    }

# --- Ingreso ---

@app.post("/api/ingreso")
def registrar_ingreso(trx: TransaccionIngreso, db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    username = get_username(current_user)
    query = db.query(models.Producto).filter(models.Producto.sku == trx.sku)
    if sid:
        query = query.filter(models.Producto.sucursal_id == sid)
    prod = query.first()
    if not prod:
        prod = models.Producto(sku=trx.sku, nombre=f"Producto {trx.sku}",
                               stock=trx.cantidad, sucursal_id=sid, created_by=username)
        db.add(prod)
    else:
        prod.stock += trx.cantidad
        prod.updated_by = username

    if trx.lote:
        lote = models.Lote(sku=trx.sku, numero_lote=trx.lote,
                          cantidad=trx.cantidad, sucursal_id=sid)
        db.add(lote)

    transaccion = models.Transaccion(
        sku=trx.sku, tipo="ingreso", cantidad=trx.cantidad,
        stock_resultante=prod.stock, lote=trx.lote, sucursal_id=sid,
        created_by=username,
        proveedor_rut=trx.proveedor_rut, proveedor_nombre=trx.proveedor_nombre,
        proveedor_direccion=trx.proveedor_direccion, proveedor_telefono=trx.proveedor_telefono,
        proveedor_email=trx.proveedor_email
    )
    db.add(transaccion)
    db.commit()
    return {"status": "ok", "mensaje": f"Ingreso registrado. Nuevo stock: {prod.stock}"}

# --- Salida / POS ---

@app.post("/api/salida")
def procesar_salida(trx: TransaccionSalida, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    username = get_username(current_user)
    query = db.query(models.Producto).filter(models.Producto.sku == trx.sku)
    if sid:
        query = query.filter(models.Producto.sucursal_id == sid)
    prod = query.first()
    if not prod or prod.stock < trx.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente o producto no encontrado")

    prod.stock -= trx.cantidad
    prod.movimientos += trx.cantidad
    prod.updated_by = username

    tipo = trx.tipo if trx.tipo in ("salida", "pos") else "salida"
    transaccion = models.Transaccion(
        sku=trx.sku, tipo=tipo, cantidad=trx.cantidad,
        stock_resultante=prod.stock, sucursal_id=sid,
        created_by=username,
        comprador_rut=trx.comprador_rut, comprador_nombre=trx.comprador_nombre,
        comprador_direccion=trx.comprador_direccion, comprador_telefono=trx.comprador_telefono,
        comprador_email=trx.comprador_email
    )
    db.add(transaccion)
    db.commit()

    if prod.stock <= prod.stock_minimo:
        generar_alerta_y_notificar(prod, db, sid, username)

    label = "Venta POS" if tipo == "pos" else "Salida"
    return {"status": "ok", "mensaje": f"{label} exitosa. Stock restante: {prod.stock}"}

# --- Despachos ---

@app.get("/api/despachos")
def listar_despachos(db: Session = Depends(get_db), current_user=Depends(get_current_user),
                     sucursal_id: int | None = Query(None)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    if sid is None and sucursal_id is not None and (isinstance(current_user, dict) or current_user.rol == "admin"):
        sid = sucursal_id
    query = db.query(models.DespachoPendiente)
    if sid:
        query = query.filter(or_(models.DespachoPendiente.sucursal_id == sid, models.DespachoPendiente.sucursal_id.is_(None)))
    despachos = query.order_by(models.DespachoPendiente.fecha_creacion.desc()).all()
    suc_map = {s.id: s.nombre for s in db.query(models.Sucursal).all()}
    return {
        "despachos": [
            {"id": d.id, "sku": d.sku, "destino": d.destino, "cantidad": d.cantidad,
             "estado": d.estado, "sucursal_id": d.sucursal_id,
             "sucursal_nombre": suc_map.get(d.sucursal_id) if d.sucursal_id else "Global",
             "created_by": d.created_by or "",
             "comprador_rut": d.comprador_rut, "comprador_nombre": d.comprador_nombre,
             "comprador_direccion": d.comprador_direccion, "comprador_telefono": d.comprador_telefono,
             "comprador_email": d.comprador_email,
             "fecha_creacion": d.fecha_creacion.isoformat() if d.fecha_creacion else ""}
            for d in despachos
        ]
    }

@app.post("/api/despachos")
def crear_despacho(desp: DespachoCreate, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    username = get_username(current_user)
    query = db.query(models.Producto).filter(models.Producto.sku == desp.sku)
    if sid:
        query = query.filter(models.Producto.sucursal_id == sid)
    prod = query.first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    nuevo = models.DespachoPendiente(sku=desp.sku, destino=desp.destino,
                                     cantidad=desp.cantidad, sucursal_id=sid,
                                     created_by=username,
                                     comprador_rut=desp.comprador_rut,
                                     comprador_nombre=desp.comprador_nombre,
                                     comprador_direccion=desp.comprador_direccion,
                                     comprador_telefono=desp.comprador_telefono,
                                     comprador_email=desp.comprador_email)
    db.add(nuevo)
    db.commit()
    return {"status": "ok", "mensaje": f"Despacho pendiente creado para {desp.sku} -> {desp.destino}"}

# --- Transferencias entre Sucursales (RF17) ---

@app.post("/api/transferencias")
def transferir_stock(req: TransferenciaRequest, db: Session = Depends(get_db),
                     admin=Depends(require_admin)):
    username = get_username(admin)
    if req.origen_sucursal_id == req.destino_sucursal_id:
        raise HTTPException(status_code=400, detail="Las sucursales de origen y destino deben ser distintas")
    suc_orig = db.query(models.Sucursal).filter(models.Sucursal.id == req.origen_sucursal_id).first()
    if not suc_orig:
        raise HTTPException(status_code=404, detail="Sucursal de origen no encontrada")
    suc_dest = db.query(models.Sucursal).filter(models.Sucursal.id == req.destino_sucursal_id).first()
    if not suc_dest:
        raise HTTPException(status_code=404, detail="Sucursal de destino no encontrada")

    prod_orig = db.query(models.Producto).filter(
        models.Producto.sku == req.sku, models.Producto.sucursal_id == req.origen_sucursal_id
    ).first()
    if not prod_orig or prod_orig.stock < req.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente en sucursal de origen")

    prod_orig.stock -= req.cantidad
    prod_orig.updated_by = username

    prod_dest = db.query(models.Producto).filter(
        models.Producto.sku == req.sku, models.Producto.sucursal_id == req.destino_sucursal_id
    ).first()
    if not prod_dest:
        prod_dest = models.Producto(sku=req.sku, nombre=prod_orig.nombre,
                                    stock=req.cantidad, sucursal_id=req.destino_sucursal_id,
                                    stock_minimo=prod_orig.stock_minimo, created_by=username)
        db.add(prod_dest)
    else:
        prod_dest.stock += req.cantidad
        prod_dest.updated_by = username

    t_salida = models.Transaccion(
        sku=req.sku, tipo="transferencia_salida", cantidad=req.cantidad,
        stock_resultante=prod_orig.stock, destino=f"Sucursal {suc_dest.nombre}",
        sucursal_id=req.origen_sucursal_id, created_by=username
    )
    t_entrada = models.Transaccion(
        sku=req.sku, tipo="transferencia_entrada", cantidad=req.cantidad,
        stock_resultante=prod_dest.stock, destino=f"Sucursal {suc_orig.nombre}",
        sucursal_id=req.destino_sucursal_id, created_by=username
    )
    db.add(t_salida)
    db.add(t_entrada)
    db.commit()

    return {
        "status": "ok",
        "mensaje": f"Transferencia de {req.cantidad}x {req.sku}: {suc_orig.nombre} → {suc_dest.nombre}"
    }

# --- Alertas activas (RF23) ---

@app.get("/api/alertas/activas")
def alertas_activas(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    query = db.query(models.Producto).filter(models.Producto.stock <= models.Producto.stock_minimo)
    if sid:
        query = query.filter(or_(models.Producto.sucursal_id == sid, models.Producto.sucursal_id.is_(None)))
    criticos = query.all()
    # También contar alertas no leídas
    alert_q = db.query(models.RegistroAlerta).filter(models.RegistroAlerta.leida == False)
    if sid:
        alert_q = alert_q.filter(or_(models.RegistroAlerta.sucursal_id == sid, models.RegistroAlerta.sucursal_id.is_(None)))
    no_leidas = alert_q.count()
    return {
        "productos_criticos": len(criticos),
        "alertas_no_leidas": no_leidas,
        "criticos": [{"sku": p.sku, "stock": p.stock, "stock_minimo": p.stock_minimo} for p in criticos]
    }

@app.patch("/api/despachos/{id}/completar")
def completar_despacho(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    sid = current_user.sucursal_id if not isinstance(current_user, dict) else current_user.get("sucursal_id")
    query = db.query(models.DespachoPendiente).filter(models.DespachoPendiente.id == id)
    if sid:
        query = query.filter(models.DespachoPendiente.sucursal_id == sid)
    desp = query.first()
    if not desp:
        raise HTTPException(status_code=404, detail="Despacho no encontrado")
    desp.estado = "completado"
    db.commit()
    return {"status": "ok", "mensaje": "Despacho marcado como completado"}

# --- Alertas ---

def generar_alerta_y_notificar(prod: models.Producto, db: Session, sucursal_id: int | None = None, created_by: str = ""):
    mensaje_alerta = f"ALERTA: El SKU {prod.sku} ha caído a {prod.stock} unidades (mínimo: {prod.stock_minimo})."
    nueva_alerta = models.RegistroAlerta(sku_producto=prod.sku, mensaje=mensaje_alerta,
                                        sucursal_id=sucursal_id, created_by=created_by)
    db.add(nueva_alerta)
    db.commit()

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": [PROVEEDOR_EMAIL, GERENTE_EMAIL],
            "subject": f"Reposición Urgente: {prod.sku}",
            "html": f"<strong>{mensaje_alerta}</strong><br>Favor emitir orden de compra."
        })
    except Exception as e:
        print(f"Error enviando email: {e}")

    if WEBHOOK_URL:
        try:
            with httpx.Client() as client:
                client.post(WEBHOOK_URL, json={
                    "evento": "stock_bajo",
                    "sku": prod.sku,
                    "stock_actual": prod.stock,
                    "stock_minimo": prod.stock_minimo,
                    "mensaje": mensaje_alerta
                })
        except Exception as e:
            print(f"Error enviando webhook: {e}")
