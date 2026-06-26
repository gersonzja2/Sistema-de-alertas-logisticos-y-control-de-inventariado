# Requisitos del Sistema — ADS40

> Sistema de Alertas Logísticas y Control de Inventario
>
> Documentación generada a partir de la verificación y validación completa del código fuente (06/2026).

---

## 1. Requisitos Funcionales (RF)

| ID | Nombre | Estado | Implementación |
|----|--------|--------|----------------|
| **RF01** | Descuento en Tiempo Real | ✅ | `POST /api/salida` — endpoint unificado que procesa tanto salidas de inventario (`tipo: "salida"`) como ventas POS (`tipo: "pos"`). Descuenta stock en tiempo real, registra transacción con cantidad variable y actualiza contador de movimientos. El endpoint original RF01 descrito como `/api/pos/salida` (cantidad fija=1) fue reemplazado por este diseño más flexible. |
| **RF02** | Notificación de Umbral Mínimo | ✅ | `generar_alerta_y_notificar()` en `main.py:561` — se activa automáticamente al procesar una salida/POS cuando `stock <= stock_minimo`. Realiza 3 acciones: (1) registra alerta en tabla `RegistroAlerta`, (2) envía email vía Resend a Proveedor + Gerente, (3) envía webhook HTTP a `WEBHOOK_URL` (configurable vía `.env`). |
| **RF03** | Dashboard de Gestión | ✅ | `GET /api/dashboard` — retorna KPIs (total productos, productos críticos, despachos pendientes), top 5 productos por rotación (ordenados por `movimientos` descendente), y últimas 10 alertas registradas. Filtrado automático por sucursal del usuario. |
| **RF04** | Ingreso e Indexación de Lotes | ✅ | `POST /api/ingreso` — registra entrada de stock. Si el SKU no existe, lo crea automáticamente. Soporta número de lote opcional (`lote`), que si se provee se registra en la tabla `Lotes` independiente. Input con ícono de código de barras. |
| **RF05** | Autenticación y Control de Acceso | ✅ | `POST /api/auth/login` — login con JWT real (HS256, pyjwt), expiración 24h configurable. Retorna token + datos del usuario (id, username, rol, sucursal). `POST /api/auth/register` — creación de usuarios solo para administradores (protegido con `require_admin()`). `GET /api/auth/me` — devuelve datos del usuario autenticado. Password hashing con SHA-256 + salt (`PWD_SALT` configurable). |
| **RF06** | Gestión de Usuarios | ✅ | `GET /api/usuarios` — lista todos los usuarios con su rol y sucursal (admin-only). `DELETE /api/usuarios/{id}` — elimina usuario (admin-only). Protege al último administrador del sistema (`main.py:274-277`: si el usuario es admin y es el único, rechaza la operación). |
| **RF07** | Gestión de Sucursales | ✅ | CRUD completo con segmentación de datos. `GET /api/sucursales` — lista sucursales (admin ve todas, trabajador solo la suya). `POST /api/sucursales` — crear (admin, valida duplicados). `PUT /api/sucursales/{id}` — actualizar (admin, valida duplicados). `DELETE /api/sucursales/{id}` — eliminar (admin, rechaza si hay usuarios asignados a esa sucursal). |
| **RF08** | Datos de Proveedor/Comprador en Transacciones | ✅ | Todos los formularios de ingreso, salida/POS y despachos incluyen sección colapsable de datos de contacto. Los campos se persisten en `Transaccion` y `DespachoPendiente` y se despliegan en las tablas de historial y despachos. Campos: RUT, nombre, dirección, teléfono, email. |
| **RF09** | Gestión de Despachos | ✅ | `POST /api/despachos` — crear despacho pendiente (requiere SKU existente). `GET /api/despachos` — listar despachos (filtrados por sucursal). `PATCH /api/despachos/{id}/completar` — marcar como completado. Incluye datos del comprador. |
| **RF10** | Consulta de Productos y Stock en Vivo | ✅ | `GET /api/productos` — lista todos los productos con stock actual, stock mínimo y movimientos. Soporta filtro `?sucursal_id=` para admin. `GET /api/productos/{sku}` — consulta individual. Las filas con stock crítico (`stock <= stock_minimo`) se resaltan en rojo en la UI. |
| **RF11** | Filtro por Sucursal | ✅ | Los trabajadores ven automáticamente solo los datos de su sucursal asignada (productos, transacciones, despachos, dashboard). Los administradores tienen un selector en el header para filtrar cualquier vista por sucursal. Implementado vía `get_sucursal_id()` en endpoints y `getFilterSucursalId()` en frontend. |
| **RF12** | Seed Automático de Admin por Defecto | ✅ | `seed_admin()` en `main.py:48` — al iniciar el sistema, crea automáticamente el usuario `admin` / `admin123` con rol administrador si no existe. Busca por username `"admin"` (no por rol), garantizando que siempre exista aunque haya otros admins en BD. |
| **RF13** | Página de Login | ✅ | Ruta `GET /login` — página única con diseño oscuro. Sin pestaña de registro público. Muestra overlay con rol y sucursal después de login exitoso, redirige automáticamente al sistema. |
| **RF14** | Interfaz Principal | ✅ | Ruta `GET /` — interfaz con 9 secciones navegables: Home, Dashboard, Stock en Vivo, Ingreso, Salida/POS, Historial, Despachos, Usuarios (admin), Sucursales (admin). Sidebar con navegación por rol: las secciones admin tienen borde rojo. Header con avatar, nombre, badge de rol, selector de sucursal (admin) y botón de salir. |
| **RF15** | Wizard de Configuración Inicial | ✅ | En la sección Home, si el administrador no tiene sucursales registradas, se muestra un wizard para crear la primera sucursal. Incluye formulario con nombre y dirección, y validación de campos requeridos. |
| **RF16** | Protección de Rutas | ✅ | Middleware `get_current_user()` en endpoints protegidos valida token JWT. `require_admin()` protege endpoints administrativos. Redirección a `/login` si no hay token. |

