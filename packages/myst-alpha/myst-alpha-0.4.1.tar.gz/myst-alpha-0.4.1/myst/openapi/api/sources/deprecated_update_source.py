from myst.client import Client
from myst.openapi.models.source_get import SourceGet
from myst.openapi.models.source_update import SourceUpdate


def request_sync(client: Client, uuid: str, json_body: SourceUpdate) -> SourceGet:
    """Updates a source."""

    return client.request(method="patch", path=f"/sources/{uuid}", response_class=SourceGet, request_model=json_body)
