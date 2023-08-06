import collections
from io import TextIOWrapper
import logging
from pydantic import ValidationError
import re
from typing import Generator, List, NewType, Union, Dict

from diagho_toolkit.models import (
    GeneModel,
    SymptomGeneAnnotationModel,
    SymptomHierarchyModel,
    SymptomModel,
)

logger = logging.getLogger(__name__)

HPO_ENCODING = "utf_8"
HPOIOWrapper = NewType("HPOIOWrapper", TextIOWrapper)

TAG_AND_VALUE_REGEX = "(?P<tag>[^:]+):(?P<value>[^!]+)"
ONLY_ONE_ALLOWED_PER_STANZA = set(["id", "name", "def", "comment"])


def hpo_reader(hpo_filename: str) -> HPOIOWrapper:
    return HPOIOWrapper(
        open(hpo_filename, mode="r", encoding=HPO_ENCODING, errors="strict")
    )


def hpo_obo_parser(hpo_stream: HPOIOWrapper) -> Dict[str, Union[str, List[str]]]:
    obo_records_dict = {}
    current_stanza_type: str = ""
    current_record = {}
    for row in hpo_stream:
        if row.startswith("["):
            current_stanza_type = row.strip("[]\n")
            continue

        # skip header rows and stanzas that aren't "Terms"
        if current_stanza_type != "Term":
            continue

        # remove new-row character and any comments
        row = row.strip().split("!")[0]
        if len(row) == 0:
            continue

        match = re.match(TAG_AND_VALUE_REGEX, row)
        if not match:
            raise ValueError("Unexpected row format: %s" % str(row))

        tag = match.group("tag")
        value = match.group("value").strip()

        if tag == "id":
            current_record = collections.defaultdict(list)
            obo_records_dict[value] = current_record

        if tag in ONLY_ONE_ALLOWED_PER_STANZA:
            if tag in current_record:
                raise ValueError(
                    "More than one '%s' found in %s stanza: %s"
                    % (
                        tag,
                        current_stanza_type,
                        ", ".join([current_record[tag], value]),
                    )
                )

            current_record[tag] = value
        else:
            current_record[tag].append(value)

    return obo_records_dict


def symptom_reader(
    hpo_stream: HPOIOWrapper,
) -> Generator[
    Union[tuple[SymptomModel, None], tuple[None, ValidationError]],
    None,
    None,
]:
    for item in hpo_obo_parser(hpo_stream).values():

        # Get name
        name: str = item["name"]

        # Get symptom ID
        symptom_id: str = item["id"]

        # yield a SymptomModel object or a ValidationError
        try:
            yield SymptomModel(
                name=name,
                symptom_id=symptom_id,
                attributes=item,
            ), None
        except ValidationError as e:
            yield None, e


def symptom_hierarchy_reader(
    hpo_stream: HPOIOWrapper,
) -> Generator[
    Union[tuple[SymptomHierarchyModel, None], tuple[None, ValidationError]],
    None,
    None,
]:
    for item in hpo_obo_parser(hpo_stream).values():

        # Get child_id
        child_id: str = item["id"]

        # Get parents_ids
        parents_ids: List[str] = []
        parents_ids.extend(item["is_a"])

        # yield a SymptomModel object or a ValidationError
        try:
            yield SymptomHierarchyModel(
                child_id=child_id,
                parents_ids=parents_ids,
            ), None
        except ValidationError as e:
            yield None, e


def gene_reader(
    hpo_stream: HPOIOWrapper,
) -> Generator[
    Union[tuple[GeneModel, None], tuple[None, ValidationError]],
    None,
    None,
]:
    attributes_headers: List[str] = []
    attributes: Dict[str, Union[str, List[str]]] = {}
    for row in hpo_stream:
        cleaned_row: str = row.strip()
        if row.startswith("#"):
            attributes_headers = cleaned_row.split(sep="<tab>")
            attributes_headers[0] = attributes_headers[0].split(sep=":")[1].strip()
        else:
            raw_columns: List[str] = cleaned_row.split(sep="\t")

            # Get gene_id
            symbol: str = ""
            try:
                symbol = raw_columns[1]
            except IndexError as e:
                logger.info(e)

            attributes = dict(zip(attributes_headers, raw_columns))

            # yield a SymptomGeneAnnotationModel object or a ValidationError
            try:
                yield GeneModel(
                    symbol=symbol,
                    attributes=attributes,
                ), None
            except ValidationError as e:
                yield None, e


def symptom_gene_annotation_reader(
    hpo_stream: HPOIOWrapper,
) -> Generator[
    Union[tuple[SymptomGeneAnnotationModel, None], tuple[None, ValidationError]],
    None,
    None,
]:
    attributes_headers: List[str] = []
    attributes: Dict[str, List[str]] = {}

    for row in hpo_stream:
        cleaned_row: str = row.strip()
        if row.startswith("#"):
            attributes_headers = cleaned_row.split(sep="<tab>")
            attributes_headers[0] = attributes_headers[0].split(sep=":")[1].strip()
        else:
            raw_columns: List[str] = cleaned_row.split(sep="\t")

            # Get gene_id
            gene_id: str = ""
            try:
                gene_id = raw_columns[3]
            except IndexError as e:
                logger.info(e)

            # Get symptom_id
            symptom_id: str = ""
            try:
                symptom_id = raw_columns[0]
            except IndexError as e:
                logger.info(e)

            attributes = dict(zip(attributes_headers, raw_columns))

            # yield a SymptomGeneAnnotationModel object or a ValidationError
            try:
                yield SymptomGeneAnnotationModel(
                    gene_id=gene_id,
                    symptom_id=symptom_id,
                    attributes=attributes,
                ), None
            except ValidationError as e:
                yield None, e


def get_symptoms(hpo_obo_filename: str) -> Generator[SymptomModel, None, None]:
    with hpo_reader(hpo_filename=hpo_obo_filename) as hpo_stream:
        for symptom, error in symptom_reader(
            hpo_stream=hpo_stream,
        ):
            if error:
                logger.error(error.json())
            else:
                yield symptom


def get_symptoms_hierarchies(
    hpo_obo_filename: str,
) -> Generator[SymptomHierarchyModel, None, None]:
    with hpo_reader(hpo_filename=hpo_obo_filename) as hpo_stream:
        for symptom_hierarchy, error in symptom_hierarchy_reader(
            hpo_stream=hpo_stream,
        ):
            if error:
                logger.error(error.json())
            else:
                yield symptom_hierarchy


def get_symptoms_genes_annotations(
    hpo_p2g_filename: str,
) -> Generator[SymptomGeneAnnotationModel, None, None]:
    with hpo_reader(hpo_filename=hpo_p2g_filename) as hpo_stream:
        for symtom_gene_annotation, error in symptom_gene_annotation_reader(
            hpo_stream=hpo_stream,
        ):
            if error:
                logger.error(error.json())
            else:
                yield symtom_gene_annotation


def get_genes(
    hpo_g2p_filename: str,
) -> Generator[GeneModel, None, None]:
    with hpo_reader(hpo_filename=hpo_g2p_filename) as hpo_stream:
        for gene, error in gene_reader(
            hpo_stream=hpo_stream,
        ):
            if error:
                logger.error(error.json())
            else:
                yield gene
