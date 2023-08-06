from pydantic import BaseModel


class SequenceModel(BaseModel):
    name: str = ""
    comment: str = None
