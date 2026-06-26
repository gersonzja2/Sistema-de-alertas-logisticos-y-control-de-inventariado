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
