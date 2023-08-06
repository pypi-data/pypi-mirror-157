from captur_ml_sdk.dtypes.generics import Image, LivePredictMeta

from pydantic import (
    BaseModel
)
from typing import Optional


class Model(BaseModel):
    endpoint_id: str
    type: str

    class Config:
        arbitrary_types_allowed = True


class ModelLivePredictRequest(BaseModel):
    meta: Optional[LivePredictMeta] = None
    model: Model
    data: Image
