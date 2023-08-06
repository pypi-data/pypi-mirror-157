"""
https://samtools.github.io/hts-specs/VCFv4.3.pdf
"""

import logging

from contextlib import contextmanager
from cyvcf2 import VCF
from cyvcf2.cyvcf2 import Variant
from pydantic import ValidationError
from typing import Generator, List, NewType, Union

from diagho_toolkit.models import SampleModel, VariantModel

logger = logging.getLogger(__name__)

VCFIOWrapper = NewType("VCFIOWrapper", Generator[Variant, None, None])


@contextmanager
def vcf_reader(vcf_filename: str) -> VCFIOWrapper:
    vcf = VCF(
        fname=vcf_filename,
        # If gts012==True, then gt_types will be 0=HOM_REF, 1=HET, 2=HOM_ALT, 3=UNKNOWN.
        # If gts012==False, 3, 2 are flipped.
        gts012=True,
        # If lazy==True, then don’t unpack (parse) the underlying record until needed.
        lazy=True,
        # If strict_gt==True, then any ‘.’ present in a genotype will classify the
        # corresponding element in the gt_types array as UNKNOWN.
        strict_gt=False,
        # List of samples to extract from full set in file.
        samples=None,
        # The number of threads to use including this reader.
        threads=None,
    )
    try:
        yield vcf
    except Exception as e:
        logger.error(e)
    finally:
        pass


def contig_reader(
    vcf_stream: VCFIOWrapper,
) -> Generator[Union[tuple[str, None], tuple[None, ValidationError]], None, None]:

    seen_contigs = []

    for record in vcf_stream:
        contig = record.CHROM

        if contig not in seen_contigs:
            seen_contigs.append(contig)
            yield contig, None


def variant_reader(
    vcf_stream: VCFIOWrapper, contig: str = ""
) -> Generator[
    Union[tuple[VariantModel, None], tuple[None, ValidationError]], None, None
]:

    samples = vcf_stream.samples

    for record in vcf_stream:

        # yield a VariantModel object or a ValidationError
        # WARNING : we guess the VCF file is decomposed !
        try:
            if contig and record.CHROM != contig:
                pass
            else:
                variant = VariantModel(
                    chrom=record.CHROM,
                    pos=record.POS,
                    ids=record.ID.split(";") if record.ID else [],
                    ref=record.REF,
                    alt=record.ALT[0] if record.ALT else ".",
                    qual=record.QUAL,
                    filters=record.FILTER.split(";") if record.FILTER else [],
                    infos=dict(record.INFO),
                )

                if samples:

                    # GT
                    gt_allele_1, gt_allele_2, gt_phased = tuple(
                        map(list, zip(*record.genotypes))
                    )
                    gt_type = list(record.gt_types)

                    # AD
                    ad_allele_1 = list(record.gt_ref_depths)
                    ad_allele_2 = list(record.gt_alt_depths)

                    # DP
                    dp = list(record.gt_depths)

                    # GQ
                    gq = list(record.gt_quals)

                    field_value_list = [
                        samples,  # sample name list
                        gt_allele_1,  # GT
                        gt_allele_2,  # GT
                        gt_phased,  # GT
                        gt_type,  # GT
                        ad_allele_1,  # AD
                        ad_allele_2,  # AD
                        dp,  # DP
                        gq,  # GQ
                    ]

                    field_name_list = [
                        "name",
                        "gt_allele_1",  # GT
                        "gt_allele_2",  # GT
                        "gt_phased",  # GT
                        "gt_type",  # GT
                        "ad_allele_1",  # AD
                        "ad_allele_2",  # AD
                        "dp",  # DP
                        "gq",  # GQ
                    ]

                    for sample_value_list in map(list, zip(*field_value_list)):
                        sample_dict = dict(zip(field_name_list, sample_value_list))
                        sample = SampleModel.parse_obj(sample_dict)
                        variant.samples.append(sample)

                yield variant, None

        except ValidationError as e:
            yield None, e


def get_variants(
    vcf_filename: str, contig: str = ""
) -> Generator[VariantModel, None, None]:
    with vcf_reader(vcf_filename=vcf_filename) as vcf_stream:
        for variant, error in variant_reader(vcf_stream=vcf_stream, contig=contig):
            if error:
                logger.error(error.json())
            else:
                yield variant


def get_samples(vcf_filename: str) -> List[str]:
    """Returns a list of samples pulled from the VCF."""

    with vcf_reader(vcf_filename=vcf_filename) as vcf_stream:
        return vcf_stream.samples


def get_seqnames(vcf_filename: str) -> List[str]:
    """Returns a list of chromosomes in the VCF."""

    with vcf_reader(vcf_filename=vcf_filename) as vcf_stream:
        return vcf_stream.seqnames


def get_contigs(vcf_filename: str) -> Generator[str, None, None]:
    with vcf_reader(vcf_filename=vcf_filename) as vcf_stream:
        for contig, error in contig_reader(vcf_stream=vcf_stream):
            if error:
                logger.error(error.json())
            else:
                yield contig
