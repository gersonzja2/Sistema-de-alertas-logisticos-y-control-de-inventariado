let CURRENT_USER = null;

function getToken() {
    return localStorage.getItem('token');
}

function getAuth() {
    const token = getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function getUser() {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
}

function checkAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

async function cargarUserInfo() {
    if (!checkAuth()) return;
    try {
        const resp = await fetch('/api/auth/me', { headers: getAuth() });
        if (!resp.ok) { logout(); return; }
        const user = await resp.json();
        CURRENT_USER = user;
        localStorage.setItem('user', JSON.stringify(user));

        document.getElementById('sidebar-username').textContent = user.username;
        document.getElementById('header-username').textContent = user.username;

        const letter = user.username.charAt(0).toUpperCase();
        document.getElementById('user-avatar-letter').textContent = letter;

        const badge = document.getElementById('sidebar-role-badge');
        if (user.rol === 'admin') {
            badge.textContent = 'Admin';
            badge.className = 'user-badge badge-admin';
            document.getElementById('header-role-label').textContent = 'Administrador';
            document.getElementById('admin-nav-section').style.display = 'block';
            document.getElementById('sucursal-selector-container').style.display = 'block';
            cargarSucursalesSelect('admin-sucursal-filter');
        } else {
            badge.textContent = 'Trabajador';
            badge.className = 'user-badge badge-trabajador';
            document.getElementById('header-role-label').textContent = 'Trabajador';
            document.getElementById('admin-nav-section').style.display = 'none';
            document.getElementById('sucursal-selector-container').style.display = 'none';

            if (user.sucursal) {
                document.getElementById('header-role-label').textContent = `Trabajador — ${user.sucursal.nombre}`;
            }
        }
    } catch (e) {
        console.error('Error cargando usuario:', e);
        logout();
    }
}

// --- Navigation ---

function mostrarSeccion(id) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('activo'));
    const panelActivo = document.getElementById(id);
    if (panelActivo) panelActivo.classList.add('activo');

    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    const navItem = document.getElementById(`btn-nav-${id}`);
    if (navItem) navItem.classList.add('active');

    const pageTitle = document.getElementById('page-title');
    const subtitle = document.getElementById('page-subtitle');

    const titles = {
        'home': ['Inicio', 'Panel de bienvenida y acceso rápido'],
        'dashboard': ['Panel de Control', 'Monitoreo de SKUs, rotación y alertas críticas en tiempo real'],
        'ingreso': ['Recepción de Mercancía', 'Entradas de stock, registro de lotes y escaneo de código de barras'],
        'salida': ['Despacho / Punto de Venta (POS)', 'Salidas de stock con cantidad seleccionable por transacción'],
        'stock': ['Stock en Vivo', 'Consulta el stock actual de todos los productos al instante'],
        'historial': ['Historial de Transacciones', 'Registro completo de entradas y salidas del inventario'],
        'despachos': ['Despachos Pendientes', 'Gestión de despachos y estado de entregas'],
        'usuarios': ['Gestión de Usuarios', 'Administración de usuarios del sistema'],
        'sucursales': ['Gestión de Sucursales', 'Administración de sucursales y bodegas']
    };
    const t = titles[id] || ['Panel de Control', ''];
    pageTitle.innerText = t[0];
    subtitle.innerText = t[1];

    if (id === 'home') cargarHome();
    else if (id === 'dashboard') cargarDashboard();
    else if (id === 'stock') cargarStockVivo();
    else if (id === 'historial') cargarHistorial();
    else if (id === 'despachos') { cargarDespachos(); }
    else if (id === 'usuarios') { cargarUsuarios(); cargarSucursalesSelect('reg-sucursal'); }
    else if (id === 'sucursales') cargarSucursalesAdmin();
}

// --- Home / Welcome ---