---

## 2. Requisitos No Funcionales (RNF)

| ID | Nombre | Estado | Implementación |
|----|--------|--------|----------------|
| **RNF01** | Latencia de Sincronización | ✅ | Middleware HTTP `monitorear_latencia()` en `main.py:162` — mide tiempo de respuesta de cada request. Agrega header `X-Response-Time-Ms` con la duración en milisegundos. Loggea a consola cuando supera 500ms. |
| **RNF02** | Alta Disponibilidad | ✅ | `GET /health` en `main.py:174` — endpoint público sin autenticación que retorna `{"status": "healthy", "uptime_sla": "99.9%", "timestamp": ...}`. No tiene dependencias externas para el health check. |
| **RNF03** | Seguridad y Control de Acceso | ✅ | JWT con algoritmo HS256 y `JWT_SECRET` configurable vía `.env`. Password hashing con `hashlib.sha256(f"{password}:{SALT}".encode()).hexdigest()`. Roles: `admin` (acceso total) y `trabajador` (solo su sucursal). Middleware `require_admin()` retorna 403 si no es admin. Token expiración configurable (default 24h). Token de simulación `simulacion-jwt-token-123` para tests. |
| **RNF04** | Arquitectura de Base de Datos | ✅ | SQLAlchemy ORM con `declarative_base()`. Pool de conexiones por defecto de SQLAlchemy. `PRAGMA foreign_keys=ON` para integridad referencial. SQLite como motor actual, preparado para migrar a PostgreSQL cambiando `DATABASE_URL`. Modelos: User, Sucursal, Producto, Lote, Transaccion, DespachoPendiente, RegistroAlerta. |
| **RNF05** | Stack Tecnológico | ✅ | **Backend**: Python 3.12+ / FastAPI / Uvicorn. **ORM**: SQLAlchemy 2.0. **Auth**: PyJWT. **Email**: Resend SDK. **Frontend**: HTML5 + CSS3 + JavaScript vanilla. **Iconos**: Lucide (vía CDN). **Fuente**: Outfit (Google Fonts). **Tests**: pytest + httpx (TestClient). |
| **RNF06** | Diseño UI/UX | ✅ | Tema oscuro completo (slate blue). Diseño responsive (grid adaptable a móvil). Animaciones y transiciones suaves (fadeIn, slideIn, hover effects). Tarjetas con efecto glassmorphism (backdrop-filter blur). KPIs con gradientes y sombras. Tablas con hover y resaltado de filas críticas. Sidebar colapsable en mobile. |
| **RNF07** | Mantenibilidad y Código Fuente | ✅ | Código modular: `main.py` (endpoints + lógica), `models.py` (ORM), `database.py` (conexión), `templates/` (HTML), `static/js/` (frontend), `static/css/` (estilos). Seed automático de admin al iniciar. Comentarios descriptivos en secciones clave. Variables de entorno para configuración sensible. |
| **RNF08** | Cobertura de Pruebas | ✅ | 33 tests automatizados con pytest. Cobertura: autenticación (login, JWT, register admin-only), roles y permisos (admin vs trabajador), CRUD de sucursales (crear, duplicado, actualizar, eliminar con usuarios), flujo completo de trabajador (login → ingreso → filtro por sucursal), stock (ingreso, salida, POS, alertas), protección de último admin, validaciones (cantidad inválida), dashboard, health check, latencia header. |

