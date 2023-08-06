"""
https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md
"""

import logging
import re
from io import TextIOWrapper
from pydantic import ValidationError
from typing import Dict, Generator, List, NewType, Union

from diagho_toolkit.models import FeatureModel, RegionModel

logger = logging.getLogger(__name__)

GFF3_ENCODING = "utf_8"
GFF3IOWrapper = NewType("GFF3IOWrapper", TextIOWrapper)


def gff3_reader(gff3_filename: str) -> GFF3IOWrapper:
    return GFF3IOWrapper(
        open(gff3_filename, mode="r", encoding=GFF3_ENCODING, errors="strict")
    )


def directive_reader(gff3_stream: GFF3IOWrapper) -> Generator[str, None, None]:

    # filter rows begining with '##'
    for row in filter(lambda row: row[0:2] == "##", gff3_stream):

        # remove the first two characters '##' and the endline character '\n'
        cleaned_row: str = row[2:].rstrip()

        # yield the cleaned row
        yield cleaned_row


def region_reader(
    gff3_stream: GFF3IOWrapper,
) -> Generator[
    Union[tuple[RegionModel, None], tuple[None, ValidationError]], None, None
]:

    # filter rows begining with '##sequence-region'
    for row in filter(lambda row: row.startswith("##sequence-region"), gff3_stream):

        # remove the endline character '\n'
        cleaned_row: str = row.rstrip()

        # remove multiple spaces
        cleaned_row = re.sub(" +", " ", cleaned_row)

        # split the result in list of str
        info: list[str] = cleaned_row.split(sep=" ")

        # yield a RegionModel object or a ValidationError
        try:
            yield RegionModel(
                **dict(zip(["directive", "seqid", "start", "end"], info))
            ), None
        except ValidationError as e:
            yield None, e


def feature_reader(
    gff3_stream: GFF3IOWrapper,
    seqid: str = "",
    feature_type: str = "",
) -> Generator[
    Union[tuple[FeatureModel, None], tuple[None, ValidationError]], None, None
]:

    if seqid and feature_type:
        rx = re.compile(f"^{seqid}\t([a-zA-Z0-9.]+)\t{feature_type}\t")
        my_filter = filter(lambda row: rx.match(row), gff3_stream)
    elif seqid:
        rx = re.compile(f"^{seqid}\t")
        my_filter = filter(lambda row: rx.match(row), gff3_stream)
    elif feature_type:
        rx = re.compile(f"^([a-zA-Z0-9.]+)\t([a-zA-Z0-9.]+)\t{feature_type}\t")
        my_filter = filter(lambda row: rx.match(row), gff3_stream)
    else:
        my_filter = filter(lambda row: row[0] != "#", gff3_stream)

    # filter rows begining with '#'
    for row in my_filter:

        # remove the endline character '\n'
        cleaned_row: str = row.rstrip()

        # skip empty lines
        if cleaned_row:

            raw_columns: list[str] = cleaned_row.split(sep="\t")

            column_headers = [
                "seqid",
                "source",
                "feature_type",
                "start",
                "end",
                "score",
                "strand",
                "phase",
                # "attributes",
            ]

            decoded_row: dict[str, Union[str, Dict[str, List[str]]]] = dict(
                zip(column_headers, raw_columns)
            )

            # Column 9: "attributes"
            try:
                raw_attributes = raw_columns[8].split(";")

                decoded_row["attributes"] = {}

                for raw_attribute in raw_attributes:
                    tag, _, raw_values = raw_attribute.partition("=")

                    decoded_values = raw_values.split(",")

                    decoded_row["attributes"][tag] = decoded_values

            except IndexError:
                # There is no 'attributes' column!
                pass

            # yield a FeatureModel object or a ValidationError
            try:
                yield FeatureModel(**decoded_row), None
            except ValidationError as e:
                yield None, e


def get_regions(gff3_filename: str) -> Generator[RegionModel, None, None]:
    with gff3_reader(gff3_filename=gff3_filename) as gff3_stream:
        for region, error in region_reader(gff3_stream=gff3_stream):
            if error:
                logger.error(error.json())
            else:
                yield region


def get_features(
    gff3_filename: str, seqid: str = "", feature_type: str = ""
) -> Generator[FeatureModel, None, None]:
    with gff3_reader(gff3_filename=gff3_filename) as gff3_stream:
        for feature, error in feature_reader(
            gff3_stream=gff3_stream,
            seqid=seqid,
            feature_type=feature_type,
        ):
            if error:
                logger.error(error.json())
            else:
                yield feature
