from sentra_brain_api.core.base_mongo_model import BaseMongoModel


def test_string_id():
    doc = {"_id": "abc123", "name": "Chat"}

    class DummyModel(BaseMongoModel):
        name: str

    model = DummyModel.from_mongo(doc)

    assert model.id == "abc123"
    assert model.model_dump() == {"id": "abc123", "name": "Chat"}


def test_int_id():
    doc = {"_id": 42, "name": "Chat"}

    class DummyModel(BaseMongoModel):
        name: str

    model = DummyModel.from_mongo(doc)

    assert model.id == "42"
    assert model.model_dump() == {"id": "42", "name": "Chat"}


def test_uuid_id():
    import uuid
    my_uuid = uuid.uuid4()
    doc = {"_id": str(my_uuid), "name": "Chat"}

    class DummyModel(BaseMongoModel):
        id: str
        name: str

    model = DummyModel.from_mongo(doc)

    assert model.id == str(my_uuid)



def test_missing_id():
    doc = {"name": "Chat"}

    class DummyModel(BaseMongoModel):
        name: str

    model = DummyModel.from_mongo(doc)

    assert model.id is None
    assert model.model_dump() == {"id": None, "name": "Chat"}