async function cargarHome() {
    if (!CURRENT_USER) await cargarUserInfo();
    const user = CURRENT_USER;
    if (!user) return;

    document.getElementById('welcome-avatar').textContent = user.username.charAt(0).toUpperCase();
    document.getElementById('welcome-greeting').textContent = `¡Bienvenido, ${user.username}!`;

    const roleLabel = document.getElementById('welcome-role-label');
    const roleBadge = document.getElementById('welcome-role-badge');
    const sucursalBadge = document.getElementById('welcome-sucursal-badge');

    if (user.rol === 'admin') {
        roleLabel.textContent = 'Has iniciado sesión como Administrador';
        roleBadge.textContent = 'Administrador';
        roleBadge.className = 'user-badge badge-admin';
        sucursalBadge.style.display = 'none';
    } else {
        roleLabel.textContent = `Has iniciado sesión como Trabajador`;
        roleBadge.textContent = 'Trabajador';
        roleBadge.className = 'user-badge badge-trabajador';
        if (user.sucursal) {
            sucursalBadge.textContent = `📍 ${user.sucursal.nombre}`;
            sucursalBadge.style.display = 'inline-block';
            sucursalBadge.className = 'user-badge badge-trabajador';
        } else {
            sucursalBadge.style.display = 'none';
        }
    }

    const actionsContainer = document.getElementById('welcome-actions');
    actionsContainer.innerHTML = '';

    const actions = [];
    if (user.rol === 'admin') {
        actions.push(
            { icon: 'layout-dashboard', label: 'Ir al Dashboard', action: "mostrarSeccion('dashboard')", color: 'var(--accent-blue)', desc: 'Métricas y alertas del sistema' },
            { icon: 'building-2', label: 'Gestionar Sucursales', action: "mostrarSeccion('sucursales')", color: '#8b5cf6', desc: 'Crear y administrar bodegas' },
            { icon: 'users', label: 'Gestionar Usuarios', action: "mostrarSeccion('usuarios')", color: '#f97316', desc: 'Administrar trabajadores' },
            { icon: 'package', label: 'Stock en Vivo', action: "mostrarSeccion('stock')", color: '#10b981', desc: 'Inventario actual' }
        );
    } else {
        actions.push(
            { icon: 'layout-dashboard', label: 'Ir al Dashboard', action: "mostrarSeccion('dashboard')", color: 'var(--accent-blue)', desc: 'Métricas de tu sucursal' },
            { icon: 'package', label: 'Ver Stock', action: "mostrarSeccion('stock')", color: '#10b981', desc: 'Inventario de tu sucursal' },
            { icon: 'arrow-up-right', label: 'Salida / POS', action: "mostrarSeccion('salida')", color: '#ef4444', desc: 'Despachar o vender' },
            { icon: 'arrow-down-left', label: 'Ingresar Stock', action: "mostrarSeccion('ingreso')", color: 'var(--accent-blue)', desc: 'Recibir mercancía' }
        );
    }

    actions.forEach(a => {
        const card = document.createElement('div');
        card.className = 'content-card';
        card.style.cursor = 'pointer';
        card.style.transition = 'var(--transition)';
        card.onmouseover = () => { card.style.transform = 'translateY(-4px)'; card.style.borderColor = a.color; };
        card.onmouseout = () => { card.style.transform = ''; card.style.borderColor = ''; };
        card.onclick = () => { eval(a.action); };
        card.innerHTML = `
            <div class="card-body" style="display:flex;align-items:center;gap:16px;padding:20px;">
                <div style="width:44px;height:44px;border-radius:10px;background:${a.color}22;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                    <i data-lucide="${a.icon}" style="width:22px;height:22px;color:${a.color};"></i>
                </div>
                <div>
                    <strong style="font-size:1rem;">${a.label}</strong>
                    <p style="color:var(--text-secondary);font-size:0.85rem;margin-top:2px;">${a.desc}</p>
                </div>
            </div>
        `;
        actionsContainer.appendChild(card);
    });
    lucide.createIcons();

    // Check if admin needs first branch setup
    const setupDiv = document.getElementById('first-sucursal-setup');
    if (user.rol === 'admin') {
        try {
            const resp = await fetch('/api/sucursales', { headers: getAuth() });
            const data = await resp.json();
            if (!data.sucursales || data.sucursales.length === 0) {
                setupDiv.style.display = 'block';
            } else {
                setupDiv.style.display = 'none';
            }
        } catch (e) {
            setupDiv.style.display = 'none';
        }
    } else {
        setupDiv.style.display = 'none';
    }
}

