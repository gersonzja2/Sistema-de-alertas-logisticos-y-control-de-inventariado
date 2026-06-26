# A.1 Diagrama de Casos de Uso

## Actores

| Actor | Representación |
|-------|---------------|
| **Administrador** | Figura humana con etiqueta "Administrador" |
| **Trabajador** | Figura humana con etiqueta "Trabajador" |
| **Sistema** | Figura humana con etiqueta "Sistema" (o rectángulo con «actor») |

## Casos de Uso

### Administrador
1. **Iniciar Sesión** — el admin ingresa credenciales para acceder al sistema.
2. **Gestionar Usuarios** — crear, listar y eliminar usuarios del sistema.
3. **Gestionar Sucursales** — crear, editar y eliminar sucursales.
4. **Transferir Stock** — mover productos entre sucursales.
5. **Filtrar por Sucursal** — seleccionar una sucursal para ver sus datos.
6. **Gestionar Stock** — realizar ingreso, salida y venta POS en cualquier sucursal.
7. **Gestionar Despachos** — crear y completar despachos pendientes.
8. **Ver Dashboard** — visualizar KPIs y alertas globales.
9. **Exportar CSV** — descargar tablas como archivo CSV.

### Trabajador
10. **Iniciar Sesión** — el trabajador ingresa credenciales para acceder al sistema.
11. **Gestionar Stock (propio)** — realizar ingreso, salida y venta POS en su sucursal.
12. **Gestionar Despachos (propios)** — crear y completar despachos de su sucursal.
13. **Ver Dashboard (propio)** — visualizar KPIs de su sucursal.
14. **Consultar Stock** — ver productos de su sucursal + globales.
15. **Exportar CSV** — descargar datos de su sucursal.

### Sistema
16. **Autenticar Usuario** — validar credenciales y generar JWT.
17. **Notificar Stock Bajo** — enviar email y webhook cuando stock ≤ mínimo.
18. **Registrar Transacción** — almacenar cada operación con trazabilidad.
19. **Actualizar Dashboard** — recalcular KPIs en cada transacción.

## Relaciones (Include/Extend)

- "Gestionar Stock" **incluye** "Registrar Transacción" (cada operación de stock genera un registro).
- "Gestionar Stock" **extiende** "Notificar Stock Bajo" (solo si stock ≤ mínimo).
- "Iniciar Sesión" **incluye** "Autenticar Usuario".
- "Transferir Stock" **incluye** "Gestionar Stock" (usa la misma lógica de descuento/ingreso).

## Instrucciones para dibujar en Draw.io

1. Crear 3 actores (figuras humanas): Administrador, Trabajador, Sistema.
2. Crear un rectángulo "Sistema SALCI".
3. Dentro del rectángulo, agregar 19 elipses para los casos de uso.
4. Conectar actores con casos de uso mediante líneas.
5. Agregar flechas punteadas con estereotipos `<<include>>` y `<<extend>>` donde corresponda.
6. Colocar al Administrador a la izquierda, Trabajador a la derecha, Sistema abajo.
