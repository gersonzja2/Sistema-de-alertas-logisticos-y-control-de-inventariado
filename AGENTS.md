# ADS40 — AGENTS.md

## Quick start

```powershell
.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
# Open http://localhost:8000/login  (admin / admin123)
```

## Tests

```powershell
python -m pytest static/tests/test.py -v
# single test:
python -m pytest static/tests/test.py::test_ingreso_producto_nuevo -v
```

All 42 tests are in one file `static/tests/test.py`. No conftest. Uses `TestClient` with `sqlite:///./test_logistica.db` and a `setup_db` fixture that recreates schema per function.

## DB quirks

- Schema auto-creates on startup (`Base.metadata.create_all` in `main.py:22`)
- If you add columns to models, **delete both `logistica.db` and `test_logistica.db`** before running, or old schema columns won't exist
- `test_logistica.db` is NOT in `.gitignore` — it's test collateral, commit only intentionally
- SQLite with `PRAGMA foreign_keys=ON` (set via engine event listener)

## Architecture

```
main.py          — FastAPI app (~700 lines): endpoints, auth, Pydantic schemas, seed, middleware
models.py        — 7 SQLAlchemy models: Sucursal, User, Producto, Lote, Transaccion, DespachoPendiente, RegistroAlerta
database.py      — engine + SessionLocal + Base
templates/       — Jinja2 HTML (login.html, index.html)
static/js/       — script.js (~790 lines, vanilla JS)
static/css/      — style.css
static/tests/    — test.py (42 tests)
```

## Auth pattern

- JWT (HS256, 24h) in `Authorization: Bearer <token>`
- Sim token `simulacion-jwt-token-123` maps to admin for TestClient only
- `require_admin()` returns 403 if not admin
- Token payload includes `sub` (string), `username`, `rol`, `sucursal_id`

## Multi-sucursal filter pattern

Every list endpoint uses `or_(col.sucursal_id == sid, col.sucursal_id.is_(None))` so global records (sucursal_id=NULL) are always included when filtering by sucursal. This applies to productos, historial, dashboard, despachos, alertas.

Exception: `POST /api/ingreso` and `POST /api/salida` filter strictly by `sucursal_id == sid` (no `or_`), because stock must be separate per sucursal.

## Key gotchas

- **Password hashing**: SHA-256 + salt (`hashlib`), NOT bcrypt. `PWD_SALT` env var.
- **Env vars**: `.env` is gitignored. Required: `RESEND_API_KEY`. Optional: `JWT_SECRET`, `PWD_SALT`, `WEBHOOK_URL`, `PROVEEDOR_EMAIL`, `GERENTE_EMAIL`.
- **Port 8000**: if ghost LISTENING, use `taskkill /F /PID <pid>` or change port.
- **`.venv`** not `venv` — activate with `.venv\Scripts\Activate.ps1`
- **Frontend is vanilla JS**: no framework, no bundler. `lucide.createIcons()` called after dynamic DOM changes.
- **No migrations**: schema changes require deleting .db files and restarting.
- **Foreign key constraints**: `PRAGMA foreign_keys=ON` means delete order in tests matters (sucursal before user, etc.).
- **Colspans in tables**: when adding/removing columns, update colspan in both `templates/index.html` (empty row) and `static/js/script.js`.

## Endpoints to know

| Method | Path | Auth |
|--------|------|------|
| GET | `/login`, `/` | Public (pages) |
| POST | `/api/auth/login` | Public |
| POST | `/api/auth/register` | Admin only |
| GET/POST | `/api/usuarios`, DELETE `/api/usuarios/{id}` | Admin only |
| GET/POST/PUT/DELETE | `/api/sucursales` | Admin for mutations |
| GET | `/api/productos`, `/api/productos/{sku}` | Auth |
| POST | `/api/ingreso` | Auth |
| POST | `/api/salida` | Auth |
| GET | `/api/historial`, `/api/dashboard`, `/api/despachos` | Auth |
| POST | `/api/transferencias` | Admin only |
| GET | `/api/alertas/activas` | Auth |
| GET | `/health` | Public |

## Styling conventions

- CSS variables in `:root` (slate-blue dark theme, see `style.css:2-27`)
- `.content-card` pattern for all sections: card-header + card-body
- Tables use class `tabla-datos`, `<td class="stock-bajo">` for critical rows
- Inline `<style>` in `index.html` for section-specific overrides
- Badges: `.user-badge` + `.badge-admin` / `.badge-trabajador`
