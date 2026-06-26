# A.2 Modelo Entidad-Relación

## Entidades y Atributos

### Sucursal (`sucursales`)
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id (PK) | INTEGER | Identificador único |
| nombre | VARCHAR (unique) | Nombre de la sucursal |
| direccion | VARCHAR | Dirección física |
| created_at | DATETIME | Fecha de creación |
| created_by | VARCHAR | Usuario que creó |
| updated_by | VARCHAR | Último usuario en modificar |
| updated_at | DATETIME | Fecha de última modificación |

### Usuario (`usuarios`)
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id (PK) | INTEGER | Identificador único |
| username | VARCHAR (unique) | Nombre de usuario |
| password_hash | VARCHAR | Hash SHA-256 + salt |
| rol | VARCHAR | "admin" o "trabajador" |
| sucursal_id (FK) | INTEGER → Sucursal.id | Sucursal asignada (nullable para admin) |
| created_at | DATETIME | Fecha de creación |

### Producto (`productos`)
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id (PK) | INTEGER | Identificador único |
| sku | VARCHAR (index) | Código del producto |
| nombre | VARCHAR | Nombre del producto |
| stock | INTEGER | Cantidad actual |
| stock_minimo | INTEGER | Umbral para alertas |
| movimientos | INTEGER | Contador de rotación |
| sucursal_id (FK) | INTEGER → Sucursal.id | Sucursal dueña (NULL = global) |
| created_by | VARCHAR | Usuario que creó |
| updated_by | VARCHAR | Último usuario en modificar |

### Lote (`lotes`)
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id (PK) | INTEGER | Identificador único |
| sku | VARCHAR (index) | Código del producto |
| numero_lote | VARCHAR | Número de lote |
| cantidad | INTEGER | Cantidad ingresada |
| sucursal_id (FK) | INTEGER → Sucursal.id | Sucursal |
| fecha_ingreso | DATETIME | Fecha de registro |

### Transacción (`transacciones`)
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id (PK) | INTEGER | Identificador único |
| sku | VARCHAR (index) | Código del producto |
| tipo | VARCHAR | "ingreso", "salida", "pos", "transferencia_salida", "transferencia_entrada" |
| cantidad | INTEGER | Cantidad movida |
| stock_resultante | INTEGER | Stock después de la operación |
| lote | VARCHAR | Número de lote (si aplica) |
| destino | VARCHAR | Destino (despachos/transferencias) |
| sucursal_id (FK) | INTEGER → Sucursal.id | Sucursal donde ocurrió |
| fecha | DATETIME | Fecha y hora |
| created_by | VARCHAR | Usuario que realizó la operación |
| proveedor_rut | VARCHAR | RUT del proveedor |
| proveedor_nombre | VARCHAR | Nombre del proveedor |
| proveedor_direccion | VARCHAR | Dirección del proveedor |
| proveedor_telefono | VARCHAR | Teléfono del proveedor |
| proveedor_email | VARCHAR | Email del proveedor |
| comprador_rut | VARCHAR | RUT del comprador |
| comprador_nombre | VARCHAR | Nombre del comprador |
| comprador_direccion | VARCHAR | Dirección del comprador |
| comprador_telefono | VARCHAR | Teléfono del comprador |
| comprador_email | VARCHAR | Email del comprador |

### Despacho Pendiente (`despachos_pendientes`)
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id (PK) | INTEGER | Identificador único |
| sku | VARCHAR (index) | Producto a despachar |
| destino | VARCHAR | Lugar de destino |
| cantidad | INTEGER | Cantidad a despachar |
| sucursal_id (FK) | INTEGER → Sucursal.id | Sucursal origen |
| estado | VARCHAR | "pendiente" o "completado" |
| fecha_creacion | DATETIME | Fecha de creación |
| created_by | VARCHAR | Usuario que creó |
| comprador_rut | VARCHAR | RUT del comprador |
| comprador_nombre | VARCHAR | Nombre del comprador |
| comprador_direccion | VARCHAR | Dirección del comprador |
| comprador_telefono | VARCHAR | Teléfono del comprador |
| comprador_email | VARCHAR | Email del comprador |

### Registro Alerta (`registro_alertas`)
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id (PK) | INTEGER | Identificador único |
| sku_producto | VARCHAR | Producto que generó la alerta |
| sucursal_id (FK) | INTEGER → Sucursal.id | Sucursal donde ocurrió |
| fecha | DATETIME | Fecha y hora |
| mensaje | VARCHAR | Descripción de la alerta |
| leida | BOOLEAN | Indica si fue revisada |
| created_by | VARCHAR | Usuario que generó (sistema) |

## Relaciones

```
Sucursal 1 ──── * Usuario         (una sucursal tiene muchos usuarios)
Sucursal 1 ──── * Producto        (una sucursal tiene muchos productos)
Sucursal 1 ──── * Lote            (una sucursal registra muchos lotes)
Sucursal 1 ──── * Transaccion     (una sucursal genera muchas transacciones)
Sucursal 1 ──── * DespachoPendiente (una sucursal gestiona muchos despachos)
Sucursal 1 ──── * RegistroAlerta  (una sucursal genera muchas alertas)
Producto  * ──── 1 Sucursal       (cada producto pertenece a una sucursal o es global)
```

**Nota**: los productos con `sucursal_id = NULL` son globales (creados por admin). No tienen relación foránea con Sucursal pero se incluyen en las consultas mediante `or_`.

## Instrucciones para dibujar en Draw.io

1. Crear 7 rectángulos de entidad con sus nombres.
2. Dentro de cada rectángulo, listar los atributos. Marcar (PK) para llaves primarias y (FK) para llaves foráneas.
3. Conectar las entidades con líneas y rombos:
   - Sucursal ── 1 ──◊── * ── Usuario
   - Sucursal ── 1 ──◊── * ── Producto
   - (productos globales son la excepción: sin conexión)
4. Usar colores para distinguir: entidades principales (azul), atributos (blanco), PK (negrita), FK (cursiva).
