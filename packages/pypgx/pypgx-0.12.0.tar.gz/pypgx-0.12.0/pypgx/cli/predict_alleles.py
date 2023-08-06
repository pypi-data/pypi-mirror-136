import sys

from ..api import utils

import fuc
import pysam

description = f"""
Predict candidate star alleles based on observed variants.
"""

def create_parser(subparsers):
    parser = fuc.api.common._add_parser(
        subparsers,
        fuc.api.common._script_name(),
        description=description,
        help='Predict candidate star alleles based on observed \n'
             'variants.',
    )
    parser.add_argument(
        'consolidated_variants',
        metavar='consolidated-variants',
        help='Archive file with the semantic type \n'
             'VcfFrame[Consolidated].'
    )
    parser.add_argument(
        'alleles',
        help='Archive file with the semantic type \n'
             'SampleTable[Alleles].'
    )

def main(args):
    alleles = utils.predict_alleles(args.consolidated_variants)
    alleles.to_file(args.alleles)
