"""
xengsort
xenograft indexing and classification
by Jens Zentgraf & Sven Rahmann, 2019--2021
"""

import argparse
import os
from importlib import import_module  # dynamically import subcommand
from ._version import VERSION, DESCRIPTION


def index(p):
    """
    Hash all (unique) k-mers of the input files,
    and store values according to the given value set.
    """
    # required arguments: index and either --host and --graft or --precomputed
    p.add_argument("index", metavar="INDEX_HDF5",
        help="name of the resulting index HDF5 file (output)")
    p.add_argument("--host", "-H", metavar="FASTA", nargs="+",
        help="reference FASTA file(s) for the host organism")
    p.add_argument("--graft", "-G", metavar="FASTA", nargs="+",
        help="reference FASTA file(s) for the graft organism")
    p.add_argument("--precomputed", metavar="KMERS_VALUES",
        help="build index from precomputed k-mers/values, not from FASTA file(s)")
    # optional arguments
    p.add_argument('-v', '--valueset', nargs='+', default=['xenograft', '3'],
        help="value set with arguments, implemented in values.{VALUESET}.py")
    p.add_argument('-k', '--kmersize', metavar="INT", type=int, default=25,
        help="k-mer size")
    p.add_argument("--rcmode", metavar="MODE", default="max",
        choices=("f", "r", "both", "min", "max"),
        help="mode specifying how to encode k-mers")
    p.add_argument("--parameters", "-P", metavar="PARAMETER", nargs="+",
        help="provide parameters directly: "
            "[NOBJECTS TYPE[:ALIGNED] HASHFUNCTIONS PAGESIZE FILL], where "
            "NOBJECTS is the number of objects to be stored, "
            "TYPE[:ALIGNED] is the hash type implemented in hash_{TYPE}.py, "
            "and ALIGNED can be a or u for aligned and unaligned, "
            "HASHFUNCTIONS is a colon-separated list of hash functions, "
            "PAGESIZE is the number of elements on a page"
            "FILL is the desired fill rate of the hash table.") 
    p.add_argument("--shortcutbits", "-S", metavar="INT", type=int, choices=(0,1,2),
        help="number of shortcut bits (0,1,2), default: 0", default=0)
    p.add_argument("-c", "--chunkprefixlength", metavar="INT", type=int, default=2,
        help="calculate weak k-mers in chunks with common prefix of this length [2]")
    p.add_argument("-T", "--threads", "-j", metavar="INT", type=int, default=1,
        help="calculate weak kmers with this number of threads [1]")
    p.add_argument("--xenome", action="store_true",
        help="calculate weak k-mers as xenome does (merge weak host and weak graft)")
    # single parameter options for parameters
    p.add_argument("-n", "--nobjects", metavar="INT", type=int, required=True,
        help="upper bound on number of k-mers to be stored; "
            " for all 25-mers in the human and mouse genome and transcriptome, "
            " this number is roughly 4_500_000_000.")
    p.add_argument("--type", default="3FCVbb",
        help="hash type (e.g. 3FCVbb), implemented in hash_{TYPE}.py")
    p.add_argument("--unaligned", action="store_const", 
        const=False, dest="aligned", default=None,
        help="use unaligned pages (smaller, slightly slower; default)")
    p.add_argument("--aligned", action="store_const",
        const=True, dest="aligned", default=None,
        help="use power-of-two aligned pages (faster, but larger)")
    p.add_argument("--hashfunctions", "--functions",
        help="hash functions: 'default', 'random', or func1:func2[:func3]")
    p.add_argument("--pagesize", "-p", type=int, default=4,
        help="page size, i.e. number of elements on a page")
    p.add_argument("--fill", type=float, default=0.85,
        help="desired fill rate of the hash table")
    # less important options
    p.add_argument("--nostatistics", "--nostats", action="store_true",
        help="do not compute or show index statistics at the end")
    p.add_argument("--longwalkstats", action="store_true",
        help="show detailed random walk length statistics")
    p.add_argument("--maxwalk", metavar="INT", type=int, default=500,
        help="maximum length of random walk through hash table before failing [500]")
    p.add_argument("--maxfailures", metavar="INT", type=int, default=0, 
        help="continue even after this many failures [default:0; forever:-1]")
    p.add_argument("--walkseed", type=int, default=7,
        help="seed for random walks while inserting elements [7]")


