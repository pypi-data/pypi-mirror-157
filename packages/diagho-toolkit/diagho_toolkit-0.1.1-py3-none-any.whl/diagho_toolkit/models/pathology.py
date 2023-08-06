from pydantic import BaseModel, Field
from typing import Dict, List, Union


class PathologyModel(BaseModel):
    name: str = Field(
        default="",
        description="The OMIM name of the pathology",
    )
    pathology_attributes: Dict[str, Union[str, List[str]]] = Field(
        default={},
        description="Attributes in relation with a pathology",
    )


class PathologyGeneAnnotationModel(BaseModel):
    gene_id: str = Field(
        default="",
        description="Gene id",
    )
    pathology_name: str = Field(
        default="", description="Pathology associated to a gene"
    )
    pathology_gene_annotation_attributes: Dict[str, str] = Field(
        default={},
        description="Attributes in relation with a pathology and a gene",
    )
