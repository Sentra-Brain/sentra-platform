# packages/sentra-infra/src/sentra/infra/sql/repositories/base_repository.py
from typing import List, TypeVar, Generic, Type, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sentra.domain.entities.base_entity import BaseEntity

T = TypeVar('T', bound=BaseEntity)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get(self, id: UUID) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id, self.model.deleted_at.is_(None))
        return self.db.scalars(stmt).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        stmt = select(self.model).where(self.model.deleted_at.is_(None)).limit(limit).offset(offset)
        return self.db.scalars(stmt).all()

    def filter_by(self, limit: int = 100, offset: int = 0, **kwargs) -> List[T]:
        stmt = select(self.model).filter_by(**kwargs).where(self.model.deleted_at.is_(None)).limit(limit).offset(offset)
        return self.db.scalars(stmt).all()

    def create(self, obj: T) -> T:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(self._parse_integrity_error(e))

    def update(self, obj: T) -> T:
        try:
            self.db.merge(obj)
            self.db.commit()
            return obj
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(self._parse_integrity_error(e))

    def delete(self, id: UUID, soft: bool = True) -> None:
        obj = self.get(id)
        if not obj:
            raise ValueError("Object not found")

        if soft and hasattr(obj, "soft_delete"):
            obj.soft_delete()
        else:
            self.db.delete(obj)

        self.db.commit()

    def _parse_integrity_error(self, error: IntegrityError) -> str:
        orig_msg = str(error.orig)
        err_msg = orig_msg.split(':')[-1].replace('\n', '').strip()

        parts = err_msg.split('.')
        if len(parts) >= 2:
            table, column = parts[-2], parts[-1]
            return f"Duplicate entry for {column} in {table}. Please choose a different value."
        else:
            return "An error occurred while processing your request."

