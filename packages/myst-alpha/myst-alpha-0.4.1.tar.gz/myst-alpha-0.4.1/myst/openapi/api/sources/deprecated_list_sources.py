from myst.client import Client
from myst.openapi.models.source_list import SourceList


def request_sync(client: Client) -> SourceList:
    """Lists sources."""

    return client.request(method="get", path=f"/sources/", response_class=SourceList)
