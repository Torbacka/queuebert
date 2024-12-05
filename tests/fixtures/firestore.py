import pytest
from testcontainers.core.container import DockerContainer


@pytest.fixture(scope="session")
def shared_firestore():
    with DockerContainer("mtlynch/firestore-emulator:20210410") as container:
        container.with_exposed_ports(8080)
        container.with_bind_ports(8080, 8080)
        container.with_env("FIRESTORE_PROJECT_ID", "queuebert")
        container.start()
        yield container