async function crearPrimeraSucursal() {
    const nombre = document.getElementById('wizard-suc-nombre').value.trim();
    const direccion = document.getElementById('wizard-suc-direccion').value.trim();
    const msg = document.getElementById('msg-wizard-sucursal');
    if (!nombre) { mostrarMensaje(msg, "El nombre es requerido.", "var(--danger)"); return; }
    try {
        const resp = await fetch('/api/sucursales', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuth() },
            body: JSON.stringify({ nombre, direccion })
        });
        const result = await resp.json();
        if (resp.ok) {
            mostrarMensaje(msg, `✅ ${result.mensaje}`, "var(--success)");
            document.getElementById('wizard-suc-nombre').value = '';
            document.getElementById('wizard-suc-direccion').value = '';
            setTimeout(() => cargarHome(), 1000);
        } else {
            mostrarMensaje(msg, `Error: ${result.detail}`, "var(--danger)");
        }
    } catch (e) {
        mostrarMensaje(msg, "Error de conexión.", "var(--danger)");
    }
}

// --- Dashboard ---

async function cargarDashboard() {
    if (!checkAuth()) return;
    try {
        const response = await fetch('/api/dashboard', { headers: getAuth() });
        if (!response.ok) throw new Error("Error");
        const data = await response.json();

        document.getElementById('kpi-total').innerText = data.total_productos;
        document.getElementById('kpi-criticos').innerText = data.productos_criticos;
        document.getElementById('kpi-despachos').innerText = data.despachos_pendientes;

        const criticoCard = document.getElementById('kpi-card-criticos');
        criticoCard.classList.toggle('critico', data.productos_criticos > 0);

        const lista = document.getElementById('lista-alertas');
        lista.innerHTML = '';
        if (data.alertas_recientes && data.alertas_recientes.length > 0) {
            data.alertas_recientes.forEach(alerta => {
                const li = document.createElement('li');
                li.className = 'alerta-item';
                let f = alerta.fecha;
                try {
                    const d = new Date(alerta.fecha);
                    f = `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
                } catch(e) { f = (alerta.fecha || '').substring(0,16).replace('T',' '); }
                li.innerHTML = `<div><strong>[${f}]</strong> ${alerta.mensaje}</div>`;
                lista.appendChild(li);
            });
        } else {
            lista.innerHTML = '<li style="border-left-color:var(--success);background:var(--success-glow)"><div><span style="color:var(--success);font-weight:600;">Sin Alertas Críticas:</span> Todos los SKUs tienen stock saludable.</div></li>';
        }

        const rotLista = document.getElementById('lista-rotacion');
        rotLista.innerHTML = '';
        if (data.top_rotacion && data.top_rotacion.length > 0) {
            data.top_rotacion.forEach((p, i) => {
                const li = document.createElement('li');
                const med = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i+1}.`;
                li.innerHTML = `<div><strong>${med} ${p.sku}</strong> — ${p.nombre} <span class="badge">${p.movimientos} mov</span></div>`;
                rotLista.appendChild(li);
            });
        } else {
            rotLista.innerHTML = '<li><div>No hay datos de rotación aún.</div></li>';
        }
    } catch (error) {
        console.error("Error cargando dashboard:", error);
    }
}

// --- Stock ---

async function cargarStockVivo() {
    if (!checkAuth()) return;
    try {
        const sid = getFilterSucursalId();
        let url = '/api/productos';
        if (sid) url += `?sucursal_id=${sid}`;
        const response = await fetch(url, { headers: getAuth() });
        if (!response.ok) throw new Error("Error");
        const data = await response.json();
        const tbody = document.querySelector('#tabla-stock tbody');
        tbody.innerHTML = '';
        if (data.productos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);padding:2rem;">No hay productos registrados.</td></tr>';
            return;
        }
        data.productos.forEach(p => {
            const tr = document.createElement('tr');
            const critico = p.stock <= p.stock_minimo;
            if (critico) tr.className = 'fila-critica';
            tr.innerHTML = `
                <td><strong>${p.sku}</strong></td>
                <td>${p.nombre}</td>
                <td class="stock-valor ${critico ? 'stock-bajo' : 'stock-normal'}">${p.stock}</td>
                <td>${p.stock_minimo}</td>
                <td><span class="badge">${p.movimientos}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Error cargando stock:", error);
    }
}

// --- Historial ---

async function cargarHistorial() {
    if (!checkAuth()) return;
    try {
        const sid = getFilterSucursalId();
        let url = '/api/historial';
        if (sid) url += `?sucursal_id=${sid}`;
        const response = await fetch(url, { headers: getAuth() });
        if (!response.ok) throw new Error("Error");
        const data = await response.json();
        const tbody = document.querySelector('#tabla-historial tbody');
        tbody.innerHTML = '';
        if (data.transacciones.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-secondary);padding:2rem;">No hay transacciones registradas.</td></tr>';
            return;
        }
        data.transacciones.forEach(t => {
            const tr = document.createElement('tr');
            let f = t.fecha;
            try {
                const d = new Date(t.fecha);
                f = `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
            } catch(e) {}
            const tipoLabel = t.tipo === 'ingreso' ? 'Ingreso' : t.tipo === 'salida' ? 'Salida' : 'POS';
            const tipoClass = t.tipo === 'ingreso' ? 'tipo-ingreso' : 'tipo-salida';
            const prov = t.proveedor_nombre ? `${t.proveedor_nombre}<br><small style="color:var(--text-secondary);">${t.proveedor_rut || ''}</small>` : '-';
            const comp = t.comprador_nombre ? `${t.comprador_nombre}<br><small style="color:var(--text-secondary);">${t.comprador_rut || ''}</small>` : '-';
            tr.innerHTML = `
                <td>${f}</td>
                <td><strong>${t.sku}</strong></td>
                <td><span class="tipo-badge ${tipoClass}">${tipoLabel}</span></td>
                <td>${t.cantidad}</td>
                <td>${t.stock_resultante}</td>
                <td>${prov}</td>
                <td>${comp}</td>
                <td>${t.lote || t.destino || '-'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Error cargando historial:", error);
    }
}

// --- Transacciones ---

async function procesarTransaccion(tipo, subtipo) {
    if (!checkAuth()) return;
    const prefijo = tipo === 'ingreso' ? 'in' : 'out';
    const skuInput = document.getElementById(`${prefijo}-sku`);
    const cantInput = document.getElementById(`${prefijo}-cant`);
    const msgElement = document.getElementById(`msg-${tipo}`);

    const sku = skuInput.value.trim().toUpperCase();
    const cant = parseInt(cantInput.value);

    if (!sku) { mostrarMensaje(msgElement, "Error: El SKU es requerido.", "var(--danger)"); return; }
    if (isNaN(cant) || cant <= 0) { mostrarMensaje(msgElement, "Error: La cantidad debe ser un número entero mayor a cero.", "var(--danger)"); return; }

    try {
        msgElement.innerText = "Procesando...";
        msgElement.style.color = "var(--text-secondary)";
        const body = tipo === 'ingreso'
            ? JSON.stringify({
                sku, cantidad: cant,
                lote: document.getElementById('in-lote')?.value?.trim() || '',
                proveedor_rut: document.getElementById('in-prov-rut')?.value?.trim() || '',
                proveedor_nombre: document.getElementById('in-prov-nombre')?.value?.trim() || '',
                proveedor_direccion: document.getElementById('in-prov-direccion')?.value?.trim() || '',
                proveedor_telefono: document.getElementById('in-prov-telefono')?.value?.trim() || '',
                proveedor_email: document.getElementById('in-prov-email')?.value?.trim() || ''
            })
            : JSON.stringify({
                sku, cantidad: cant, tipo: subtipo || 'salida',
                comprador_rut: document.getElementById('out-comp-rut')?.value?.trim() || '',
                comprador_nombre: document.getElementById('out-comp-nombre')?.value?.trim() || '',
                comprador_direccion: document.getElementById('out-comp-direccion')?.value?.trim() || '',
                comprador_telefono: document.getElementById('out-comp-telefono')?.value?.trim() || '',
                comprador_email: document.getElementById('out-comp-email')?.value?.trim() || ''
            });

        const response = await fetch(`/api/${tipo}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuth() },
            body
        });
        const result = await response.json();
        if (response.ok) {
            mostrarMensaje(msgElement, result.mensaje, "var(--success)");
            skuInput.value = '';
            cantInput.value = '';
            if (document.getElementById('in-lote')) document.getElementById('in-lote').value = '';
            ['in-prov-rut','in-prov-nombre','in-prov-direccion','in-prov-telefono','in-prov-email',
             'out-comp-rut','out-comp-nombre','out-comp-direccion','out-comp-telefono','out-comp-email'
            ].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
        } else {
            mostrarMensaje(msgElement, `Error: ${result.detail || 'Error al procesar la solicitud.'}`, "var(--danger)");
        }
    } catch (error) {
        mostrarMensaje(msgElement, "Error de conexión con el servidor.", "var(--danger)");
    }
}

