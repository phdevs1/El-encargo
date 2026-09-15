from functools import wraps

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.shared_kernel.domain.phone import InvalidPhoneNumber
from app.waitlist.domain.errors import (
    InvalidReorderTarget,
    InvalidStateTransition,
    LocationNotFound,
    SortOrderPrecisionExhausted,
    WaitlistEntryNotFound,
)


def handle_domain_errors(fn):
    @wraps(fn)
    def wrapper(*args, db: Session, **kwargs):
        try:
            result = fn(*args, db=db, **kwargs)
            db.commit()
            return result
        except StaleDataError:
            db.rollback()
            raise HTTPException(
                status_code=409, detail="This entry was updated by someone else. Refresh and try again."
            )
        except InvalidStateTransition as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc))
        except SortOrderPrecisionExhausted:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Could not reorder: too many entries stacked here, try a different spot.",
            )
        except (WaitlistEntryNotFound, LocationNotFound, InvalidReorderTarget) as exc:
            db.rollback()
            raise HTTPException(status_code=404, detail=str(exc))
        except InvalidPhoneNumber as exc:
            db.rollback()
            raise HTTPException(status_code=422, detail=f"Invalid phone number: {exc.raw}")

    return wrapper
