from datetime import datetime
from decimal import Decimal

from app.waitlist.domain.errors import SortOrderPrecisionExhausted

# Arbitrary spacing unit for entries placed at either end of the queue.
# sort_order is seeded from epoch-milliseconds, so this is tiny by comparison.
STEP = Decimal("1000")

# Matches the smallest representable gap for Numeric(20,10) columns.
PRECISION_FLOOR = Decimal("0.0000000001")


def seed_sort_order(joined_at: datetime) -> Decimal:
    return Decimal(int(joined_at.timestamp() * 1000))


def compute_reordered_sort_order(
    lower: Decimal | None, upper: Decimal | None, *, entry_id: int
) -> Decimal:
    if lower is None and upper is None:
        return Decimal(int(datetime.utcnow().timestamp() * 1000))

    if lower is None:
        candidate = upper - STEP
        return candidate if candidate > 0 else upper / 2

    if upper is None:
        return lower + STEP

    midpoint = (lower + upper) / 2
    if midpoint <= lower or midpoint >= upper or (upper - lower) < PRECISION_FLOOR:
        raise SortOrderPrecisionExhausted(entry_id)
    return midpoint
