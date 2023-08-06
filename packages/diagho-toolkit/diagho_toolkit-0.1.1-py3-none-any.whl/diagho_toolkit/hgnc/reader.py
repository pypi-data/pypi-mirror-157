import logging
import csv
from io import TextIOWrapper
from pydantic import ValidationError
from typing import Generator, NewType, Union

from diagho_toolkit.models import GeneModel

logger = logging.getLogger(__name__)

HGNC_ENCODING = "utf_8"
HGNCIOWrapper = NewType("HGNCIOWrapper", TextIOWrapper)


def hgnc_reader(hgnc_filename: str) -> HGNCIOWrapper:
    return HGNCIOWrapper(
        open(hgnc_filename, mode="r", encoding=HGNC_ENCODING, errors="strict")
    )


def gene_reader(
    hgnc_stream: HGNCIOWrapper,
) -> Generator[Union[tuple[GeneModel, None], tuple[None, ValidationError]], None, None]:
    # Create CSV DictReader
    csv_hgnc_stream = csv.DictReader(hgnc_stream, delimiter="\t")

    for row in csv_hgnc_stream:
        # Clean attributes in row
        attributes = {k: v for k, v in row.items() if v != ""}

        # Make Gene attributes
        model_args = {
            "symbol": row["symbol"].upper(),
            "name": row["name"],
            "gene_type": row["locus_group"],
            "attributes": attributes,
        }

        # yield a Gene object or a ValidationError
        try:
            yield GeneModel(**model_args), None
        except ValidationError as e:
            yield None, e


def get_genes(hgnc_filename: str, seqid: str = "") -> Generator[GeneModel, None, None]:
    with hgnc_reader(hgnc_filename=hgnc_filename) as hgnc_stream:
        for gene, error in gene_reader(
            hgnc_stream=hgnc_stream,
        ):
            if error:
                logger.error(error.json())
            else:
                yield gene
