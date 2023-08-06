from codenames.game import Guess, Hint
from pydantic import BaseModel

from . import ModelIdentifier, Solver


class BaseResponse(BaseModel):
    status_code: int = 200


class LoadModelsResponse(BaseResponse):
    loaded_models_count: int


class GenerateHintResponse(BaseResponse):
    suggested_hint: Hint
    used_solver: Solver
    used_model_identifier: ModelIdentifier


class GenerateGuessResponse(BaseResponse):
    suggested_guess: Guess
    used_solver: Solver
    used_model_identifier: ModelIdentifier
