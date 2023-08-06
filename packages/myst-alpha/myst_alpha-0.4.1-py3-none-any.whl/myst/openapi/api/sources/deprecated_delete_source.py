from myst.client import Client
from myst.openapi.models.source_get import SourceGet


def request_sync(client: Client, uuid: str) -> SourceGet:
    """Deletes a new source."""

    return client.request(method="delete", path=f"/sources/{uuid}", response_class=SourceGet)
