# 5. Diseño de la Solución

## 5.1 Arquitectura del Sistema

El sistema sigue una arquitectura **cliente-servidor de tres capas**:

```
┌─────────────────────────────────────────────────────┐
│                   Cliente Web                        │
│        (HTML + CSS + JavaScript + Lucide)            │
│              Navegador (Chrome/Firefox)              │
└────────────────────────┬────────────────────────────┘
                         │ HTTP (JSON)
                         ▼
┌─────────────────────────────────────────────────────┐
│               Servidor (FastAPI + Uvicorn)           │
│  ┌───────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Endpoints │  │ JWT Auth │  │ Lógica de Negocio│  │
│  │  REST API │  │ Middleware│  │ (alertas, stock) │  │
│  └───────────┘  └──────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────┘
                         │ SQLAlchemy ORM
                         ▼
┌─────────────────────────────────────────────────────┐
│            Base de Datos (SQLite / PostgreSQL)       │
│  7 tablas: usuarios, sucursales, productos, lotes,  │
│  transacciones, despachos_pendientes, alertas       │
└─────────────────────────────────────────────────────┘
```

**Capa de Presentación**: HTML5 semántico + CSS3 con tema oscuro (paleta slate-blue) + JavaScript vanilla. Sin frameworks ni dependencias externas pesadas (solo Lucide para iconos y Outfit para tipografía, ambos vía CDN).

**Capa de Lógica de Negocio**: FastAPI con endpoints REST organizados por dominio (auth, productos, historial, dashboard, despachos, transferencias). Middleware de latencia y autenticación JWT.

**Capa de Datos**: SQLAlchemy 2.0 con SQLite embebido (sin instalación de servidor BD). Schema con 7 tablas, foreign keys y `PRAGMA foreign_keys=ON` para integridad referencial.

## 5.2 Funcionalidades Clave

### 5.2.1 Autenticación con Roles (RF05, RF16)

El sistema implementa autenticación mediante JWT (JSON Web Token) con algoritmo HS256. Al iniciar sesión, el servidor valida las credenciales contra el hash SHA-256 almacenado y retorna un token con los datos del usuario (id, username, rol, sucursal_id). Este token debe enviarse en el header `Authorization: Bearer <token>` para acceder a endpoints protegidos.

Los roles determinan la experiencia:
- **Admin**: ve el selector de sucursal en el header, puede filtrar cualquier vista, accede a las secciones de administración (Usuarios, Sucursales, Transferencias).
- **Trabajador**: solo ve datos de su sucursal + globales. No tiene acceso a las secciones admin.

**Visualización**: formulario de login único sin registro público. Tras autenticarse, un overlay muestra el rol y la sucursal antes de redirigir al panel principal.

### 5.2.2 Ingreso con Lote (RF04, RF08)

El formulario de ingreso permite registrar entrada de stock. El operador ingresa SKU (o se crea automáticamente si no existe), cantidad, y opcionalmente un número de lote. Sección colapsable permite ingresar datos del proveedor (RUT, nombre, dirección, teléfono, email).

**Flujo**:
1. Usuario ingresa SKU y cantidad.
2. Opcional: ingresa número de lote y datos del proveedor.
3. Sistema verifica si el SKU existe en la sucursal. Si no, lo crea.
4. Si existe, incrementa el stock.
5. Si se ingresó lote, registra en tabla independiente `Lotes`.
6. Registra la transacción en `Transacciones` con tipo "ingreso".

### 5.2.3 Salida/POS con Alerta Automática (RF01, RF02)

El endpoint unificado `POST /api/salida` procesa tanto salidas de inventario como ventas POS. Acepta un campo `tipo` ("salida" o "pos") y una `cantidad` variable.

**Flujo**:
1. Usuario selecciona SKU, ingresa cantidad y tipo de operación.
2. Opcional: ingresa datos del comprador.
3. Sistema verifica stock suficiente en la sucursal.
4. Descuenta stock y registra la transacción.
5. **Si el stock resultante ≤ stock mínimo**, se dispara la alerta:
   - Registro en `RegistroAlerta`.
   - Email a Proveedor y Gerente vía Resend API.
   - Webhook HTTP a URL configurable.
6. Muestra mensaje de confirmación con stock restante.

**Visualización**: los productos con stock crítico se resaltan en rojo en la tabla de Stock. El sidebar muestra un badge con el conteo total de alertas activas.

### 5.2.4 Dashboard con KPIs (RF03)

El dashboard presenta una visión ejecutiva del estado del inventario:

