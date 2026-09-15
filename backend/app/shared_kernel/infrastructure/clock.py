from datetime import datetime

from app.shared_kernel.ports.clock import ClockPort


class SystemClock(ClockPort):
    def now(self) -> datetime:
        return datetime.utcnow()
