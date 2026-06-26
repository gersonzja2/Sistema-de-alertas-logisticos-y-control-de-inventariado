# Sistema de Alertas Logísticas y Control de Inventario

Sistema de gestión de inventario multi-sucursal con alertas en tiempo real, control de stock,
roles admin/trabajador y dashboard de KPIs. Desarrollado con FastAPI + SQLAlchemy + JavaScript vanilla.

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12+ / FastAPI / Uvicorn |
| ORM | SQLAlchemy 2.0 / SQLite |
| Auth | JWT (HS256) + SHA-256 password hashing |
| Email | Resend API |
| Frontend | HTML5 + CSS3 + JavaScript vanilla |
| Iconos | Lucide (CDN) |
| Tests | pytest + httpx (TestClient) |

---

## Requisitos Funcionales

| ID | Nombre | Estado | Descripción |
|----|--------|--------|-------------|
| **RF01** | Descuento en Tiempo Real | ✅ | `POST /api/salida` — endpoint unificado para salidas (`tipo: "salida"`) y ventas POS (`tipo: "pos"`). Descuenta stock en tiempo real, registra transacción con cantidad variable. |
| **RF02** | Notificación de Umbral Mínimo | ✅ | Alerta automática cuando `stock <= stock_minimo`. Envía email vía Resend a Proveedor + Gerente y webhook HTTP a `WEBHOOK_URL`. |
| **RF03** | Dashboard de Gestión | ✅ | `GET /api/dashboard` — KPIs (total productos, críticos, despachos pendientes), top 5 rotación, últimas 10 alertas. Filtrable por sucursal. |
| **RF04** | Ingreso e Indexación de Lotes | ✅ | `POST /api/ingreso` — entrada de stock con creación automática de SKU si no existe. Soporta número de lote opcional. |
| **RF05** | Autenticación y Control de Acceso | ✅ | Login JWT (HS256, 24h). Registro solo para admins. Password hashing SHA-256 + salt. |
| **RF06** | Gestión de Usuarios | ✅ | CRUD de usuarios (admin-only). Protege al último administrador del sistema. |
| **RF07** | Gestión de Sucursales | ✅ | CRUD completo con segmentación. Admin ve todas; trabajador solo la suya. Rechaza eliminar si hay usuarios asignados. |
| **RF08** | Datos de Proveedor/Comprador | ✅ | Formularios con RUT, nombre, dirección, teléfono, email en ingreso, salida/POS y despachos. |
| **RF09** | Gestión de Despachos | ✅ | Crear, listar y completar despachos pendientes. Incluye datos del comprador. |
| **RF10** | Consulta de Stock en Vivo | ✅ | `GET /api/productos` y `GET /api/productos/{sku}`. Filas críticas resaltadas en rojo. Filtro por sucursal. Columna "Sucursal" muestra nombre de sucursal o "Global". |
| **RF11** | Filtro por Sucursal | ✅ | Trabajadores ven solo su sucursal. Admin tiene selector en header para filtrar cualquier vista. Incluye registros globales (`sucursal_id IS NULL`). |
| **RF12** | Seed Automático de Admin | ✅ | Crea usuario `admin`/`admin123` al iniciar si no existe. |
| **RF13** | Página de Login | ✅ | Página única oscura sin registro público. Overlay de rol post-login. |
| **RF14** | Interfaz Principal | ✅ | 9 secciones navegables con sidebar por rol, header con avatar y selector de sucursal (admin). |
| **RF15** | Wizard de Configuración Inicial | ✅ | Wizard para crear primera sucursal si no hay ninguna registrada. |
| **RF16** | Protección de Rutas | ✅ | Middleware JWT en endpoints protegidos. `require_admin()` para rutas admin. Redirección a `/login` si no hay token. |
| **RF17** | Transferencias entre Sucursales | ✅ | Mover stock entre sucursales. `POST /api/transferencias` descuenta de origen y suma en destino. Registra transacciones de tipo `transferencia_salida` y `transferencia_entrada`. Solo admin. |
| **RF20** | Exportación CSV | ✅ | Botón "Exportar CSV" en tablas de Stock e Historial. Descarga datos visibles respetando filtro por sucursal. |
| **RF23** | Notificaciones en UI | ✅ | Badge numerado en sidebar con alertas activas (productos críticos + alertas no leídas). Se actualiza cada 30s. |
| **RF24** | Pista de Auditoría | ✅ | Campos `created_by`/`created_at` en Producto, Transaccion, DespachoPendiente, RegistroAlerta. `updated_by`/`updated_at` en Producto y Sucursal. |