- **Total de productos** en la sucursal (o global).
- **Productos críticos** (stock ≤ mínimo).
- **Despachos pendientes**.
- **Top 5 productos** por rotación (movimientos).
- **Últimas 10 alertas** generadas.

El dashboard se filtra automáticamente por la sucursal del usuario (o por el selector en caso del admin).

### 5.2.5 Transferencia entre Sucursales (RF17)

Solo disponible para administradores. Permite mover stock de una sucursal a otra:

1. Admin selecciona SKU, sucursal origen, sucursal destino y cantidad.
2. Sistema verifica: sucursales existen, son distintas, hay stock suficiente en origen.
3. Descuenta stock de origen.
4. Incrementa (o crea) stock en destino.
5. Registra dos transacciones: `transferencia_salida` (origen) y `transferencia_entrada` (destino), cada una visible en el historial de su respectiva sucursal.

## 5.3 Funcionalidad In Situ: Ciclo Completo de Venta POS

A continuación se describe en detalle el flujo completo de una venta POS, desde que el trabajador accede al sistema hasta que se genera una alerta de stock bajo.

### Paso 1: Ingreso al Sistema
El trabajador abre `http://localhost:8000/login` e ingresa sus credenciales. El sistema valida contra la BD, genera un JWT con expiración 24h, y redirige al panel principal mostrando solo las secciones habilitadas para su rol.

### Paso 2: Navegación a Salida/POS
En el sidebar, el trabajador hace clic en "Salida / POS". La sección muestra un formulario con:
- Campo SKU (texto)
- Campo Cantidad (number, > 0)
- Selector Tipo: "Salida" o "POS"
- Sección colapsable "Datos del Comprador" con RUT, nombre, dirección, teléfono, email

### Paso 3: Procesar la Venta
El trabajador ingresa SKU="LECHE-001", cantidad=5, tipo="pos", completa datos del comprador y presiona "Procesar". El frontend envía `POST /api/salida` con el token JWT en el header.

### Paso 4: Validación y Descuento
El backend:
1. Extrae `sucursal_id` del token (el trabajador solo puede operar en su sucursal).
2. Busca el producto con `sku="LECHE-001"` y `sucursal_id=X`.
3. Verifica `stock >= 5`. Si es suficiente, descuenta: `stock -= 5`, `movimientos += 5`.
4. Registra transacción con tipo "pos", los datos del comprador, y `created_by=username`.

### Paso 5: Verificación de Alerta
Si el stock resultante (ej: 3) es ≤ stock mínimo (ej: 10), el sistema:
1. Crea un registro en `RegistroAlerta` con el mensaje de alerta.
2. Envía email vía Resend a `PROVEEDOR_EMAIL` y `GERENTE_EMAIL`.
3. Envía webhook HTTP a `WEBHOOK_URL` (si está configurada).

### Paso 6: Retroalimentación al Usuario
El frontend muestra "Venta POS exitosa. Stock restante: 3". El badge de notificaciones en el sidebar se actualiza (polling cada 30s) para reflejar el nuevo producto crítico.

## 5.4 Diseño de la Interfaz

El diseño visual sigue una paleta **oscura (slate blue)** con los siguientes principios:

- **Consistencia**: todas las secciones usan el mismo sistema de tarjetas (`content-card`), tablas (`tabla-datos`) y botones.
- **Jerarquía visual**: el sidebar siempre visible indica la sección activa. El header muestra usuario, rol y selector de sucursal.
- **Feedback inmediato**: botones con hover states, transiciones suaves, mensajes de éxito/error con temporizador.
- **Responsive**: grid adaptable, sidebar colapsable en mobile, tablas con scroll horizontal.
- **Accesibilidad**: contraste suficiente, labels semánticos, iconos decorativos con `data-lucide`.

### Patrón de diseño por sección

Cada sección sigue la estructura:
```
┌──────────────────────────────────────────┐
│  Card Header: Título + Botón acción      │
├──────────────────────────────────────────┤
│  Card Body: Formulario o Tabla           │
│  (overflow-x:auto para tablas)           │
└──────────────────────────────────────────┘
```

### Tecnologías visuales
- **Fuente**: Outfit (Google Fonts) para texto limpio y moderno.
- **Iconos**: Lucide (vía CDN, 28kb) reemplaza imágenes raster.
- **Animaciones**: CSS `@keyframes` para fadeIn y slideIn de paneles.
- **Glassmorphism**: `backdrop-filter: blur()` en tarjetas y sidebar.
