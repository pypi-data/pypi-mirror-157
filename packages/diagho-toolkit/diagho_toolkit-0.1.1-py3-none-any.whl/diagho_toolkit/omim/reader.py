import logging
import re
from io import TextIOWrapper
from pydantic import ValidationError
from typing import Generator, List, NewType, Union, Dict

from diagho_toolkit.models import (
    PathologyModel,
    PathologyGeneAnnotationModel,
    GeneModel,
)

logger = logging.getLogger(__name__)

OMIM_ENCODING = "utf_8"
OMIMIOWrapper = NewType("OMIMIOWrapper", TextIOWrapper)


def omim_reader(omim_filename: str) -> OMIMIOWrapper:
    return OMIMIOWrapper(
        open(omim_filename, mode="r", encoding=OMIM_ENCODING, errors="strict")
    )


def gene_reader(
    omim_stream: OMIMIOWrapper,
) -> Generator[Union[tuple[GeneModel, None], tuple[None, ValidationError]], None, None]:
    for row in filter(lambda row: not row.startswith("#"), omim_stream):
        cleaned_row: str = row.rstrip()
        if cleaned_row:
            raw_columns: List[str] = cleaned_row.split(sep="\t")

            # Create gene attributes
            gene_attributes: Dict[str, List[str]]
            column_headers = [
                "chromosome",
                "genomicPositionStart",
                "genomicPositionEnd",
                "cytoLocation",
                "computedCytoLocation",
                "mimNumber",
                "geneSymbols",
                "geneName",
                "approvedGeneSymbol",
                "entrezGeneID",
                "ensemblGeneID",
                "comments",
            ]
            attributes = dict(zip(column_headers, [x for x in raw_columns[:11]]))
            gene_attributes = {
                k: v.split(",") for k, v in attributes.items() if v != ""
            }

            # Get gene symbol if it exists
            symbol: str = ""
            try:
                symbol = raw_columns[8]
            except IndexError as e:
                logger.info(e)

            # Get gene name if it exists
            name: str = ""
            try:
                name = raw_columns[7]
            except IndexError as e:
                logger.info(e)

            # yield a Gene object or a ValidationError
            try:
                yield GeneModel(
                    name=name,
                    symbol=symbol,
                    attributes=gene_attributes,
                ), None
            except ValidationError as e:
                yield None, e


def pathology_reader(
    omim_stream: OMIMIOWrapper,
) -> Generator[
    Union[tuple[PathologyModel, None], tuple[None, ValidationError]], None, None
]:
    for row in filter(lambda row: not row.startswith("#"), omim_stream):
        cleaned_row: str = row.rstrip()
        if cleaned_row:
            raw_columns: List[str] = cleaned_row.split(sep="\t")

            # Create Pathologies attributes
            pathology_string: str = ""
            try:
                pathology_string = raw_columns[12]
            except IndexError as e:
                logger.info(e)

            if pathology_string:
                for pathology in pathology_string.split(";"):
                    # Clean the pathology
                    pathology = pathology.strip()
                    pathology_attributes: Dict[str, Union[str, List[str]]] = {}
                    name: str = ""
                    # Long pathology
                    matcher = re.match(
                        r"^(.*),\s(\d{6})\s\((\d)\)(|, (.*))$", pathology
                    )
                    if matcher:
                        # Get the fields
                        name = matcher.group(1)
                        pathology_attributes = {
                            "mim_id": matcher.group(2),
                            "mapping_key": matcher.group(3),
                        }
                        inheritances = matcher.group(5)
                        # Get the inheritances, may or may not be there
                        if inheritances:
                            pathology_attributes["inheritances"] = inheritances.split(
                                ","
                            )

                    # Short pathology
                    else:
                        # Short pathology
                        matcher = re.match(r"^(.*)\((\d)\)(|, (.*))$", pathology)
                        if matcher:
                            # Get the fields
                            name = matcher.group(1)
                            pathology_attributes = {"mapping_key": matcher.group(2)}
                            inheritances = matcher.group(3)

                            # Get the inheritances, may or may not be there
                            if inheritances:
                                pathology_attributes[
                                    "inheritances"
                                ] = inheritances.split(",")

                    # yield a Pathology object or a ValidationError
                    try:
                        yield PathologyModel(
                            name=name,
                            pathology_attributes=pathology_attributes,
                        ), None
                    except ValidationError as e:
                        yield None, e


