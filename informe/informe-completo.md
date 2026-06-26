# Sistema de Alertas Logísticas y Control de Inventario (SALCI)

**Curso**: Análisis y Diseño de Sistemas
**Fecha**: Junio 2026
**Integrantes**: [Nombre1, Nombre2, Nombre3, Nombre4]

---

> Este documento compila todas las secciones del informe. Copia cada sección a tu editor de PDF.
> Los archivos individuales están en las carpetas `informe/` y `informe/anexos/`.

---

# 1. Introducción

El presente informe documenta el análisis, diseño e implementación del **Sistema de Alertas Logísticas y Control de Inventario (SALCI)**, desarrollado como proyecto del curso Análisis y Diseño de Sistemas.

SALCI es una plataforma web diseñada para resolver problemas de gestión de inventario en pequeñas y medianas empresas (PyMEs) que operan con múltiples sucursales. El sistema permite el control de stock en tiempo real, la generación automática de alertas de reabastecimiento vía email y webhook, y la segmentación de datos por sucursal con roles diferenciados (administrador global y trabajador por sucursal).

El documento cubre todas las etapas del ciclo de vida del sistema: análisis de contexto, planificación, requisitos, modelado, diseño de la solución, y una evaluación ética y legal del proyecto. Se incluyen además anexos con diagramas y prototipos.

---

# 2. Análisis de Contexto

## 2.1 El Problema

Las PyMEs con múltiples sucursales enfrentan desafíos críticos en la gestión de inventario: desconocimiento del stock real en cada ubicación, demoras en la detección de faltantes, procesos manuales propensos a errores, y ausencia de trazabilidad en las transacciones. Estos problemas generan pérdidas económicas por quiebres de stock, exceso de inventario o vencimientos no detectados.

## 2.2 La Solución Propuesta

SALCI es un sistema web de gestión de inventario multi-sucursal que ofrece:

- **Control de stock en tiempo real**: cada ingreso, salida o venta POS actualiza instantáneamente el inventario.
- **Alertas automáticas de reabastecimiento**: cuando un producto cae bajo su stock mínimo, se notifica vía email (Resend) y webhook.
- **Segmentación por sucursal**: cada trabajador opera exclusivamente sobre los datos de su sucursal, mientras el administrador tiene visión global con filtro por sucursal.
- **Trazabilidad completa**: todas las transacciones quedan registradas con datos del proveedor/comprador, fechas y responsable.
- **Dashboard ejecutivo**: KPIs de rotación, productos críticos y despachos pendientes.
- **Transferencias entre sucursales**: movimiento de stock entre ubicaciones con registro contable doble.

## 2.3 Objetivos

**Objetivo General:**
Desarrollar un sistema de información que permita a PyMEs con múltiples sucursales gestionar su inventario de forma centralizada, automatizada y trazable.

**Objetivos Específicos:**
1. Proveer una interfaz web responsiva accesible desde cualquier dispositivo.
2. Automatizar la detección y notificación de stock crítico.
3. Garantizar la segmentación de datos por sucursal con roles de acceso diferenciados.
4. Mantener un historial completo y auditable de todas las transacciones.
5. Permitir transferencias de stock entre sucursales con registro contable.

## 2.4 Relevancia

En Chile, las PyMEs representan el 98% de las empresas y generan el 65% del empleo. Muchas operan con sucursales múltiples pero carecen de sistemas integrados de inventario, dependiendo de planillas Excel y comunicación telefónica. SALCI aborda esta brecha con una solución de bajo costo (stack open-source, SQLite embebido) y fácil despliegue.

---

# 3. Planificación

## 3.1 Ciclo de Vida del Sistema

Se adoptó un **ciclo de vida iterativo-incremental**, donde cada iteración produce un incremento funcional del sistema. Este enfoque permite obtener retroalimentación temprana y ajustar requisitos sobre la marcha.

| Fase | Descripción |
|------|-------------|
| **Análisis** | Identificación de requisitos funcionales y no funcionales a partir del problema planteado. Definición de actores y casos de uso. |
| **Diseño** | Arquitectura del sistema (FastAPI + SQLAlchemy + SQLite), diseño de la base de datos (Modelo Entidad-Relación), diseño de interfaz (HTML+CSS+JS vanilla, tema oscuro). |
| **Implementación** | Codificación incremental por sprint: cada sprint agrega entre 2 y 4 RF completos. |
| **Pruebas** | Pruebas automatizadas con pytest para cada RF implementado. 42 tests al final del proyecto. |

## 3.2 Metodología de Desarrollo

Se seleccionó una **metodología ágil adaptada (Scrum simplificado)** por las siguientes razones:

- El sistema involucró requisitos que evolucionaron durante el desarrollo (ej: se agregaron RF17, RF20, RF23, RF24 en etapas tardías).
- Se requería retroalimentación continua sobre la usabilidad de la interfaz.
- El equipo era pequeño (4 personas), ideal para ciclos cortos con reuniones sincrónicas mínimas.

**Justificación frente a alternativas:**
- **Cascada**: descartada porque los requisitos no estaban completamente definidos al inicio (ej: el filtro por sucursal con inclusión de registros globales surgió durante pruebas).
- **Prototipado**: usado de forma complementaria para la interfaz de usuario, pero no como metodología principal por la falta de estructura formal.

## 3.3 Planificación Temporal

El proyecto se desarrolló en 7 sprints de 1 semana cada uno:

| Sprint | Período | Entregable |
|--------|---------|------------|
| **Sprint 1** | Semana 1 | RF01-RF04: endpoints de stock (ingreso, salida, POS, alerta), health check. |
| **Sprint 2** | Semana 2 | RF05-RF07: autenticación JWT, roles, CRUD de usuarios y sucursales. |
| **Sprint 3** | Semana 3 | RF08-RF11: datos de proveedor/comprador, filtro por sucursal, dashboard. |
| **Sprint 4** | Semana 4 | RF12-RF16: seed admin, página login, interfaz principal, wizard, protección rutas. |
| **Sprint 5** | Semana 5 | Pruebas de integración, corrección de bugs (filtro con or_ para globales, sucursal en dashboard). |
| **Sprint 6** | Semana 6 | RF17 (transferencias), RF24 (auditoría), RF20 (exportación CSV), RF23 (notificaciones UI). |
| **Sprint 7** | Semana 7 | Documentación (REQUIREMENTS.md, README.md), tests finales (42 tests), preparación del informe. |

### Hitos

| Hito | Fecha | Criterio de éxito |
|------|-------|-------------------|
| MVP funcional | Fin Sprint 3 | CRUD completo de stock + auth + sucursales |
| Sistema completo | Fin Sprint 5 | Todos los RF originales funcionando + tests pasando |
| Versión extendida | Fin Sprint 6 | 4 nuevos RF implementados |
| Entrega | Fin Sprint 7 | Informe, diagramas y presentación |

## 3.4 Herramientas Utilizadas

| Herramienta | Versión | Uso |
|-------------|---------|-----|
| Python | 3.12 | Lenguaje de programación |
| FastAPI | 0.115 | Framework web REST |
| Uvicorn | 0.34 | Servidor ASGI |
| SQLAlchemy | 2.0 | ORM y mapeo objeto-relacional |
| SQLite | 3.x | Motor de base de datos embebido |
| PyJWT | 2.10 | Creación y validación de tokens JWT |
| Resend | SDK | Envío de emails transaccionales |
| pytest | 9.x | Framework de pruebas unitarias |
| httpx | 0.x | Cliente HTTP para tests |
| Git | — | Control de versiones |

---

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

---

# 5. Diseño de la Solución

## 5.1 Arquitectura del Sistema

El sistema sigue una arquitectura **cliente-servidor de tres capas**:

```
  ┌─────────────────────────────────────┐
  │          Cliente Web                │
  │  (HTML + CSS + JavaScript + Lucide) │
  └──────────────┬──────────────────────┘
                 │ HTTP (JSON)
                 ▼
  ┌─────────────────────────────────────┐
  │       Servidor (FastAPI)            │
  │  ┌─────────┐ ┌───────┐ ┌─────────┐ │
  │  │REST API │ │JWT    │ │Lógica   │ │
  │  │Endpoints│ │Auth   │ │Negocio  │ │
  │  └─────────┘ └───────┘ └─────────┘ │
  └──────────────┬──────────────────────┘
                 │ SQLAlchemy ORM
                 ▼
  ┌─────────────────────────────────────┐
  │      Base de Datos (SQLite)         │
  │  7 tablas con foreign keys          │
  └─────────────────────────────────────┘
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

| Indicador | Fuente |
|-----------|--------|
| Total de productos | Conteo de Producto (según filtro) |
| Productos críticos | Productos con stock ≤ stock_minimo |
| Despachos pendientes | DespachoPendiente con estado="pendiente" |
| Top 5 rotación | Productos ordenados por movimientos DESC |
| Últimas 10 alertas | RegistroAlerta ordenado por fecha DESC |

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
- **Accesibilidad**: contraste suficiente, labels semánticos, iconos decorativos.

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

---

# 6. Análisis Ético y Legal

## 6.1 Consideraciones Éticas

**Neutralidad tecnológica**: SALCI es un sistema de gestión de inventario que no discrimina entre tipos de productos, proveedores o clientes. El sistema trata todos los SKU, sucursales y transacciones de manera uniforme, sin sesgos algorítmicos ni decisiones automatizadas que puedan perjudicar a personas.

**Responsabilidad profesional**: como desarrolladores, asumimos la responsabilidad de que el sistema funcione correctamente. Las alertas de stock bajo son informativas y no ejecutan órdenes de compra automáticas; la decisión final de reabastecer recae siempre en un humano. Esto evita riesgos de compras no deseadas por errores en los datos.

**Transparencia**: el sistema registra todas las transacciones con datos completos (quién, qué, cuándo, dónde). Cualquier auditoría puede reconstruir el historial completo de movimientos de cada producto. Los campos de auditoría (created_by, updated_by) garantizan la trazabilidad de cada acción.

## 6.2 Privacidad y Confidencialidad de los Datos

El sistema almacena datos personales de proveedores y compradores (RUT, nombre, dirección, teléfono, email). Se implementan las siguientes medidas:

- **Autenticación obligatoria**: todos los endpoints (excepto /health y /login) requieren JWT válido.
- **Segmentación por rol**: los trabajadores solo acceden a datos de su sucursal.
- **Hashing de contraseñas**: SHA-256 con salt, sin almacenamiento en texto plano.
- **Protección del último admin**: no se puede eliminar el único administrador del sistema.

**Cumplimiento legal (Ley 19.628 - Chile)**: la ley chilena de protección de datos personales exige:
- **Consentimiento**: los datos de proveedores/compradores se capturan con su conocimiento directo (ingresados por el operador en el momento de la transacción).
- **Finalidad**: los datos se usan exclusivamente para la gestión de inventario y contacto logístico.
- **Proporcionalidad**: solo se almacenan los datos mínimos necesarios para la operación (RUT, nombre, datos de contacto).
- **Seguridad**: acceso restringido por autenticación y roles.

Se recomienda que la empresa implemente una **política de retención de datos** que elimine registros de transacciones anteriores a 5 años.

## 6.3 Impacto Social y Ambiental

**Impacto social positivo**:
- Reduce la carga laboral de trabajadores que antes gestionaban inventario manualmente.
- Disminuye errores humanos en el conteo y registro de stock.
- Facilita la toma de decisiones informadas para dueños de PyMEs.

**Impacto ambiental**:
- Al optimizar el inventario y reducir quiebres de stock, se disminuye el desperdicio de productos perecibles.
- Al ser un sistema web liviano (sin bases de datos masivas ni infraestructura cloud pesada), el consumo energético es mínimo.
- La opción de SQLite embebido evita la necesidad de servidores de base de datos adicionales.

## 6.4 No Discriminación

El sistema no discrimina por ningún motivo: todos los usuarios con el mismo rol tienen las mismas funcionalidades independientemente de la sucursal a la que pertenezcan. No hay sesgos de género, etnia, religión o nivel educativo en el diseño de la interfaz (uso de iconos universales, texto en español neutro).

## 6.5 Uso Responsable de IA

El sistema **no incorpora inteligencia artificial** ni algoritmos de machine learning. Todas las decisiones (descuento de stock, alertas, filtros) son deterministas y basadas en reglas explícitas. Esto elimina riesgos de sesgos algorítmicos, cajas negras o decisiones no explicables.

---

# 7. Recomendaciones del Ingeniero Informático

Basado en incidentes reales ocurridos durante el desarrollo del proyecto, se presentan las siguientes recomendaciones.

## 7.1 Evento 1: Fallo de Dependencia Tercerizada (bcrypt)

**Problema**: la librería `passlib` con `bcrypt` fallaba en Windows debido a problemas de compilación de dependencias nativas, bloqueando el login durante 2 días.

**Solución**: se reemplazó bcrypt por `hashlib.sha256` con salt configurable (`PWD_SALT`), eliminando la dependencia problemática.

**Recomendación**: verificar que todas las dependencias críticas funcionen en el SO objetivo. Preferir bibliotecas Python puras sobre extensiones C cuando la portabilidad importe.

## 7.2 Evento 2: Token de Simulación Heredado

**Problema**: el código contenía un token de simulación fijo (`simulacion-jwt-token-123`) que permitía acceso admin sin autenticación real. Riesgo de seguridad si se olvidaba en producción.

**Solución**: se mantuvo solo para TestClient. En producción, el JWT_SECRET diferente invalida el token de simulación.

**Recomendación**: nunca incluir backdoors o tokens fijos en código que pueda llegar a producción. Usar variables de entorno para diferenciar entornos.

## 7.3 Evento 3: Trabajador No Veía Productos Globales

**Problema**: al filtrar por sucursal, los trabajadores no veían productos globales del admin, dejando vistas vacías.

**Solución**: modificar todos los endpoints para usar `or_(sucursal_id == X, sucursal_id.is_(None))`.

**Recomendación**: al diseñar sistemas multi-tenant, considerar desde el inicio el modelo de datos para registros "globales" vs "específicos".

## 7.4 Recomendaciones Generales

1. **Pruebas automatizadas desde el día 1**: detectan regresiones antes de que lleguen a producción.
2. **BD liviana**: SQLite es adecuado para PyMEs (< 10 sucursales); migrar a PostgreSQL si escala.
3. **Capacitación**: guía rápida de uso y sesión de 30 min para nuevos trabajadores.
4. **Respaldos**: copia periódica de `logistica.db` a servicio cloud.

---

# 8. Conclusión

## 8.1 Lecciones Aprendidas

- **Los requisitos evolucionan**: de 16 RF iniciales a 20 RF finales. La metodología ágil permitió incorporarlos sin afectar el cronograma.
- **Las pruebas son un multiplicador de calidad**: 42 tests detectaron regresiones, especialmente en el filtro por sucursal.
- **El diseño de BD debe considerar la segmentación desde el inicio**: `sucursal_id` en todas las tablas fue acertado, pero los globales (`IS NULL`) requirieron ajustes.
- **La ética no es un añadido**: el análisis reveló aspectos (Ley 19.628, transparencia) no considerados inicialmente.

## 8.2 Cumplimiento de Objetivos

| Objetivo | Estado | Evidencia |
|----------|--------|-----------|
| Interfaz web responsiva | ✅ | HTML+CSS+JS vanilla, responsive design |
| Alertas automáticas | ✅ | Email + Webhook + Dashboard |
| Segmentación por sucursal | ✅ | Roles admin/trabajador, filtro con or_ |
| Historial auditable | ✅ | 20 campos por transacción + created_by |
| Transferencias entre sucursales | ✅ | Endpoint con registro contable doble |

Todos los objetivos fueron cumplidos y validados mediante 42 pruebas automatizadas.

## 8.3 Reflexión sobre el Trabajo Colaborativo

- **División**: backend, frontend, tests, documentación — trabajo en paralelo sin conflictos.
- **Comunicación**: reuniones diarias de 15 min, Discord + Git.
- **Ejemplo**: cuando el filtro no incluía globales, backend identificó el bug, frontend confirmó, tests lo reprodujeron, documentación lo registró. Todo en el mismo día.
- **Dificultad**: coordinación de horarios. Solución: horario fijo 20:00-21:30 (lun-jue) para trabajo sincrónico, fines de semana para asincrónico.

---

# Anexos

## A.1 Diagrama de Casos de Uso

Ver archivo: `anexos/a1-diagrama-casos-de-uso.md`

### Actores
- **Administrador**: gestiona usuarios, sucursales, transferencias, filtra por sucursal.
- **Trabajador**: gestiona stock y despachos de su sucursal.
- **Sistema**: autentica, notifica stock bajo, registra transacciones.

### Casos de Uso (19 total)
| # | Caso de Uso | Actor |
|---|-------------|-------|
| 1 | Iniciar Sesión | Admin, Trabajador |
| 2 | Gestionar Usuarios | Admin |
| 3 | Gestionar Sucursales | Admin |
| 4 | Transferir Stock | Admin |
| 5 | Filtrar por Sucursal | Admin |
| 6 | Gestionar Stock | Admin, Trabajador |
| 7 | Gestionar Despachos | Admin, Trabajador |
| 8 | Ver Dashboard | Admin, Trabajador |
| 9 | Exportar CSV | Admin, Trabajador |
| 10 | Consultar Stock | Admin, Trabajador |
| 11 | Autenticar Usuario | Sistema |
| 12 | Notificar Stock Bajo | Sistema |
| 13 | Registrar Transacción | Sistema |
| 14 | Actualizar Dashboard | Sistema |

## A.2 Modelo Entidad-Relación

Ver archivo: `anexos/a2-modelo-entidad-relacion.md`

### Entidades (7)
- **Sucursal** — nombre, direccion, created_by, updated_by
- **Usuario** — username, password_hash, rol, sucursal_id (FK)
- **Producto** — sku, nombre, stock, stock_minimo, movimientos, sucursal_id (FK), created_by, updated_by
- **Lote** — sku, numero_lote, cantidad, sucursal_id (FK), fecha_ingreso
- **Transaccion** — sku, tipo, cantidad, stock_resultante, sucursal_id (FK), created_by, datos proveedor/comprador
- **DespachoPendiente** — sku, destino, cantidad, sucursal_id (FK), estado, created_by, datos comprador
- **RegistroAlerta** — sku_producto, sucursal_id (FK), mensaje, leida, created_by

### Relaciones principales
- Sucursal 1──* Usuario
- Sucursal 1──* Producto (Producto.sucursal_id nullable = global)
- Sucursal 1──* Transaccion
- Sucursal 1──* DespachoPendiente
- Sucursal 1──* RegistroAlerta
- Sucursal 1──* Lote
