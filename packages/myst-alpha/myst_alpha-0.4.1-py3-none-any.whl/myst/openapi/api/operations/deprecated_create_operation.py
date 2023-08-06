from myst.client import Client
from myst.openapi.models.deprecated_operation_create import DeprecatedOperationCreate
from myst.openapi.models.operation_get import OperationGet


def request_sync(client: Client, json_body: DeprecatedOperationCreate) -> OperationGet:
    """Creates an operation."""

    return client.request(method="post", path=f"/operations/", response_class=OperationGet, request_model=json_body)
