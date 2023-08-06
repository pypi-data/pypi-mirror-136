from typing import Any, List, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class DeprecatedTimeSeriesCreate(base_model.BaseModel):
    """Schema for time series create requests."""

    title: str
    project: str
    sample_period: str
    cell_shape: List[Any]
    coordinate_labels: List[Any]
    axis_labels: List[Any]
    object_: Optional[Literal["Node"]] = Field("Node", alias="object")
    type: Optional[Literal["TimeSeries"]] = "TimeSeries"
    description: Optional[str] = None
