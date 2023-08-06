"""
Module for creating training data from GateNLP documents
"""
# NOTE: this simple sends all documents to Conll2003FileDestination

import os
import argparse
import logging
from gatenlp.corpora.export import Conll2003FileDestination
from gatenlp.corpora.dirs import DirFilesSource
from gatenlp.utils import init_logger


def build_argparser():
    argparser = argparse.ArgumentParser(
        description="Export token classification training data from a directory of documents"
    )
    argparser.add_argument("docdir", type=str,
                           help="Input directory"
                           )
    argparser.add_argument("outdir", type=str,
                           help="A directory where the output files are stored")
    argparser.add_argument("--outfile", type=str, default="train.txt",
                           help="The file name of the conll format file in outdir (train.txt)")
    argparser.add_argument("--recursive", action="store_true",
                           help="If specified, process all matching documents in the directory tree")
    argparser.add_argument("--exts", nargs="+", default=[".bdocjs"],
                           help="File extensions to process (.bdocjs)")
    argparser.add_argument("--on_error", choices=["exit", "log", "ignore"], default="exit",
                           help="What to do if an error occurs writing the data for a document")
    argparser.add_argument("--fmt", type=str, default=None,
                           help="File format to expect for the matching documents (None: infer from extension)")
    argparser.add_argument("--annset_name", type=str, default="",
                           help="Annotation set name to use (default annotation set)")
    argparser.add_argument("--sentence_type", type=str,
                           help="Sentence/sequence annotation type (default: None, use whole document)")
    argparser.add_argument("--token_type", type=str, default="Token",
                           help="Token annotation type (Token)")
    argparser.add_argument("--token_feature", type=str,
                           help="Token feature name to get the string from (None: get from document text)")
    argparser.add_argument("--chunk_types", nargs="*",
                           help="Annotation types of entity/chunk annotations")
    argparser.add_argument("--chunk_annset_name", type=str,
                           help="If specified, a different annotation set names for getting the chunk annotations")
    argparser.add_argument("--scheme", type=str, choices=["IOB", "BIO", "IOBES", "BILOU", "BMEOW", "BMEWO"],
                           default="BIO",
                           help="Chunk coding scheme to use (BIO)")
    argparser.add_argument("--debug", action="store_true",
                           help="Enable debugging mode/logging")
    return argparser


def parse_args():
    parser = build_argparser()
    args = parser.parse_args()
    return args


def run_docs2dataset():
    args = parse_args()
    if args.debug:
        logger = init_logger(lvl=logging.DEBUG)
    else:
        logger = init_logger()
    outfile = os.path.join(args.outdir, args.outfile)
    src = DirFilesSource(dirpath=args.docdir, recursive=args.recursive, exts=args.exts, fmt=args.fmt)
    dest = Conll2003FileDestination(
        file=outfile,
        annset_name=args.annset_name,
        sentence_type=args.sentence_type,
        token_type=args.token_type,
        token_feature=args.token_feature,
        chunk_annset_name=args.chunk_annset_name,
        chunk_types=args.chunk_types,
        scheme=args.scheme,
    )
    n_errors = 0
    n_read = 0
    for doc in src:
        n_read += 1
        try:
            dest.append(doc)
        except Exception as ex:
            n_errors += 1
            if args.on_error == "exit":
                logger.error(f"Problem writing document {n_read} to the destination", ex)
                raise ex
            elif args.on_error == "log":
                logger.error(f"Problem {n_errors} writing document {n_read} to the destination", ex)
            else:
                pass   # ignore the error
    logger.info(f"Number of documents read: {n_read}")
    logger.info(f"Number of errors: {n_errors}")


if __name__ == "__name__":
    run_docs2dataset()