---

## 3. Matriz de Cobertura (Tests)

| Test | RF/RNF Relacionado | Archivo:Línea |
|------|-------------------|---------------|
| `test_ingreso_producto_nuevo` | RF04 | `test.py:44` |
| `test_ingreso_con_lote` | RF04 | `test.py:49` |
| `test_stock_en_vivo` | RF10 | `test.py:55` |
| `test_producto_individual` | RF10 | `test.py:62` |
| `test_historial_transacciones` | RF01 | `test.py:72` |
| `test_salida_exitosa` | RF01 | `test.py:85` |
| `test_salida_insuficiente` | RF01 | `test.py:91` |
| `test_pos_cantidad_variable` | RF01 | `test.py:97` |
| `test_pos_sin_stock` | RF01 | `test.py:103` |
| `test_salida_alerta_stock_minimo` | RF02 | `test.py:109` |
| `test_dashboard_rotacion_y_despachos` | RF03, RF09 | `test.py:125` |
| `test_health_check` | RNF02 | `test.py:138` |
| `test_jwt_requerido` | RNF03 | `test.py:145` |
| `test_latencia_header` | RNF01 | `test.py:151` |
| `test_validaciones_cantidad_invalida` | RNF03 | `test.py:157` |
| `test_login_admin_exitoso` | RF05 | `test.py:169` |
| `test_login_credenciales_invalidas` | RF05 | `test.py:177` |
| `test_login_usuario_inexistente` | RF05 | `test.py:182` |
| `test_me_con_token_valido` | RF05 | `test.py:188` |
| `test_me_sin_token` | RF05, RNF03 | `test.py:195` |
| `test_register_trabajador` | RF05, RF06 | `test.py:201` |
| `test_register_duplicado` | RF05 | `test.py:215` |
| `test_register_sin_auth` | RF05, RNF03 | `test.py:229` |
| `test_register_sucursal_inexistente` | RF05, RF07 | `test.py:235` |
| `test_listar_usuarios` | RF06 | `test.py:245` |
| `test_listar_usuarios_sin_auth` | RF06, RNF03 | `test.py:252` |
| `test_crear_sucursal` | RF07 | `test.py:258` |
| `test_crear_sucursal_duplicada` | RF07 | `test.py:266` |
| `test_crear_sucursal_sin_auth` | RF07, RNF03 | `test.py:273` |
| `test_actualizar_sucursal` | RF07 | `test.py:277` |
| `test_eliminar_sucursal_sin_usuarios` | RF07 | `test.py:286` |
| `test_flujo_trabajador` | RF05, RF07, RF10, RF11 | `test.py:297` |
| `test_no_eliminar_unico_admin` | RF06 | `test.py:341` |

---

## 4. Endpoints del Sistema

