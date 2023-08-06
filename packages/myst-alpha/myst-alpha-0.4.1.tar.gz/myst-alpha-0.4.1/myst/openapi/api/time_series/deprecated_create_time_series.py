from myst.client import Client
from myst.openapi.models.deprecated_time_series_create import DeprecatedTimeSeriesCreate
from myst.openapi.models.time_series_get import TimeSeriesGet


def request_sync(client: Client, json_body: DeprecatedTimeSeriesCreate) -> TimeSeriesGet:
    """Creates a time series."""

    return client.request(method="post", path=f"/time_series/", response_class=TimeSeriesGet, request_model=json_body)