async function procesarVentaPOS() {
    if (!checkAuth()) return;
    const skuInput = document.getElementById('pos-sku');
    const cantInput = document.getElementById('pos-cant');
    const msgElement = document.getElementById('msg-pos');
    const sku = skuInput.value.trim().toUpperCase();
    const cant = parseInt(cantInput.value);

    if (!sku) { mostrarMensaje(msgElement, "Error: El SKU es requerido.", "var(--danger)"); return; }
    if (isNaN(cant) || cant <= 0) { mostrarMensaje(msgElement, "Error: La cantidad debe ser mayor a cero.", "var(--danger)"); return; }

    try {
        msgElement.innerText = "Procesando venta POS...";
        msgElement.style.color = "var(--text-secondary)";
        const response = await fetch('/api/salida', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuth() },
            body: JSON.stringify({
                sku, cantidad: cant, tipo: 'pos',
                comprador_rut: document.getElementById('pos-comp-rut')?.value?.trim() || '',
                comprador_nombre: document.getElementById('pos-comp-nombre')?.value?.trim() || '',
                comprador_direccion: document.getElementById('pos-comp-direccion')?.value?.trim() || '',
                comprador_telefono: document.getElementById('pos-comp-telefono')?.value?.trim() || '',
                comprador_email: document.getElementById('pos-comp-email')?.value?.trim() || ''
            })
        });
        const result = await response.json();
        if (response.ok) {
            mostrarMensaje(msgElement, result.mensaje, "var(--success)");
            skuInput.value = '';
            cantInput.value = '1';
            ['pos-comp-rut','pos-comp-nombre','pos-comp-direccion','pos-comp-telefono','pos-comp-email'
            ].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
        } else {
            mostrarMensaje(msgElement, `Error: ${result.detail || 'Error al procesar la venta.'}`, "var(--danger)");
        }
    } catch (error) {
        mostrarMensaje(msgElement, "Error de conexión con el servidor.", "var(--danger)");
    }
}