---

## Requisitos No Funcionales

| ID | Nombre | Estado | Implementación |
|----|--------|--------|----------------|
| **RNF01** | Latencia | ✅ | Middleware mide tiempo de respuesta. Header `X-Response-Time-Ms`. Log cuando supera 500ms. |
| **RNF02** | Alta Disponibilidad | ✅ | `GET /health` público con `{"status": "healthy", "uptime_sla": "99.9%"}`. |
| **RNF03** | Seguridad | ✅ | JWT HS256 + SHA-256 + salt. Roles admin/trabajador. Token expiración configurable. |
| **RNF04** | Base de Datos | ✅ | SQLAlchemy ORM con `PRAGMA foreign_keys=ON`. Preparado para migrar a PostgreSQL. |
| **RNF05** | Stack Tecnológico | ✅ | FastAPI / SQLAlchemy / PyJWT / Resend / HTML+CSS+JS vanilla / Lucide / pytest. |
| **RNF06** | Diseño UI/UX | ✅ | Tema oscuro, responsive, glassmorphism, animaciones, resaltado de filas críticas. |
| **RNF07** | Mantenibilidad | ✅ | Código modular (main.py, models.py, database.py, templates/, static/). Seed automático. Variables de entorno. |
| **RNF08** | Cobertura de Pruebas | ✅ | 42 tests automatizados cubriendo auth, roles, CRUD, stock, alertas, dashboard, health, transferencias, auditoría. |

---

## Matriz de Cobertura (Tests)

42 tests — ver `REQUIREMENTS.md` sección 3 para el detalle completo línea por línea.

| Categoría | Tests |
|-----------|-------|
| Autenticación | login exitoso, credenciales inválidas, usuario inexistente, JWT requerido, /me con/sin token |
| Registro | crear trabajador, duplicado, sin auth, sucursal inexistente |
| Usuarios | listar, listar sin auth, no eliminar único admin |
| Sucursales | crear, duplicada, sin auth, actualizar, eliminar sin usuarios |
| Stock | ingreso, lote, stock en vivo, producto individual, salida exitosa, salida insuficiente, POS variable, POS sin stock |
| Alertas | alerta por stock mínimo |
| Dashboard | rotación y despachos |
| Flujo Trabajador | login → ingreso → filtro por sucursal |
| Salud | health check, latencia header, validaciones |
| Transferencias (RF17) | entre sucursales, misma sucursal rechazada, stock insuficiente, sin auth |
| Auditoría (RF24) | created_by en ingreso y sucursal, updated_by en sucursal, created_by en transacción |
| Notificaciones (RF23) | endpoint alertas activas |

---

## Endpoints del Sistema

### Públicos
| Método | Ruta | Propósito |
|--------|------|-----------|
| `GET` | `/health` | Health check |
| `GET` | `/login` | Página de login |
| `POST` | `/api/auth/login` | Iniciar sesión |

