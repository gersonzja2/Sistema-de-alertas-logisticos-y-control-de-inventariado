// Función para cambiar de pestañas en la UI y actualizar estilos de navegación
function mostrarSeccion(id) {
    // Cambiar paneles visibles
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('activo'));
    const panelActivo = document.getElementById(id);
    if (panelActivo) {
        panelActivo.classList.add('activo');
    }
    
    // Actualizar estado activo en la barra lateral
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    const navItem = document.getElementById(`btn-nav-${id}`);
    if (navItem) {
        navItem.classList.add('active');
    }

    // Actualizar título y subtítulo de la cabecera
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.querySelector('.main-header .subtitle');
    
    if (id === 'dashboard') {
        pageTitle.innerText = "Panel de Control";
        pageSubtitle.innerText = "Monitoreo de SKUs y alertas críticas en tiempo real";
        cargarDashboard();
    } else if (id === 'ingreso') {
        pageTitle.innerText = "Recepción de Mercancía";
        pageSubtitle.innerText = "Entradas de stock y registro de inventario (RF04)";
    } else if (id === 'salida') {
        pageTitle.innerText = "Despacho / Punto de Venta";
        pageSubtitle.innerText = "Salidas de stock y alertas automáticas de reposición (RF01)";
    }
}

// RF03: Cargar datos del dashboard
async function cargarDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) throw new Error("Error en la respuesta del servidor");
        const data = await response.json();
        
        // Cargar KPIs
        document.getElementById('kpi-total').innerText = data.total_productos;
        document.getElementById('kpi-criticos').innerText = data.productos_criticos;
        
        // Cambiar estilos de las tarjetas si hay alertas críticas
        const criticoCard = document.getElementById('kpi-card-criticos');
        if (data.productos_criticos > 0) {
            criticoCard.classList.add('critico');
        } else {
            criticoCard.classList.remove('critico');
        }
        
        // Renderizar lista de alertas
        const lista = document.getElementById('lista-alertas');
        lista.innerHTML = '';
        
        if (data.alertas_recientes && data.alertas_recientes.length > 0) {
            data.alertas_recientes.forEach(alerta => {
                const li = document.createElement('li');
                // Formatear la fecha de ISO a un formato más amigable (DD/MM/YYYY HH:MM)
                let fechaFormateada = alerta.fecha;
                try {
                    const dateObj = new Date(alerta.fecha);
                    const dia = String(dateObj.getDate()).padStart(2, '0');
                    const mes = String(dateObj.getMonth() + 1).padStart(2, '0');
                    const anio = dateObj.getFullYear();
                    const horas = String(dateObj.getHours()).padStart(2, '0');
                    const mins = String(dateObj.getMinutes()).padStart(2, '0');
                    fechaFormateada = `${dia}/${mes}/${anio} ${horas}:${mins}`;
                } catch(e) {
                    fechaFormateada = alerta.fecha.substring(0, 16).replace('T', ' ');
                }
                
                li.innerHTML = `<div><strong>[${fechaFormateada}]</strong> ${alerta.mensaje}</div>`;
                lista.appendChild(li);
            });
        } else {
            // Mensaje cuando no hay alertas
            const li = document.createElement('li');
            li.style.borderLeftColor = 'var(--success)';
            li.style.backgroundColor = 'var(--success-glow)';
            li.innerHTML = `<div><span style="color: var(--success); font-weight: 600;">✔️ Sin Alertas Críticas:</span> Todos los SKUs tienen stock saludable.</div>`;
            lista.appendChild(li);
        }
    } catch (error) {
        console.error("Error cargando dashboard:", error);
    }
}

// RF01 y RF04: Procesar Ingresos y Salidas
async function procesarTransaccion(tipo) {
    const prefijo = tipo === 'ingreso' ? 'in' : 'out';
    const skuInput = document.getElementById(`${prefijo}-sku`);
    const cantInput = document.getElementById(`${prefijo}-cant`);
    const msgElement = document.getElementById(`msg-${tipo}`);

    const sku = skuInput.value.trim().toUpperCase();
    const cant = parseInt(cantInput.value);

    // Validaciones
    if (!sku) {
        mostrarMensaje(msgElement, "Error: El SKU es requerido.", "var(--danger)");
        return;
    }
    
    if (isNaN(cant) || cant <= 0) {
        mostrarMensaje(msgElement, "Error: La cantidad debe ser un número entero mayor a cero.", "var(--danger)");
        return;
    }

    try {
        msgElement.innerText = "Procesando...";
        msgElement.style.color = "var(--text-secondary)";
        
        // Petición al backend
        const response = await fetch(`/api/${tipo}`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                // RNF03: Simulación de token de seguridad
                'Authorization': 'Bearer simulacion-jwt-token-123' 
            },
            body: JSON.stringify({ sku: sku, cantidad: cant })
        });

        const result = await response.json();
        
        if (response.ok) {
            mostrarMensaje(msgElement, result.mensaje, "var(--success)");
            // Limpiar campos
            skuInput.value = '';
            cantInput.value = '';
        } else {
            // Manejar errores de validación HTTP o lógica del backend
            const errorMsg = result.detail ? result.detail : "Error al procesar la solicitud.";
            mostrarMensaje(msgElement, `Error: ${errorMsg}`, "var(--danger)");
        }
    } catch (error) {
        mostrarMensaje(msgElement, "Error de conexión con el servidor.", "var(--danger)");
    }
}

// Función auxiliar para mostrar mensajes de feedback
function mostrarMensaje(element, texto, color) {
    element.innerText = texto;
    element.style.color = color;
    element.style.opacity = 1;
    
    // Desvanecer el mensaje después de 5 segundos
    setTimeout(() => {
        if (element.innerText === texto) {
            element.style.opacity = 0;
            setTimeout(() => { element.innerText = ''; }, 300);
        }
    }, 5000);
}

// Cargar dashboard al iniciar
window.onload = () => {
    cargarDashboard();
};