from myst.client import Client
from myst.openapi.models.time_series_insert import TimeSeriesInsert
from myst.openapi.models.time_series_insert_result_get import TimeSeriesInsertResultGet


def request_sync(client: Client, uuid: str, json_body: TimeSeriesInsert) -> TimeSeriesInsertResultGet:
    """Inserts time series data."""

    return client.request(
        method="post",
        path=f"/time_series/{uuid}:insert",
        response_class=TimeSeriesInsertResultGet,
        request_model=json_body,
    )
