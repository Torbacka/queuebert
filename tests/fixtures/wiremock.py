import os
import time

import pytest
import requests
from testcontainers.core.container import DockerContainer


@pytest.fixture(scope="session")
def slack_wiremock():
    mappings_file_path = os.path.join(os.path.dirname(__file__), "wiremock_mapping")
    wiremock_port = 8082
    health_check_url = f"http://localhost:{wiremock_port}/__admin"
    with DockerContainer("wiremock/wiremock:3.9.2") as container:
        container.with_exposed_ports(8080)
        container.with_bind_ports(8080, wiremock_port)
        container.with_volume_mapping(mappings_file_path, "/home/wiremock/mappings")
        container.start()
        # Wait for the container to be ready
        max_retries = 10
        retry_interval = 1  # seconds
        for _ in range(max_retries):
            try:
                response = requests.get(health_check_url)
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(retry_interval)
        else:
            raise RuntimeError("WireMock container did not become ready in time.")

        yield container, wiremock_port
