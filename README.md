# Restaurant Waitlist

Lista de espera digital para restaurantes con mucho *walk-in*: el comensal se une a la cola escaneando un QR, ve su posición en vivo, y el anfitrión gestiona la cola desde una tablet. Piloto en 3 locales (Lima x2, Santiago x1).

## Quickstart

Requisito: Docker + Docker Compose. Nada más — no hace falta Python ni Node instalados, todo corre en contenedores.

```bash
cd restaurant
cp .env.example .env    # credenciales de MySQL — los defaults ya sirven para desarrollo
docker compose up --build
```

Eso es todo. Al terminar (la primera vez tarda un par de minutos: build de imágenes + `npm install`):

| | |
|---|---|
| 🍽️ Comensal | http://localhost:5173/l/la-terraza-azul |
| 🧑‍💼 Anfitrión | http://localhost:5173/host/1 |
| 🔌 API / Swagger | http://localhost:8000/docs |

Los 3 locales del piloto ya están sembrados automáticamente — no hace falta ningún paso extra antes de probar (ver [Datos de prueba](#datos-de-prueba)).

## Qué levanta `docker compose up`

| Servicio | Puerto | Qué hace al arrancar |
|---|---|---|
| `mysql` | `3306` | espera a pasar el healthcheck antes de que arranque `backend` |
| `backend` | `8000` | corre `alembic upgrade head` → siembra datos de prueba si hacen falta → levanta `uvicorn` |
| `frontend` | `5173` | `npm install && npm run dev` (servidor de desarrollo de Vite) |

## Datos de prueba

Los 3 locales reales del piloto ya están sembrados automáticamente al arrancar (idempotente, no duplica en arranques siguientes) — el mecanismo completo del seed está documentado en [`backend/README.md`](backend/README.md#datos-de-prueba-seed). Cada local tiene su cola completamente aislada — un comensal que se une a uno no aparece en la cola de otro:

| Local | 🍽️ Comensal | 🧑‍💼 Anfitrión |
|---|---|---|
| La Terraza Azul (Lima) | http://localhost:5173/l/la-terraza-azul | http://localhost:5173/host/1 |
| Cuatro Vientos (Lima) | http://localhost:5173/l/cuatro-vientos | http://localhost:5173/host/2 |
| Casa Mediterránea (Santiago) | http://localhost:5173/l/casa-mediterranea | http://localhost:5173/host/3 |

Para probar de punta a punta: abrí la URL de comensal de un local en una pestaña, unite a la cola, y en otra pestaña abrí la URL de anfitrión de ese mismo local — la entrada aparece **al instante**, sin recargar (la tablet del anfitrión se actualiza en tiempo real por WebSocket, no por polling — ver [`backend/README.md`](backend/README.md#tiempo-real-websocket)). El puntito junto a "Cola · local N" indica si está conectada (verde) o reconectando (ámbar). Probalo con los 3 en paralelo para confirmar que las colas no se mezclan entre locales.

## Comandos útiles del día a día

**Reconstruir** después de cambiar dependencias (`requirements.txt` / `package.json`):
```bash
docker compose up --build          # reconstruye solo lo que cambió
docker compose build backend       # solo el backend
docker compose build frontend      # solo el frontend
```

**Ver logs** (útil si algo no levantó bien):
```bash
docker compose logs backend --tail=50
docker compose logs frontend --tail=50
```

**Parar y limpiar:**
```bash
docker compose stop          # pausa los contenedores sin eliminarlos — reanudar con `docker compose start`
docker compose down          # detiene y elimina los contenedores; los datos de MySQL persisten en el volumen
docker compose down -v       # además borra el volumen de MySQL — la próxima vez arranca desde cero
```

## Variables de entorno

Todas están declaradas con sus defaults directamente en `docker-compose.yml`; el `.env` en la raíz solo hace falta si querés cambiar las credenciales de MySQL.

| Variable | Servicio | Default | Notas |
|---|---|---|---|
| `MYSQL_ROOT_PASSWORD` / `MYSQL_DATABASE` / `MYSQL_USER` / `MYSQL_PASSWORD` | `mysql`, `backend` | `change-me` / `waitlist` / `waitlist_app` / `change-me` | mismas credenciales inyectadas a ambos servicios |
| `VITE_API_BASE_URL` | `frontend` | `http://localhost:8000` | debe ser una URL alcanzable **desde el navegador** (el puerto publicado en el host), no el nombre interno `backend:8000` de la red de Docker — el `fetch` corre en el navegador, no dentro del contenedor |

El resto de las variables (`CORS_ALLOWED_ORIGINS`, `SEED_DEMO_DATA`, etc.) son específicas del backend y están documentadas en [`backend/README.md`](backend/README.md#cómo-correr-localmente).

## Estructura del repo

```
restaurant/
├── backend/            FastAPI + SQLAlchemy 2 + Alembic + MySQL — ver backend/README.md
├── frontend/            React + TypeScript + Zustand
├── images/               prototipo (image.png)
└── docker-compose.yml    orquesta los 3 servicios para desarrollo local
```

## Más documentación

- [`backend/README.md`](backend/README.md): arquitectura del backend (monolito modular + hexagonal), modelo ER completo, endpoints, comandos de Alembic.
