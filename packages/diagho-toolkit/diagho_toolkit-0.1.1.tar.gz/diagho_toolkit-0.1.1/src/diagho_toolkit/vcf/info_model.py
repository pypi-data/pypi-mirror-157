# WARNING !
# This may be change drasticaly, move, and/or delete soon

"""Print pydantic models template of a VCF infos fields

    usage :
        python info_model_parser.py [file.vcf] [field_chosen.txt]
    first sys argument must be a vcf file second sys
    argument can be a text file with the field wanted
    (1 line 1 field). if there is no second argument, all
    field will be taken.

"""
import sys
import logging

logger = logging.getLogger(__name__)


def main(arguments: list[str]) -> int:

    try:
        vcf_file = arguments[1]
    except IndexError as err:
        logger.error(err)
        logger.error("vcf file missing")
        return 1

    if vcf_file.split(".")[-1] != "vcf":
        logger.error("First arg must be a .vcf file")
        return 1

    try:
        fields = arguments[2]
        with open(fields, "r") as f:
            field_list = [line.rstrip() for line in f.readlines()]
        all_field = False

    except IndexError as err:
        logger.info(err)
        all_field = True
        field_list = []

    model_info = "\n"
    with open(vcf_file) as f:
        for line in f.readlines():
            if line[0:6] == "##INFO":
                if field_list.count(line.split(",")[0][11:]) or all_field:
                    line_split = line.split(",")
                    NAME = line_split[0][11:]
                    TYPE = line_split[2][5:]
                    if TYPE == "Float":
                        TYPE = "float"
                    elif TYPE == "Integer":
                        TYPE = "int"
                    elif TYPE == "String" or TYPE == "Character":
                        TYPE = "str"
                    elif TYPE == "Flag":
                        TYPE = "NoneType"
                    DESCRIPTION = line.split('Description="')[1][0:-3]
                    DESCRIPTION = "'".join(DESCRIPTION.split('"'))
                    model_info += (
                        '{0}: {1} = Field(default = None,description="{2}")\n'.format(
                            NAME, TYPE, DESCRIPTION
                        )
                    )
            elif line[0:6] == "#CHROM":
                break
        model_info.rstrip()

    logger.info(model_info)
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s",
        level=logging.DEBUG,
    )
    arguments: list[str] = sys.argv
    sys.exit(main(arguments))
