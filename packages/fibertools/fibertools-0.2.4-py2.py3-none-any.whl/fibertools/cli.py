"""Console script for fibertools."""
#!/usr/bin/env python3
import argparse
from email.policy import default
import sys
import logging
from typing_extensions import Required
from fibertools.readutils import read_in_bed_file
from fibertools.trackhub import generate_trackhub
from fibertools.unionbg import bed2d4
import fibertools as ft
import numpy as np
import gzip
import pandas as pd


def make_bam2bed_parser(subparsers):
    parser = subparsers.add_parser(
        "bam2bed",
        help="Extract m6a calls from bam and output bed12.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )


def make_add_m6a_parser(subparsers):
    parser = subparsers.add_parser(
        "add-m6a",
        help="Make MSP features",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("bam", help="ccs bam file.")
    parser.add_argument("m6a", help="m6a bed12 file.")
    parser.add_argument(
        "-o", "--out", help="file to write output bam to.", default=sys.stdout
    )


def make_bed_split_parser(subparsers):
    parser = subparsers.add_parser(
        "split",
        help="Split a bed over many output files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("bed", help="A bed file")
    parser.add_argument(
        "-o", "--out-files", help="files to split input across", nargs="+"
    )


def make_trackhub_parser(subparsers):
    parser = subparsers.add_parser(
        "trackhub",
        help="Make a trackhub from a bed file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("bed", help="A bed file")
    parser.add_argument(
        "genome_file", help="A file with chromosome sizes for the genome."
    )
    parser.add_argument("-r", "--ref", default="hg38")
    parser.add_argument("-t", "--trackhub-dir", default="trackHub")
    parser.add_argument(
        "--spacer-size",
        help="adjust minimum distance between fibers for them to be in the same bin.",
        type=int,
        default=100,
    )


def make_bed2d4_parser(subparsers):
    parser = subparsers.add_parser(
        "bed2d4",
        help="Make a multi-track d4 file from a bed file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("bed", help="A bed file")
    parser.add_argument("d4", help="Output d4 file")
    parser.add_argument(
        "-g",
        "--genome",
        help="A file with chromosome sizes for the genome.",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--column",
        help="Name of the column to split the bed file on to make bed graphs.",
        default="name",
    )


def make_accessibility_model_parser(subparsers):
    parser = subparsers.add_parser(
        "model",
        help="Make MSP features",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("msp_bed12", help="MSP bed12 file.")
    parser.add_argument("m6a_bed12", help="m6a bed12 file.")
    parser.add_argument(
        "genome",
        help="Indexed fasta file to read in sequence context. Should have the same chromosomes as referenced in the first column of the two bed files.",
    )
    parser.add_argument("-d", "--dhs", help="dhs", default=None)
    parser.add_argument(
        "-b", "--bin_width", help="size of bin width to use", type=int, default=40
    )
    parser.add_argument(
        "--bin-num",
        help="Number of feature bins to work. Must be an odd number.",
        type=int,
        default=9,
    )
    parser.add_argument(
        "--min-tp-msp-len",
        help="min msp length to be in the DHS positive training set.",
        type=int,
        default=40,
    )
    parser.add_argument(
        "--spacer-size",
        help="adjust minimum distance between fibers for them to be in the same bin.",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--train-fdr", help="Training FDR used by mokapot.", type=float, default=0.10
    )
    parser.add_argument(
        "--test-fdr", help="Testing FDR used by mokapot.", type=float, default=0.05
    )
    parser.add_argument("-m", "--model", default=None)
    parser.add_argument(
        "-o", "--out", help="Write the accessibility model to this file."
    )
    parser.add_argument(
        "-n",
        "--n-rows",
        help="For debugging only reads in n rows.",
        type=int,
        default=None,
    )


def split_bed_over_files(args):
    bed = ft.read_in_bed_file(args.bed)
    logging.debug("Read in bed file.")
    index_splits = np.array_split(np.arange(bed.shape[0]), len(args.out_files))
    for index, out_file in zip(index_splits, args.out_files):
        if out_file.endswith(".gz"):
            with gzip.open(out_file, "wb") as f:
                bed[index].to_csv(f, sep="\t", has_header=False)
        else:
            bed[index].to_csv(out_file, sep="\t", has_header=False)


def parse():
    """Console script for fibertools."""
    parser = argparse.ArgumentParser(
        description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available subcommand for fibertools",
        required=True,
    )
    make_bam2bed_parser(subparsers)
    make_add_m6a_parser(subparsers)
    make_accessibility_model_parser(subparsers)
    make_bed_split_parser(subparsers)
    make_trackhub_parser(subparsers)
    make_bed2d4_parser(subparsers)
    # shared arguments
    parser.add_argument("-t", "--threads", help="n threads to use", type=int, default=1)
    parser.add_argument(
        "-v", "--verbose", help="increase logging verbosity", action="store_true"
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=ft.__version__),
    )
    args = parser.parse_args()

    log_format = "[%(levelname)s][Time elapsed (ms) %(relativeCreated)d]: %(message)s"
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(format=log_format, level=log_level)

    if args.command == "add_m6a":
        _m6a = ft.read_in_bed12_file(args.m6a)
    elif args.command == "model":
        fiberdata = ft.Fiberdata(
            args.msp_bed12,
            args.m6a_bed12,
            n_rows=args.n_rows,
        )
        AT_genome = ft.make_AT_genome(args.genome, fiberdata.both)
        dhs = read_in_bed_file(args.dhs, n_rows=args.n_rows)
        fiberdata.make_msp_features(
            AT_genome, bin_num=args.bin_num, bin_width=args.bin_width
        )
        fiberdata.make_percolator_input(dhs, min_tp_msp_len=args.min_tp_msp_len)

        if args.model is None:
            fiberdata.train_accessibility_model(args.out)
        else:
            fiberdata.predict_accessibility(args.model)
            fiberdata.accessibility.to_csv(args.out, sep="\t", index=False)
    elif args.command == "split":
        split_bed_over_files(args)
    elif args.command == "trackhub":
        df = pd.read_csv(args.bed, sep="\t")
        generate_trackhub(
            df,
            trackhub_dir=args.trackhub_dir,
            ref=args.ref,
            genome_file=args.genome_file,
            spacer_size=args.spacer_size,
        )
    elif args.command == "bed2d4":
        bed2d4(args)

    return 0
