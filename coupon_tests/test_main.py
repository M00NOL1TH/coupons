import json
import pytest
from typing import Callable, Generator
from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from coupon_app.main import create_app, get_db_session
from coupon_app.settings import get_settings
from coupon_model import init_models  # noqa
from coupon_model.customer.model import CustomerTable

app = create_app()
client = TestClient(app)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    app.dependency_overrides[get_db_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(name="prefix_url")
def prefix_url_fixture() -> Callable[[str], str]:
    settings = get_settings()
    api_prefx = settings.api_prefix

    def prefix_url(subpath: str) -> str:
        return f"{api_prefx.rstrip('/')}/{subpath.lstrip('/')}"

    return prefix_url


def test_create_customer(client: TestClient, prefix_url: Callable[[str], str]):
    response = client.post(
        prefix_url("/customers"),
        json={"username": "testname", "name": "TestName"},
    )
    result = response.json()

    assert response.status_code == 201
    assert result["username"] == "testname"
    assert result["name"] == "TestName"


def test_create_customer_incomplete(client: TestClient, prefix_url: Callable[[str], str]):
    response = client.post(
        prefix_url("/customers"),
        json={"name": "TestName"},
    )
    assert response.status_code == 422


def test_create_customer_invalid(client: TestClient, prefix_url: Callable[[str], str]):
    response = client.post(
        prefix_url("/customers"),
        json={"username": "t1", "name": "TestName"},
    )
    assert response.status_code == 422


def test_read_customers(session: Session, client: TestClient, prefix_url: Callable[[str], str]):
    customer_1 = CustomerTable(username="testname1", name="Test Name 1")
    customer_2 = CustomerTable(username="testname2", name="Test Name 2")
    session.add(customer_1)
    session.add(customer_2)
    session.commit()

    response = client.get(prefix_url("/customers"))
    result = response.json()

    assert response.status_code == 200
    assert len(result) == 2
    assert result[0]["name"] == customer_1.name
    assert result[0]["username"] == customer_1.username
    assert result[1]["name"] == customer_2.name
    assert result[1]["username"] == customer_2.username


def test_read_customer(session: Session, client: TestClient, prefix_url: Callable[[str], str]):
    customer = CustomerTable(username="testname1", name="Test Name 1")
    session.add(customer)
    session.commit()

    response = client.get(prefix_url(f"/customers/{customer.id}"))
    result = response.json()

    assert response.status_code == 200
    assert result["name"] == customer.name
    assert result["username"] == customer.username
    assert result["id"] == customer.id
    created_at = datetime.fromisoformat(result["created_at"])
    assert isinstance(created_at, datetime)
    assert created_at == customer.created_at


def test_crud_customer(client: TestClient, prefix_url: Callable[[str], str]):
    # -- Create

    response = client.post(
        prefix_url("/customers"),
        json={"username": "testname", "name": "Test Name"},
    )
    result = response.json()

    assert response.status_code == 201
    assert result["username"] == "testname"
    assert result["name"] == "Test Name"

    # -- Read

    result_id = result["id"]
    url = prefix_url(f"/customers/{result_id}")
    response = client.get(url)
    result = response.json()

    assert response.status_code == 200
    assert result["username"] == "testname"
    assert result["name"] == "Test Name"

    # -- Update

    changes = {"name": "New Name"}
    response = client.patch(url, json=changes)
    result = response.json()

    assert response.status_code == 200
    assert result["name"] == "New Name"

    # -- Delete

    response = client.delete(url)
    assert response.status_code == 204

    response = client.get(url)
    assert response.status_code == 404
