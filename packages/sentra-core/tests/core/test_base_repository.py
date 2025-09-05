import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import IntegrityError

from sentra.domain.repository.base_repository import BaseRepository

Base = declarative_base()

class DummyModel(Base):
    __tablename__ = "dummy_model"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.now(timezone.utc)


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def base_repository(db_session):
    return BaseRepository(DummyModel, db_session)


def test_get(base_repository, db_session):
    dummy = DummyModel(id=uuid4(), name="Test")
    db_session.scalars.return_value.first.return_value = dummy

    result = base_repository.get(dummy.id)
    assert result == dummy
    db_session.scalars.assert_called_once()


def test_get_all(base_repository, db_session):
    dummy1 = DummyModel(id=uuid4(), name="Test1")
    dummy2 = DummyModel(id=uuid4(), name="Test2")
    db_session.scalars.return_value.all.return_value = [dummy1, dummy2]

    result = base_repository.get_all()
    assert result == [dummy1, dummy2]
    db_session.scalars.assert_called_once()


def test_create(base_repository, db_session):
    dummy = DummyModel(id=uuid4(), name="Test")

    result = base_repository.create(dummy)
    db_session.add.assert_called_once_with(dummy)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(dummy)
    assert result == dummy


def test_create_integrity_error(base_repository, db_session):
    dummy = DummyModel(name="Test")
    db_session.add.side_effect = IntegrityError("stmt", "params", Exception("UNIQUE constraint failed: table.column"))

    with pytest.raises(ValueError) as exc:
        base_repository.create(dummy)

    db_session.rollback.assert_called_once()
    assert "Duplicate entry for column in table." in str(exc.value)


def test_update(base_repository, db_session):
    dummy = DummyModel(id=uuid4(), name="Updated Test")
    db_session.merge.return_value = dummy

    result = base_repository.update(dummy)
    db_session.merge.assert_called_once_with(dummy)
    db_session.commit.assert_called_once()
    assert result == dummy


def test_update_integrity_error(base_repository, db_session):
    dummy = DummyModel(id=uuid4(), name="Updated Test")
    db_session.merge.side_effect = IntegrityError("stmt", "params", Exception("UNIQUE constraint failed: table.column"))

    with pytest.raises(ValueError) as exc:
        base_repository.update(dummy)

    db_session.rollback.assert_called_once()
    assert "Duplicate entry for column in table." in str(exc.value)


def test_delete_hard(base_repository, db_session):
    dummy = DummyModel(id=uuid4(), name="ToDelete")
    db_session.scalars.return_value.first.return_value = dummy

    base_repository.delete(dummy.id, soft=False)
    db_session.delete.assert_called_once_with(dummy)
    db_session.commit.assert_called_once()


def test_delete_soft(base_repository, db_session):
    dummy = DummyModel(id=uuid4(), name="ToDelete", deleted_at=None)
    db_session.scalars.return_value.first.return_value = dummy

    base_repository.delete(dummy.id, soft=True)
    assert dummy.deleted_at is not None
    db_session.delete.assert_not_called()
    db_session.commit.assert_called_once()


def test_delete_not_found(base_repository, db_session):
    db_session.scalars.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Object not found"):
        base_repository.delete(uuid4())


def test_parse_integrity_error(base_repository):
    err = IntegrityError("stmt", "params", Exception("UNIQUE constraint failed: table.column"))
    parsed = base_repository._parse_integrity_error(err)
    assert parsed == "Duplicate entry for column in table. Please choose a different value."
