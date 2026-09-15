# Restaurant Waitlist

Lista de espera digital para restaurantes con mucho *walk-in*: el comensal se une a la cola escaneando un QR, ve su posición en vivo, y el anfitrión gestiona la cola desde una tablet. Piloto en 3 locales (Lima x2, Santiago x1).

## Quickstart

Requisito único: Docker + Docker Compose (`docker compose version`). No hace falta Python ni Node instalados — todo corre en contenedores.

```bash
cd restaurant
cp .env.example .env        # credenciales de MySQL (los defaults ya funcionan)
docker compose up --build
```

La primera vez tarda un par de minutos (build de imágenes + `npm install`). Al terminar, el backend siembra automáticamente 3 locales de prueba — ver más abajo — y ya se puede abrir:

| | URL |
|---|---|
| App del comensal | http://localhost:5173/l/la-terraza-azul |
| App del anfitrión | http://localhost:5173/host/1 |
| API (Swagger) | http://localhost:8000/docs |

## Servicios

| Servicio | Puerto | Qué hace al arrancar |
|---|---|---|
| `mysql` | `3306` | espera a pasar el healthcheck antes de que arranque `backend` |
| `backend` | `8000` | migra la DB (Alembic), siembra datos de prueba si hacen falta, levanta `uvicorn` — ver [`backend/README.md`](backend/README.md) |
| `frontend` | `5173` | `npm install && npm run dev` (servidor de desarrollo de Vite) |

## Datos de prueba

El backend siembra automáticamente los 3 locales del piloto (La Terraza Azul, Cuatro Vientos, Casa Mediterránea) la primera vez que arranca, y no duplica en arranques siguientes. Detalle del mecanismo (script, idempotencia, cómo re-sembrar a mano) en [`backend/README.md`](backend/README.md#datos-de-prueba-seed).

Si la base ya tenía datos previos, el `location_id` de "La Terraza Azul" puede no ser `1` — confirmarlo con:

```bash
curl localhost:8000/locations/la-terraza-azul
```

## Comandos útiles

```bash
# reconstruir después de cambiar requirements.txt o package.json
docker compose build backend
docker compose build frontend

# logs de un servicio puntual
docker compose logs backend --tail=50
docker compose logs frontend --tail=50

# detener
docker compose down          # elimina contenedores, los datos de MySQL persisten en el volumen
docker compose down -v       # además borra el volumen — arranca desde cero la próxima vez
docker compose stop          # solo pausa, para reanudar con `docker compose start`
```

## Variables de entorno

Todas tienen default en `docker-compose.yml` — normalmente no hace falta tocar nada. Las específicas del backend (MySQL, CORS, seed) están documentadas en [`backend/README.md`](backend/README.md).

| Variable | Dónde se usa | Default | Notas |
|---|---|---|---|
| `VITE_API_BASE_URL` | `frontend` | `http://localhost:8000` | debe ser una URL alcanzable **desde el navegador** (el puerto publicado en el host), no el nombre interno `backend:8000` de la red de Docker — el `fetch` corre en el navegador, no dentro del contenedor |

## Estructura

```
restaurant/
├── backend/            FastAPI + SQLAlchemy 2 + Alembic + MySQL — ver backend/README.md
├── frontend/            React + TypeScript + Zustand
├── images/               prototipo (image.png)
└── docker-compose.yml    orquesta los 3 servicios para desarrollo local
```

## Más documentación

- [`backend/README.md`](backend/README.md): arquitectura (monolito modular + hexagonal), modelo ER, endpoints, variables de entorno del backend, Alembic, seed.
