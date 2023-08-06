from myst.client import Client
from myst.openapi.models.input_get import InputGet


def request_sync(client: Client, operation_uuid: str, uuid: str) -> InputGet:
    """Gets a specific input for an operation."""

    return client.request(method="get", path=f"/operations/{operation_uuid}/inputs/{uuid}", response_class=InputGet)
