from sqlalchemy.orm import Session
from app.models.globle_status import GlobleStatus

def create_default_status(db: Session):
    statuses = [
        {'name': 'Active', 'category': 'General'},
        {'name': 'Inactive', 'category': 'General'}
    ]

    for status in statuses:
        if not db.query(GlobleStatus).filter(GlobleStatus.name == status['name'], GlobleStatus.category == status['category']).first():
            db.add(GlobleStatus(**status, created_by=1))
    db.commit()