def classify(p):
    gf = p.add_mutually_exclusive_group(required=True)
    gf.add_argument("--fasta", "-f", metavar="FASTA",
        help="FASTA file to classify")
    gf.add_argument("--fastq", "-q", metavar="FASTQ",
        help="single or first paired-end FASTQ file to classify")
    p.add_argument("--pairs", "-p", metavar="FASTQ",
        help="second paired-end FASTQ file (only together with --fastq)")
    p.add_argument("--index", metavar="INDEX_HDF5",
        help="existing index file (HDF5)")
    p.add_argument("--classification", "--mode", metavar="MODE",
        choices=("xenome", "majority", "xengsort"), default="xengsort",
        help="mode specifying how to classify reads ['xengsort']")
    p.add_argument("-T", "-j", "--threads", metavar="INT", type=int, default=4,
        help="maximum number of worker threads for classification [4]")
    p.add_argument("--prefix", "--out", "-o", required=True,
        help="prefix for output files (directory and name prefix);"
            " all output files with sorted reads will start with this prefix.")
    p.add_argument("--quick", action="store_true",
        help="quick mode (sample only a few k-mers per read)")
    p.add_argument("-P", "--prefetchlevel", metavar="INT", type=int, default=0, choices=(0,1,2),
        help="amount of prefetching: none (0, default); only second bucket (1); all buckets (2)")
    gmode = p.add_mutually_exclusive_group(required=False)
    gmode.add_argument("--count", action="store_true",
        help="only count reads or read pairs for each class, do not output FASTQ")
    gmode.add_argument("--filter", action="store_true",
        help="only output the graft FASTQ file, not the other class FASTQ files")
    p.add_argument("-C", "--chunksize", metavar="FLOAT_SIZE_MB",
        type=float, default=8.0,
        help="chunk size in MB [default: 8.0]; one chunk is allocated per thread.")
    p.add_argument("-R", "--chunkreads", metavar="INT", type=int,
        help="maximum number of reads per chunk per thread [SIZE_MB * 2**20 / 200]")

##### main argument parser #############################

def get_argument_parser():
    """
    return an ArgumentParser object
    that describes the command line interface (CLI)
    of this application
    """
    p = argparse.ArgumentParser(
        description = DESCRIPTION,
        epilog = "by Genome Informatics, University of Duisburg-Essen."
        )
    p.add_argument("--version", action="version", version=VERSION,
        help="show version and exit")

    subcommands = [
        ("index",
         "build an index for host and graft reference gneomes",
         index,
         "index", "main"),
         ("classify",
         "classify reads to host or graft genome",
         classify,
         "classify", "main")
    ]
    # add global options here
    # (none)
    # add subcommands to parser
    sps = p.add_subparsers(
        description="The xengsort application supports the following commands. "
            "Run 'xengsort COMMAND --help' for detailed information on each command.",
        metavar="COMMAND")
    sps.required = True
    sps.dest = 'subcommand'
    for (name, helptext, f_parser, module, f_main) in subcommands:
        if name.endswith('!'):
            name = name[:-1]
            chandler = 'resolve'
        else:
            chandler = 'error'
        sp = sps.add_parser(name, help=helptext,
            description=f_parser.__doc__, conflict_handler=chandler)
        sp.set_defaults(func=(module,f_main))
        f_parser(sp)
    return p


def main(args=None):
    p = get_argument_parser()
    pargs = p.parse_args() if args is None else p.parse_args(args)
    (module, f_main) = pargs.func

    # limits the number of usable threads in numba/prange
    # NOTE: option --threads must exist for EVERY module for this to work
    os.environ["OMP_NUM_THREADS"] = str(pargs.threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(pargs.threads)
    os.environ["MKL_NUM_THREADS"] = str(pargs.threads)
    os.environ["VECLIB_MAXIMUM_THREADS"] = str(pargs.threads)
    os.environ["NUMEXPR_NUM_THREADS"] = str(pargs.threads)
    os.environ["NUMBA_NUM_THREADS"] = str(pargs.threads)

    m = import_module("."+module, __package__)
    mymain = getattr(m, f_main)
    mymain(pargs)