### Autenticados
| Método | Ruta | Propósito | Rol |
|--------|------|-----------|-----|
| `GET` | `/` | Interfaz principal | Cualquiera |
| `GET` | `/api/auth/me` | Usuario actual | Cualquiera |
| `GET` | `/api/productos` | Listar productos | Cualquiera |
| `GET` | `/api/productos/{sku}` | Producto individual | Cualquiera |
| `GET` | `/api/historial` | Historial | Cualquiera |
| `GET` | `/api/dashboard` | Dashboard | Cualquiera |
| `POST` | `/api/ingreso` | Registrar ingreso | Cualquiera |
| `POST` | `/api/salida` | Salida/POS | Cualquiera |
| `GET` | `/api/despachos` | Listar despachos | Cualquiera |
| `POST` | `/api/despachos` | Crear despacho | Cualquiera |
| `PATCH` | `/api/despachos/{id}/completar` | Completar despacho | Cualquiera |
| `GET` | `/api/sucursales` | Listar sucursales | Cualquiera |
| `GET` | `/api/alertas/activas` | Alertas activas y conteo | Cualquiera |

### Solo Admin
| Método | Ruta | Propósito |
|--------|------|-----------|
| `POST` | `/api/auth/register` | Crear usuario |
| `GET` | `/api/usuarios` | Listar usuarios |
| `DELETE` | `/api/usuarios/{id}` | Eliminar usuario |
| `POST` | `/api/sucursales` | Crear sucursal |
| `PUT` | `/api/sucursales/{id}` | Actualizar sucursal |
| `DELETE` | `/api/sucursales/{id}` | Eliminar sucursal |
| `POST` | `/api/transferencias` | Transferir stock entre sucursales |

---

## Modelos de Datos

| Modelo | Tabla | Campos Clave |
|--------|-------|--------------|
| `Sucursal` | `sucursales` | id, nombre (unique), direccion, created_by, created_at, updated_by, updated_at |
| `User` | `usuarios` | id, username (unique), password_hash, rol, sucursal_id (FK), created_at |
| `Producto` | `productos` | id, sku, nombre, stock, stock_minimo, movimientos, sucursal_id (FK), created_by, updated_by |
| `Lote` | `lotes` | id, sku, numero_lote, cantidad, sucursal_id (FK), fecha_ingreso |
| `Transaccion` | `transacciones` | id, sku, tipo, cantidad, stock_resultante, sucursal_id (FK), created_by, proveedor_*, comprador_*, fecha |
| `DespachoPendiente` | `despachos_pendientes` | id, sku, destino, cantidad, sucursal_id (FK), estado, created_by, comprador_*, fecha_creacion |
| `RegistroAlerta` | `registro_alertas` | id, sku_producto, sucursal_id (FK), fecha, mensaje, leida |

---

## Configuración del Entorno (`.env`)

| Variable | Default | Propósito |
|----------|---------|-----------|
| `RESEND_API_KEY` | `re_tu_llave_de_prueba` | API key para envío de emails |
| `JWT_SECRET` | (50 chars) | Secreto para firmar tokens JWT |
| `PWD_SALT` | `ads40-salt-logistica` | Salt para password hashing |
| `WEBHOOK_URL` | `""` | URL para webhook de alertas |
| `PROVEEDOR_EMAIL` | `proveedor@empresa.com` | Email del proveedor |
| `GERENTE_EMAIL` | `gerente@empresa.com` | Email del gerente |
| `DATABASE_URL` | `sqlite:///./logistica.db` | URL de conexión a BD |

---

## Quick Start

```bash
# 1. Clonar e instalar dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configurar variables de entorno
#    Editar .env con RESEND_API_KEY, etc.

# 3. Iniciar servidor
uvicorn main:app --reload --port 8000

# 4. Abrir navegador
#    http://localhost:8000/login
#    Usuario: admin / Contraseña: admin123

# 5. Ejecutar tests
python -m pytest static/tests/test.py -v
```

---

## Estado de Validación

- **Tests**: 42/42 pasan
- **RF implementados**: 20/20 ✅
- **RNF implementados**: 8/8
- **Última verificación**: Junio 2026
