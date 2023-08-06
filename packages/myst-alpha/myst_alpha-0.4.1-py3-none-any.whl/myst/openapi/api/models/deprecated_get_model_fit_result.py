from myst.client import Client
from myst.openapi.models.model_fit_result_get import ModelFitResultGet


def request_sync(client: Client, model_uuid: str, uuid: str) -> ModelFitResultGet:
    """Gets a model fit result by its unique identifier."""

    return client.request(
        method="get", path=f"/models/{model_uuid}/model_fit_results/{uuid}", response_class=ModelFitResultGet
    )
