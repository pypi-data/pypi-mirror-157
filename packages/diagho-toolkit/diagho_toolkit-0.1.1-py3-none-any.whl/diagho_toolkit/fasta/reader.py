# WARNING ! :
# this module may change drasticaly later

import logging
from io import TextIOWrapper
from pydantic import ValidationError
from typing import Generator, NewType, Union

from diagho_toolkit.models import SequenceModel

logger = logging.getLogger(__name__)

FASTA_ENCODING = "utf_8"
FASTAIOWrapper = NewType("FASTAIOWrapper", TextIOWrapper)


def fasta_reader(fasta_filename: str) -> FASTAIOWrapper:
    return FASTAIOWrapper(
        open(fasta_filename, mode="r", encoding=FASTA_ENCODING, errors="strict")
    )


def sequence_reader(
    fasta_stream: FASTAIOWrapper,
) -> Generator[Union[tuple[SequenceModel, None], tuple[None, Exception]], None, None]:

    # filter rows begining with '>'
    for row in filter(lambda row: row[0] == ">", fasta_stream):

        # remove the first character '>' and the endline character '\n'
        cleaned_row: str = row[1:].rstrip()

        # split the line at the first space character
        # the results is a list with 1 or 2 str
        info: list[str] = cleaned_row.split(sep=" ", maxsplit=1)

        # yield a SequenceModel object or a ValidationError
        try:
            yield SequenceModel(**dict(zip(["name", "comment"], info))), None
        except ValidationError as e:
            yield None, e
