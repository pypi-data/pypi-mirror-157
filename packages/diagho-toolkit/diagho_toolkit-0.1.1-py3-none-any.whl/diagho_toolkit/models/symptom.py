from pydantic import BaseModel, Field
from typing import Dict, List, Union


class SymptomModel(BaseModel):
    name: str = Field(
        default="",
        description="The HPO name of the symptom",
    )
    symptom_id: str = Field(
        default="",
        description="HPO ID for a symptom",
    )
    attributes: Dict[str, Union[str, List[str]]] = Field(
        default={},
        description="Attributes in relation with a symptom",
    )


class SymptomHierarchyModel(BaseModel):
    child_id: str = Field(default="", description="ID corresponding to a child symptom")
    parents_ids: List[str] = Field(
        default=[], description="Id corresponding to a parent symptom"
    )


class SymptomGeneAnnotationModel(BaseModel):
    gene_id: str = Field(default="", description="ID corresponding to the gene")
    symptom_id: str = Field(default="", description="ID corresponding to the symptom")
    attributes: Dict[str, Union[str, List[str]]] = Field(
        default={},
        description="Attributes in relation with a symptom",
    )