### Públicos (sin autenticación)

| Método | Ruta | Propósito |
|--------|------|-----------|
| `GET` | `/health` | Health check (RNF02) |
| `GET` | `/login` | Página de login (RF13) |
| `POST` | `/api/auth/login` | Iniciar sesión (RF05) |

### Autenticados (requieren JWT)

| Método | Ruta | Propósito | Rol |
|--------|------|-----------|-----|
| `GET` | `/` | Interfaz principal (RF14) | Cualquiera |
| `GET` | `/api/auth/me` | Obtener usuario actual (RF05) | Cualquiera |
| `GET` | `/api/productos` | Listar productos (RF10) | Cualquiera |
| `GET` | `/api/productos/{sku}` | Producto individual (RF10) | Cualquiera |
| `GET` | `/api/historial` | Historial de transacciones (RF01) | Cualquiera |
| `GET` | `/api/dashboard` | Dashboard (RF03) | Cualquiera |
| `POST` | `/api/ingreso` | Registrar ingreso (RF04) | Cualquiera |
| `POST` | `/api/salida` | Procesar salida/POS (RF01) | Cualquiera |
| `GET` | `/api/despachos` | Listar despachos (RF09) | Cualquiera |
| `POST` | `/api/despachos` | Crear despacho (RF09) | Cualquiera |
| `PATCH` | `/api/despachos/{id}/completar` | Completar despacho (RF09) | Cualquiera |
| `GET` | `/api/sucursales` | Listar sucursales (RF07) | Cualquiera |

### Solo Administradores

| Método | Ruta | Propósito |
|--------|------|-----------|
| `POST` | `/api/auth/register` | Crear usuario (RF05) |
| `GET` | `/api/usuarios` | Listar usuarios (RF06) |
| `DELETE` | `/api/usuarios/{id}` | Eliminar usuario (RF06) |
| `POST` | `/api/sucursales` | Crear sucursal (RF07) |
| `PUT` | `/api/sucursales/{id}` | Actualizar sucursal (RF07) |
| `DELETE` | `/api/sucursales/{id}` | Eliminar sucursal (RF07) |

---

## 5. Modelos de Datos

| Modelo | Tabla | Campos Clave |
|--------|-------|--------------|
| `Sucursal` | `sucursales` | id, nombre (unique), direccion, created_at |
| `User` | `usuarios` | id, username (unique), password_hash, rol (admin/trabajador), sucursal_id (FK), created_at |
| `Producto` | `productos` | id, sku (indexed), nombre, stock, stock_minimo, movimientos, sucursal_id (FK) |
| `Lote` | `lotes` | id, sku, numero_lote, cantidad, sucursal_id (FK), fecha_ingreso |
| `Transaccion` | `transacciones` | id, sku, tipo (ingreso/salida/pos), cantidad, stock_resultante, lote, destino, sucursal_id (FK), fecha, proveedor_\*, comprador_\* |
| `DespachoPendiente` | `despachos_pendientes` | id, sku, destino, cantidad, sucursal_id (FK), estado (pendiente/completado), fecha_creacion, comprador_\* |
| `RegistroAlerta` | `registro_alertas` | id, sku_producto, sucursal_id (FK), fecha, mensaje |

---

## 6. Configuración del Entorno (`.env`)

| Variable | Default | Propósito |
|----------|---------|-----------|
| `RESEND_API_KEY` | `re_tu_llave_de_prueba` | API key para envío de emails |
| `JWT_SECRET` | (50 chars aleatorios) | Secreto para firmar tokens JWT |
| `PWD_SALT` | `ads40-salt-logistica` | Salt para hashing de contraseñas |
| `WEBHOOK_URL` | `""` | URL para webhook de alertas |
| `PROVEEDOR_EMAIL` | `proveedor@empresa.com` | Email del proveedor para alertas |

---

## 7. Estado de Validación

- **Tests**: 33/33 pasan
- **Cobertura de RF**: 16/16 implementados ✅
- **Cobertura de RNF**: 8/8 implementados ✅
- **Última verificación**: Junio 2026
