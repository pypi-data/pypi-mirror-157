import re
from typing import Any, Dict, List
from pydantic import BaseModel, Field, PositiveInt, validator


class SampleModel(BaseModel):
    name: str = Field(
        "",
        description="Sample name in the VCF file.",
    )

    # GT
    gt_allele_1: int = Field(
        -1,
        title="First Allele",
        description="First allele: 0 for the reference allele, 1 for the alternate "
        "allele (-1 for missing information).",
    )
    gt_allele_2: int = Field(
        -1,
        title="Second Allele",
        description="First allele: 0 for the reference allele, 1 for the alternate "
        "allele (-1 for missing information).",
    )
    gt_phased: bool = Field(
        True,
        title="Phasing",
        description="Genotype phasing.",
    )
    gt_type: int = Field(
        3,
        title="Type",
        description="Genotype type: 0=HOM_REF, 1=HET, 2=HOM_ALT, 3=UNKNOWN.",
    )

    # AD
    ad_allele_1: int = Field(
        -1,
        title="AD_1",
        description="Total read depths for allele 1 (-1 for missing information).",
    )
    ad_allele_2: int = Field(
        -1,
        title="AD_2",
        description="Total read depths for allele 2 (-1 for missing information).",
    )

    # DP
    dp: int = Field(
        -1,
        title="DP",
        description="Read depth at this position for this sample (-1 for missing "
        "information).",
    )

    # GQ
    gq: int = Field(
        -1,
        title="GQ",
        description="Conditional genotype quality, encoded as a phred quality (-1 for "
        "missing information).",
    )

    @classmethod
    def get_vcf_data_line_format(cls):
        return "GT:AD:DP:GQ"

    def get_vcf_data_line(self):
        # GT
        vcf_data_line = "{gt_allele_1}{gt_phased}{gt_allele_2}".format(
            gt_allele_1=self.gt_allele_1 if self.gt_allele_1 >= 0 else ".",
            gt_phased="|" if self.gt_phased else "/",
            gt_allele_2=self.gt_allele_2 if self.gt_allele_2 >= 0 else ".",
        )

        # AD
        if self.ad_allele_1 >= 0 and self.ad_allele_2 >= 0:
            vcf_data_line += ":{ad_allele_1},{ad_allele_2}".format(
                ad_allele_1=self.ad_allele_1,
                ad_allele_2=self.ad_allele_2,
            )

            # DP
            if self.dp >= 0:
                vcf_data_line += ":{dp}".format(dp=self.dp)

                # GQ
                if self.gq >= 0:
                    vcf_data_line += ":{gq}".format(gq=self.gq)

        return vcf_data_line


class VariantModel(BaseModel):
    chrom: str = Field(..., example="20")
    pos: PositiveInt = Field(..., example=1234567)
    ids: List[str] = Field([], example=["."])
    ref: str = Field(..., example="A")
    alt: str = Field(..., example="C")
    qual: float = None
    filters: List[str] = []

    infos: Dict[str, Any] = None

    samples: List[SampleModel] = []

    @validator("ref")
    def ref_must_be_valid_base(cls, v):
        p = re.compile(r"^([ACGTNacgtn]+)$")
        if not p.match(v):
            raise ValueError("Must contain one or more characters in A,C,G,T,N.")
        return v.upper()

    @validator("alt")
    def alt_must_be_valid_base(cls, v):
        p = re.compile(r"^([ACGTNacgtn]+|\*|\.)$")
        if not p.match(v):
            raise ValueError("Must contain . or * or a list of A,C,G,T,N bases.")
        return v.upper()

    @validator("chrom")
    def must_be_valid_contig_name(cls, v):
        p = re.compile(
            r"^([0-9A-Za-z!#$%&+./:;?@^_|~-][0-9A-Za-z!#$%&*+./:;=?@^_|~-]*)$"
        )
        if not p.match(v):
            raise ValueError(
                'Must contain any printableASCII characters in the range[!-~]apart from ‘\\ , "‘’ () [] {} <>’ and may not start with ‘*’ or ‘=’.'  # noqa 501
            )
        return v

    @validator("ids")
    def must_be_valid_id_name(cls, v):
        p = re.compile(r"^([a-zA-Z0-9_-]+|\.)$")
        for id in v:
            if not p.match(id):
                raise ValueError(
                    "Must contain String, no whitespace or semicolons permitted."
                )
        return v

    @validator("infos", pre=True, always=True)
    def set_infos_none_value(cls, v):
        if v is None:
            return dict()
        return v

    def get_vcf_header_line(self):
        vcf_header_line = "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
        if self.samples:
            vcf_header_line += "\tFORMAT"
            for sample in self.samples:
                vcf_header_line += "\t%s" % sample.name
        return vcf_header_line

    def get_vcf_data_line_without_sample(self):
        vcf_data_line = "{chrom}\t{pos}\t{id}\t{ref}\t{alt}\t{qual}\t{filter}\t{info}".format(  # noqa E501
            chrom=self.chrom,
            pos=self.pos,
            id=";".join(self.ids) if self.ids else ".",
            ref=self.ref,
            alt=self.alt,
            qual=round(self.qual, 2) if self.qual else ".",
            filter=";".join(self.filters) if self.filters else ".",
            info=";".join(["=".join([k, str(v)]) for k, v in self.infos.items()]),
        )
        return vcf_data_line

    def get_vcf_data_line(self):
        vcf_data_line = self.get_vcf_data_line_without_sample()
        if self.samples:
            vcf_data_line += "\t" + SampleModel.get_vcf_data_line_format()
            for sample in self.samples:
                vcf_data_line += "\t" + sample.get_vcf_data_line()
        return vcf_data_line
