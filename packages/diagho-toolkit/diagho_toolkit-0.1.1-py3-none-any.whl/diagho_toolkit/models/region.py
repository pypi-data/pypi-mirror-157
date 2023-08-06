from pydantic import BaseModel


class RegionModel(BaseModel):
    seqid: str = ""
    start: int = 0
    end: int = 0
