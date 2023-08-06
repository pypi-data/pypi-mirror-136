from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class ProjectCreate(base_model.BaseModel):
    """Schema for project create requests."""

    title: str
    object_: Optional[Literal["Project"]] = Field("Project", alias="object")
    description: Optional[str] = None
