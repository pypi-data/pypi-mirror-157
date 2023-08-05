import pydantic

from captur_ml_sdk.dtypes import ImageClassificationResult
from typing import List


class LivePredictionRequest(pydantic.BaseModel):
    endpoint_id: str = pydantic.Field(
        "",
        description="The ID of the VertexAI endpoint to use for prediction.",
    )
    image_url: str = pydantic.Field(
        "",
        description="The URL of the image to use for prediction.",
    )

class LivePredictionResponse(pydantic.BaseModel):
    endpoint_id: str = pydantic.Field(
        "",
        description='The ID of the VertexAI endpoint used for the prediction.'
    )
    images: List[ImageClassificationResult] = pydantic.Field(
        "",
        description='The list of classification results for the images used for the prediction.'
    )
