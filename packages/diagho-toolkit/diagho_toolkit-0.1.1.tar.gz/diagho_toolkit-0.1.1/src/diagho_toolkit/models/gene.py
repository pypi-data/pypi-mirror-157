from pydantic import BaseModel, Field
from typing import Dict, List, Union


class GeneModel(BaseModel):
    symbol: str = Field(
        default="",
        description="The HGNC approved gene symbol. Equates to the "
        "APPROVED SYMBOL field within the gene symbol report.",
    )
    name: str = Field(
        default="",
        description="HGNC approved name for the gene. Equates to the "
        "APPROVED NAME field within the gene symbol report.",
    )
    gene_type: str = Field(
        default="", description="A group name for a set of related locus types "
    )
    attributes: Dict[str, Union[str, List[str]]] = Field(
        default={},
        description="All metadata in relation with a gene",
    )
