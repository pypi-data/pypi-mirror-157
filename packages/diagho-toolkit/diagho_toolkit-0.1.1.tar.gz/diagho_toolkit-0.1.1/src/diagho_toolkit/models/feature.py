from enum import Enum, IntEnum
from typing import Any, Dict, List

from pydantic import BaseModel, root_validator, validator


class StrandEnum(str, Enum):
    # The strand of the feature.
    # + for positive strand (relative to the landmark),
    # - for minus strand, and
    # . for features that are not stranded.
    # In addition, ? can be used for features whose strandedness is relevant,
    # but unknown.
    positive = "+"
    minus = "-"
    not_stranded = "."
    unknown = "?"


class PhaseEnum(IntEnum):
    # For features of type "CDS", the phase indicates where the next codon begins
    # relative to the 5' end (where the 5' end of the CDS is relative to the strand of
    # the CDS feature) of the current CDS feature.
    # A phase of "0" indicates that a codon begins on the first nucleotide of the CDS
    # feature (i.e. 0 bases forward),
    # a phase of "1" indicates that the codon begins at the second nucleotide of this
    # CDS feature and
    # a phase of "2" indicates that the codon begins at the third nucleotide of this
    # region.
    first = 0
    second = 1
    third = 2


class FeatureModel(BaseModel):
    seqid: str
    source: str = None
    feature_type: str
    start: int
    end: int
    score: float = None
    strand: StrandEnum
    phase: PhaseEnum = None

    attributes: Dict[str, Any] = None

    feature_id: str = None
    name: str = None
    aliases: List[str] = None
    parents: List[str] = None

    @validator("source", "score", "phase", "feature_id", "name", pre=True, always=True)
    def set_none_value(cls, v):
        if v in [".", ""]:
            return None
        return v

    @validator("attributes", pre=True, always=True)
    def set_attributes_none_value(cls, v):
        if v is None:
            return dict()
        return v

    @root_validator(pre=False)
    def get_tags_from_attributes(cls, values):
        attributes = values.get("attributes")

        if (not values["feature_id"]) and ("ID" in attributes):
            if len(attributes["ID"]):
                values["feature_id"] = attributes["ID"][0]

        if (not values["name"]) and ("Name" in attributes):
            if len(attributes["Name"]):
                values["name"] = attributes["Name"][0]

        if (not values["aliases"]) and ("Alias" in attributes):
            if len(attributes["Alias"]):
                values["aliases"] = attributes["Alias"]

        if (not values["parents"]) and ("Parent" in attributes):
            if len(attributes["Parent"]):
                values["parents"] = attributes["Parent"]

        return values
