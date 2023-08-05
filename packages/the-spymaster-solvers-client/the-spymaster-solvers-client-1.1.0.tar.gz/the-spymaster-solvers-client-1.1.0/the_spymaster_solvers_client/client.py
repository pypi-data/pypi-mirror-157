import logging

from the_spymaster_util import wrap
from the_spymaster_util.http_client import BaseHttpClient

from .structs import (
    GenerateGuessRequest,
    GenerateGuessResponse,
    GenerateHintRequest,
    GenerateHintResponse,
    LoadModelsRequest,
    LoadModelsResponse,
)

log = logging.getLogger(__name__)
DEFAULT_BASE_URL = "http://localhost:5000"


class TheSpymasterSolversClient(BaseHttpClient):
    def __init__(self, base_url: str = None):
        if not base_url:
            base_url = DEFAULT_BASE_URL
        super().__init__(base_url=base_url)
        log.debug(f"Solvers client is using backend: {wrap(self.base_url)}")

    def generate_hint(self, request: GenerateHintRequest) -> GenerateHintResponse:
        data = self._post("generate-hint", data=request.dict())
        return GenerateHintResponse(**data)

    def generate_guess(self, request: GenerateGuessRequest) -> GenerateGuessResponse:
        data = self._post("generate-guess", data=request.dict())
        return GenerateGuessResponse(**data)

    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        data = self._post("load-models", data=request.dict())
        return LoadModelsResponse(**data)