// --- Despachos ---

async function cargarDespachos() {
    if (!checkAuth()) return;
    try {
        const sid = getFilterSucursalId();
        let url = '/api/despachos';
        if (sid) url += `?sucursal_id=${sid}`;
        const resp = await fetch(url, { headers: getAuth() });
        if (!resp.ok) throw new Error("Error");
        const data = await resp.json();
        const tbody = document.querySelector('#tabla-despachos tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (!data.despachos || data.despachos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-secondary);padding:2rem;">No hay despachos registrados.</td></tr>';
            return;
        }
        data.despachos.forEach(d => {
            const tr = document.createElement('tr');
            let f = d.fecha_creacion;
            try { const dt = new Date(d.fecha_creacion); f = `${String(dt.getDate()).padStart(2,'0')}/${String(dt.getMonth()+1).padStart(2,'0')}/${dt.getFullYear()}`; } catch(e) {}
            const estadoClass = d.estado === 'pendiente' ? 'tipo-salida' : 'tipo-ingreso';
            const comp = d.comprador_nombre ? `${d.comprador_nombre}<br><small style="color:var(--text-secondary);">${d.comprador_rut || ''}</small>` : '-';
            tr.innerHTML = `
                <td><strong>${d.sku}</strong></td>
                <td>${d.destino}</td>
                <td>${d.cantidad}</td>
                <td>${comp}</td>
                <td><span class="tipo-badge ${estadoClass}">${d.estado}</span></td>
                <td>${f}</td>
                <td>${d.estado === 'pendiente' ? `<button class="btn-sm btn-sm-success" onclick="completarDespacho(${d.id})"><i data-lucide="check" style="width:14px;height:14px;"></i> Completar</button>` : '<span style="color:var(--success);">✓ Completado</span>'}</td>
            `;
            tbody.appendChild(tr);
        });
        lucide.createIcons();
    } catch (e) {
        console.error("Error cargando despachos:", e);
    }
}

