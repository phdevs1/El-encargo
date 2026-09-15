# Importing each module's ORM models here is what registers their tables on
# Base.metadata. Nothing else in the app imports them in a guaranteed order,
# so this module must be imported before Alembic (or anything else) reads
# Base.metadata, or autogenerate will silently miss tables.
from app.organizations.infrastructure.orm import models as _organizations_models  # noqa: F401
from app.waitlist.infrastructure.orm import models as _waitlist_models  # noqa: F401
from app.notifications.infrastructure.orm import models as _notifications_models  # noqa: F401
from app.reporting.infrastructure.orm import models as _reporting_models  # noqa: F401
