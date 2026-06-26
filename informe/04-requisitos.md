# 4. Análisis de Requisitos

## 4.1 Actores del Sistema

| Actor | Descripción | Permisos |
|-------|-------------|----------|
| **Administrador** | Usuario con acceso global al sistema. Gestiona sucursales, usuarios y puede visualizar y operar sobre cualquier sucursal. | CRUD de usuarios, CRUD de sucursales, transferencias entre sucursales, filtro global por sucursal, acceso a todas las secciones. |
| **Trabajador** | Usuario asignado a una sucursal específica. Opera exclusivamente sobre los datos de su sucursal más los productos globales. | Ingreso, salida/POS, despachos, consulta de stock e historial (solo su sucursal + globales). |
| **Sistema** | Actor automatizado que monitorea el stock y dispara notificaciones cuando se detectan condiciones críticas. | Sin interfaz de usuario. Ejecuta alertas email + webhook, actualiza dashboard. |

## 4.2 Requisitos Funcionales

| ID | Nombre | Actor | Descripción |
|----|--------|-------|-------------|
| RF01 | Descuento en Tiempo Real | Trabajador, Admin | Procesar salidas y ventas POS descontando stock instantáneamente. |
| RF02 | Notificación de Umbral Mínimo | Sistema | Alertar vía email y webhook cuando stock ≤ stock mínimo. |
| RF03 | Dashboard de Gestión | Admin, Trabajador | Visualizar KPIs, top rotación y alertas recientes. |
| RF04 | Ingreso e Indexación de Lotes | Trabajador, Admin | Registrar entrada de stock con lote opcional. |
| RF05 | Autenticación y Control de Acceso | Admin, Trabajador | Login JWT con roles y protección de rutas. |
| RF06 | Gestión de Usuarios | Admin | CRUD de usuarios del sistema. |
| RF07 | Gestión de Sucursales | Admin | CRUD de sucursales con validación de integridad. |
| RF08 | Datos de Proveedor/Comprador | Trabajador, Admin | Capturar RUT, nombre, dirección, teléfono y email en transacciones. |
| RF09 | Gestión de Despachos | Trabajador, Admin | Crear, listar y completar despachos pendientes. |
| RF10 | Consulta de Stock en Vivo | Admin, Trabajador | Visualizar stock actual con resaltado de productos críticos. |
| RF11 | Filtro por Sucursal | Admin | Filtrar datos por sucursal con inclusión de registros globales. |
| RF12 | Seed Automático de Admin | Sistema | Crear usuario admin por defecto al iniciar. |
| RF13 | Página de Login | Admin, Trabajador | Interfaz de inicio de sesión única sin registro público. |
| RF14 | Interfaz Principal | Admin, Trabajador | UI con 9 secciones y navegación por rol. |
| RF15 | Wizard de Configuración Inicial | Admin | Guía para crear la primera sucursal. |
| RF16 | Protección de Rutas | Sistema | Middleware JWT + require_admin() para endpoints administrativos. |
| RF17 | Transferencias entre Sucursales | Admin | Mover stock entre sucursales con registro contable doble. |
| RF20 | Exportación CSV | Admin, Trabajador | Descargar tablas como archivo CSV. |
| RF23 | Notificaciones en UI | Sistema | Badge numerado en sidebar con alertas activas. |
| RF24 | Pista de Auditoría | Sistema | Registro de creador y modificador en todas las entidades. |

## 4.3 Requisitos No Funcionales

| ID | Nombre | Descripción |
|----|--------|-------------|
| RNF01 | Latencia | Tiempo de respuesta monitoreado vía header X-Response-Time-Ms. Alerta en consola si supera 500ms. |
| RNF02 | Alta Disponibilidad | Endpoint /health público con uptime SLA 99.9%. Sin dependencias externas para health check. |
| RNF03 | Seguridad | JWT HS256 + SHA-256 con salt. Roles admin/trabajador. Token expiración 24h configurable. |
| RNF04 | Base de Datos | SQLAlchemy ORM con foreign keys. Preparado para migrar a PostgreSQL. |
| RNF05 | Stack Tecnológico | Python 3.12+ / FastAPI / SQLAlchemy / PyJWT / Resend / HTML+CSS+JS vanilla. |
| RNF06 | Diseño UI/UX | Tema oscuro responsive. Glassmorphism, animaciones, resaltado de filas críticas. |
| RNF07 | Mantenibilidad | Código modular. Variables de entorno para configuración sensible. Seed automático. |
| RNF08 | Cobertura de Pruebas | 42 tests automatizados (pytest) cubriendo todos los RF. |
