import logging
import sys

from diagho_toolkit.vcf.reader import get_contigs, get_variants

logger = logging.getLogger(__name__)


def main(arguments: list[str]) -> int:

    # Get the first argument as filename:
    try:
        filename = arguments[1]
    except IndexError as e:
        logger.error(e)
        return 1
    else:
        logger.info("filename: %s", filename)

    # Get contig names:
    for contig in get_contigs(vcf_filename=filename):
        logger.info(contig)

    # Log variants as vcf records:
    variants = get_variants(vcf_filename=filename)
    for variant in variants:
        logger.info(variant.get_vcf_data_line())

    return 0


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s",
        level=logging.DEBUG,
    )
    arguments: list[str] = sys.argv
    sys.exit(main(arguments))