async function completarDespacho(id) {
    try {
        const resp = await fetch(`/api/despachos/${id}/completar`, {
            method: 'PATCH', headers: { ...getAuth() }
        });
        if (resp.ok) {
            cargarDespachos();
            cargarDashboard();
        }
    } catch (e) { console.error(e); }
}

// --- Admin: Usuarios ---

async function cargarUsuarios() {
    try {
        const resp = await fetch('/api/usuarios', { headers: getAuth() });
        if (!resp.ok) throw new Error("Error");
        const data = await resp.json();
        const tbody = document.querySelector('#tabla-usuarios tbody');
        tbody.innerHTML = '';
        data.usuarios.forEach(u => {
            const tr = document.createElement('tr');
            const rolClass = u.rol === 'admin' ? 'badge-admin' : 'badge-trabajador';
            tr.innerHTML = `
                <td>${u.id}</td>
                <td><strong>${u.username}</strong></td>
                <td><span class="user-badge ${rolClass}">${u.rol}</span></td>
                <td>${u.sucursal_nombre || '—'}</td>
                <td>
                    <button class="btn-sm btn-sm-danger" onclick="eliminarUsuario(${u.id}, '${u.username}')">
                        <i data-lucide="trash-2" style="width:14px;height:14px;"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        lucide.createIcons();
    } catch (e) {
        console.error("Error cargando usuarios:", e);
    }
}

async function crearUsuario() {
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    const rol = document.getElementById('reg-rol').value;
    const sucursal_id = parseInt(document.getElementById('reg-sucursal').value) || null;
    const msg = document.getElementById('msg-register');

    if (!username || !password) {
        mostrarMensaje(msg, "Error: Usuario y contraseña requeridos.", "var(--danger)");
        return;
    }
    if (rol === 'trabajador' && !sucursal_id) {
        mostrarMensaje(msg, "Error: Debes asignar una sucursal al trabajador.", "var(--danger)");
        return;
    }

    try {
        const resp = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuth() },
            body: JSON.stringify({ username, password, rol, sucursal_id })
        });
        const result = await resp.json();
        if (resp.ok) {
            mostrarMensaje(msg, result.mensaje, "var(--success)");
            document.getElementById('reg-username').value = '';
            document.getElementById('reg-password').value = '';
            cargarUsuarios();
        } else {
            mostrarMensaje(msg, `Error: ${result.detail}`, "var(--danger)");
        }
    } catch (e) {
        mostrarMensaje(msg, "Error de conexión.", "var(--danger)");
    }
}

async function eliminarUsuario(id, username) {
    if (!confirm(`¿Eliminar al usuario "${username}"?`)) return;
    try {
        const resp = await fetch(`/api/usuarios/${id}`, {
            method: 'DELETE', headers: { ...getAuth() }
        });
        if (resp.ok) {
            cargarUsuarios();
        } else {
            const result = await resp.json();
            alert(result.detail || 'Error al eliminar usuario');
        }
    } catch (e) { console.error(e); }
}

// --- Admin: Sucursales ---

async function cargarSucursalesAdmin() {
    try {
        const resp = await fetch('/api/sucursales', { headers: getAuth() });
        if (!resp.ok) throw new Error("Error");
        const data = await resp.json();
        const tbody = document.querySelector('#tabla-sucursales tbody');
        tbody.innerHTML = '';
        data.sucursales.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${s.id}</td>
                <td><strong>${s.nombre}</strong></td>
                <td>${s.direccion || '—'}</td>
                <td>
                    <div class="inline-flex">
                        <input type="text" id="edit-suc-nombre-${s.id}" value="${s.nombre}" style="display:none;padding:4px 8px;background:rgba(15,23,42,0.6);border:1px solid var(--border-color);border-radius:4px;color:white;font-size:0.8rem;width:130px;">
                        <input type="text" id="edit-suc-dir-${s.id}" value="${s.direccion}" style="display:none;padding:4px 8px;background:rgba(15,23,42,0.6);border:1px solid var(--border-color);border-radius:4px;color:white;font-size:0.8rem;width:130px;">
                        <button class="btn-sm btn-sm-edit" id="btn-edit-suc-${s.id}" onclick="editarSucursal(${s.id})">
                            <i data-lucide="pencil" style="width:14px;height:14px;"></i>
                        </button>
                        <button class="btn-sm btn-sm-edit" id="btn-save-suc-${s.id}" style="display:none;" onclick="guardarSucursal(${s.id})">
                            <i data-lucide="check" style="width:14px;height:14px;"></i>
                        </button>
                        <button class="btn-sm btn-sm-danger" onclick="eliminarSucursal(${s.id})">
                            <i data-lucide="trash-2" style="width:14px;height:14px;"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        lucide.createIcons();
    } catch (e) {
        console.error("Error cargando sucursales:", e);
    }
}

function editarSucursal(id) {
    document.getElementById(`edit-suc-nombre-${id}`).style.display = 'inline-block';
    document.getElementById(`edit-suc-dir-${id}`).style.display = 'inline-block';
    document.getElementById(`btn-edit-suc-${id}`).style.display = 'none';
    document.getElementById(`btn-save-suc-${id}`).style.display = 'inline-block';
}

async function guardarSucursal(id) {
    const nombre = document.getElementById(`edit-suc-nombre-${id}`).value.trim();
    const direccion = document.getElementById(`edit-suc-dir-${id}`).value.trim();
    try {
        const resp = await fetch(`/api/sucursales/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', ...getAuth() },
            body: JSON.stringify({ nombre, direccion })
        });
        if (resp.ok) {
            cargarSucursalesAdmin();
            cargarSucursalesSelect('admin-sucursal-filter');
            cargarSucursalesSelect('reg-sucursal');
        } else {
            const r = await resp.json();
            alert(r.detail || 'Error');
        }
    } catch (e) { console.error(e); }
}

