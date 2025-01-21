from pydantic import BaseModel


class UserRequest(BaseModel):
    """request for generate response."""

    input_user: str


class AccEval(BaseModel):
    """request file url for evaluate acc system."""

    path_url: str
