from myst.client import Client
from myst.openapi.models.deprecated_model_create import DeprecatedModelCreate
from myst.openapi.models.model_get import ModelGet


def request_sync(client: Client, json_body: DeprecatedModelCreate) -> ModelGet:
    """Creates a model."""

    return client.request(method="post", path=f"/models/", response_class=ModelGet, request_model=json_body)