def pathology_gene_annotation_reader(
    omim_stream: OMIMIOWrapper,
) -> Generator[
    Union[tuple[PathologyGeneAnnotationModel, None], tuple[None, ValidationError]],
    None,
    None,
]:
    attributes_headers: List[str] = []
    for row in omim_stream:
        if row.startswith("# Chromosome"):
            # Get columns headers
            attributes_headers = row.rstrip().split(sep="\t")
            logging.info("Create attributes headers")

        else:
            cleaned_row: str = row.rstrip()
            if cleaned_row:
                raw_columns: List[str] = cleaned_row.split(sep="\t")

                gene_id: str = ""
                try:
                    gene_id = raw_columns[8]
                except IndexError as e:
                    logger.info(e)

                pathology_gene_annotation_attributes: Dict[str, str] = {}
                # Create Globals attributes
                if attributes_headers:
                    pathology_gene_annotation_attributes: Dict[str, str] = dict(
                        zip(attributes_headers, raw_columns)
                    )
                    # Remove fields without values
                    pathology_gene_annotation_attributes = {
                        k: v
                        for k, v in pathology_gene_annotation_attributes.items()
                        if v != ""
                    }

                # Get Pathology name
                pathology_string: str = ""
                try:
                    pathology_string = raw_columns[12]
                except IndexError as e:
                    logger.info(e)

                if pathology_string:
                    for pathology in pathology_string.split(";"):
                        # Clean the pathology
                        pathology = pathology.strip()
                        pathology_name: str = ""
                        # Long pathology
                        matcher = re.match(
                            r"^(.*),\s(\d{6})\s\((\d)\)(|, (.*))$", pathology
                        )
                        if matcher:
                            # Get the fields
                            pathology_name = matcher.group(1)

                        # Short pathology
                        else:
                            # Short pathology
                            matcher = re.match(r"^(.*)\((\d)\)(|, (.*))$", pathology)
                            if matcher:
                                # Get the fields
                                pathology_name = matcher.group(1)

                        # yield a PathologyGeneAnnotation object or a ValidationError
                        try:
                            yield PathologyGeneAnnotationModel(
                                gene_id=gene_id,
                                pathology_name=pathology_name,
                                pathology_gene_annotation_attributes=(
                                    pathology_gene_annotation_attributes
                                ),
                            ), None
                        except ValidationError as e:
                            yield None, e


def get_genes(omim_filename: str) -> Generator[GeneModel, None, None]:
    with omim_reader(omim_filename=omim_filename) as omim_stream:
        for gene, error in gene_reader(
            omim_stream=omim_stream,
        ):
            if error:
                logger.error(error.json())
            else:
                yield gene


def get_pathologies(omim_filename: str) -> Generator[PathologyModel, None, None]:
    with omim_reader(omim_filename=omim_filename) as omim_stream:
        for pathology, error in pathology_reader(
            omim_stream=omim_stream,
        ):
            if error:
                logger.error(error.json())
            else:
                yield pathology


def get_pathologies_genes_annotations(
    omim_filename: str,
) -> Generator[PathologyGeneAnnotationModel, None, None]:
    with omim_reader(omim_filename=omim_filename) as omim_stream:
        for pathology_gene_annotation, error in pathology_gene_annotation_reader(
            omim_stream=omim_stream,
        ):
            if error:
                logger.error(error.json())
            else:
                yield pathology_gene_annotation
