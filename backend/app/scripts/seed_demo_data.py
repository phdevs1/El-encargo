"""Idempotent demo data for local development.

Run manually with:
    docker compose run --rm backend python -m app.scripts.seed_demo_data

Runs automatically on container start when SEED_DEMO_DATA=true (see Dockerfile) —
intended for local docker-compose only, never set in a real deployment.
"""

from sqlalchemy import select

from app.organizations.infrastructure.orm.models import Location, Organization
from app.shared_kernel.db.session import SessionLocal

# The pilot's 3 real locations. Each is its own Organization (confirmed:
# they're 3 independent clients, not one chain) — see project memory.
DEMO_LOCATIONS = [
    {
        "name": "La Terraza Azul",
        "slug": "la-terraza-azul",
        "country": "PE",
        "timezone": "America/Lima",
    },
    {
        "name": "Cuatro Vientos",
        "slug": "cuatro-vientos",
        "country": "PE",
        "timezone": "America/Lima",
    },
    {
        "name": "Casa Mediterránea",
        "slug": "casa-mediterranea",
        "country": "CL",
        "timezone": "America/Santiago",
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        for entry in DEMO_LOCATIONS:
            existing = db.execute(
                select(Location).where(Location.slug == entry["slug"])
            ).scalar_one_or_none()
            if existing is not None:
                print(f"seed_demo_data: '{entry['slug']}' already exists (location_id={existing.id}), skipping")
                continue

            org = Organization(
                name=entry["name"],
                slug=entry["slug"],
                country_default=entry["country"],
                is_active=True,
            )
            db.add(org)
            db.flush()

            loc = Location(
                organization_id=org.id,
                name=entry["name"],
                slug=entry["slug"],
                country=entry["country"],
                timezone=entry["timezone"],
                is_active=True,
            )
            db.add(loc)
            db.flush()
            print(f"seed_demo_data: created '{entry['slug']}' (organization_id={org.id}, location_id={loc.id})")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
