from pydantic import BaseModel


class URLrequest(BaseModel):
    """request for upload data and insert into database."""

    url: str