async function eliminarSucursal(id) {
    if (!confirm('¿Eliminar esta sucursal? Los usuarios asignados deben ser reasignados primero.')) return;
    try {
        const resp = await fetch(`/api/sucursales/${id}`, {
            method: 'DELETE', headers: { ...getAuth() }
        });
        const r = await resp.json();
        if (resp.ok) {
            cargarSucursalesAdmin();
            cargarSucursalesSelect('admin-sucursal-filter');
            cargarSucursalesSelect('reg-sucursal');
        } else {
            alert(r.detail || 'Error');
        }
    } catch (e) { console.error(e); }
}

async function crearSucursal() {
    const nombre = document.getElementById('suc-nombre').value.trim();
    const direccion = document.getElementById('suc-direccion').value.trim();
    const msg = document.getElementById('msg-sucursal');

    if (!nombre) { mostrarMensaje(msg, "Error: El nombre es requerido.", "var(--danger)"); return; }

    try {
        const resp = await fetch('/api/sucursales', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuth() },
            body: JSON.stringify({ nombre, direccion })
        });
        const result = await resp.json();
        if (resp.ok) {
            mostrarMensaje(msg, result.mensaje, "var(--success)");
            document.getElementById('suc-nombre').value = '';
            document.getElementById('suc-direccion').value = '';
            cargarSucursalesAdmin();
            cargarSucursalesSelect('admin-sucursal-filter');
            cargarSucursalesSelect('reg-sucursal');
        } else {
            mostrarMensaje(msg, `Error: ${result.detail}`, "var(--danger)");
        }
    } catch (e) { mostrarMensaje(msg, "Error de conexión.", "var(--danger)"); }
}

