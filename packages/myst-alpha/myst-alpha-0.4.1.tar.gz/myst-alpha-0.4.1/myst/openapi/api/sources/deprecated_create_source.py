from myst.client import Client
from myst.openapi.models.deprecated_source_create import DeprecatedSourceCreate
from myst.openapi.models.source_get import SourceGet


def request_sync(client: Client, json_body: DeprecatedSourceCreate) -> SourceGet:
    """Creates a source."""

    return client.request(method="post", path=f"/sources/", response_class=SourceGet, request_model=json_body)
