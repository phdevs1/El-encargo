from functools import wraps

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.organizations.domain.errors import LocationNotFound


def handle_domain_errors(fn):
    @wraps(fn)
    def wrapper(*args, db: Session, **kwargs):
        try:
            result = fn(*args, db=db, **kwargs)
            db.commit()
            return result
        except LocationNotFound as exc:
            db.rollback()
            raise HTTPException(status_code=404, detail=str(exc))

    return wrapper