// --- Sucursal filter (admin) ---

async function cargarSucursalesSelect(selectId) {
    try {
        const resp = await fetch('/api/sucursales', { headers: getAuth() });
        if (!resp.ok) return;
        const data = await resp.json();
        const select = document.getElementById(selectId);
        if (!select) return;
        const currentVal = select.value;
        const isFilter = selectId === 'admin-sucursal-filter';
        select.innerHTML = isFilter ? '<option value="">Todas las sucursales</option>' : '<option value="">Seleccionar sucursal...</option>';
        data.sucursales.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.nombre;
            select.appendChild(opt);
        });
        if (currentVal) select.value = currentVal;
    } catch (e) { console.error(e); }
}

function getFilterSucursalId() {
    const select = document.getElementById('admin-sucursal-filter');
    if (!select) return null;
    const val = select.value;
    return val ? parseInt(val) : null;
}

function onSucursalFilterChange() {
    const activePanel = document.querySelector('.panel.activo');
    if (activePanel) {
        const id = activePanel.id;
        if (id === 'stock') cargarStockVivo();
        else if (id === 'historial') cargarHistorial();
        else if (id === 'despachos') cargarDespachos();
        else if (id === 'dashboard') cargarDashboard();
    }
}

// --- Mensajes ---

function mostrarMensaje(element, texto, color) {
    element.innerText = texto;
    element.style.color = color;
    element.style.opacity = 1;
    setTimeout(() => {
        if (element.innerText === texto) {
            element.style.opacity = 0;
            setTimeout(() => { element.innerText = ''; }, 300);
        }
    }, 5000);
}

// --- Init ---

window.onload = async () => {
    if (!checkAuth()) return;
    await cargarUserInfo();
    // Show home by default (first nav item active, home panel active)
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('activo'));
    document.getElementById('home').classList.add('activo');
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    const homeBtn = document.getElementById('btn-nav-home');
    if (homeBtn) homeBtn.classList.add('active');
    document.getElementById('page-title').innerText = 'Inicio';
    document.getElementById('page-subtitle').innerText = 'Panel de bienvenida y acceso rápido';
    await cargarHome();
};
