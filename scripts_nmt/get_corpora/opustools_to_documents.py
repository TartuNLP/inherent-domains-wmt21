#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from argparse import ArgumentParser
import shutil
import re
import logging
import opustools

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


def opus_read(corpus, src, tgt, keep=False):
    """
    Download corpora from OPUS using the opustools package
    (Moses format, include original filenames)
    """
    logging.info("Downloading files from OPUS")
    dl_dir = f"{corpus}-{src}-{tgt}-dir-temp"
    opus_out_file = f"{corpus}-{src}-{tgt}-opus-aligned"
    os.system(f"""opus_read -d {corpus} -s {src} -t {tgt} -p raw -w {opus_out_file} -wm moses -dl {dl_dir} -pn -ln -q -cm '__@delimeter@__'""")
    if not keep:
        shutil.rmtree(f"{corpus}-{src}-{tgt}-dir-temp")
    return opus_out_file


def convert_to_docs(min_sent, input_filename, output_filename,
                    corpus, src_lang, tgt_lang, keep=False):
    """
    Convert the OPUS file into format
    "file_id\\tsrc_sent\\ttgt_sent",
    where file_id is corpus_srclang_tgtlang_docnumber
    """
    docs_count, lines_count = 0, 0
    with open(input_filename, 'r', encoding='utf8') as in_fh,\
            open(output_filename, 'w', encoding='utf8') as out_fh:
        logging.info("Converting to file_id\tsrc_sent"
                     "\ttgt_sent format")
        current_doc = []
        for line in in_fh.readlines():
            if not line.strip():
                continue
            elif re.fullmatch("^<fromDoc>(.+)</fromDoc>$", line.strip()):
                if len(current_doc) >= min_sent:
                    out_fh.writelines(["{0}_{1}_{2}_{3}\t{4}\n"
                                      .format(corpus, src_lang, tgt_lang,
                                              docs_count, pair)
                                       for pair in current_doc])
                    docs_count += 1
                    lines_count += len(current_doc)
                current_doc = []
                # src_doc = re.fullmatch("^<fromDoc>(.+)</fromDoc>$",
                #                        line.strip()).group(1)
            elif re.fullmatch("^<toDoc>(.+)</toDoc>$", line.strip()):
                continue
                # tgt_doc = re.fullmatch("^<toDoc>(.+)</toDoc>$",
                #                        line.strip()).group(1)
            else:
                current_doc.append(line.strip().replace('\t', ' ').
                                   replace('__@delimeter@__', '\t'))
    if not keep:
        if os.path.exists(input_filename):
            os.remove(input_filename)
    logging.info("Wrote {0} docs, {1} lines into {2}".format(docs_count,
                                                             lines_count,
                                                             output_filename))


def main(args):
    opus_file = opus_read(args.corpus, args.src, args.tgt, args.keepfiles)
    convert_to_docs(args.minsent, opus_file, args.filename,
                    args.corpus, args.src, args.tgt, args.keepfiles)


if __name__ == '__main__':
    parser = ArgumentParser(description="""Download OPUS corpus and
    write it in Moses format with document IDs""")
    parser.add_argument("--corpus", required=True, type=str,
                        help="Corpus name")
    parser.add_argument("--src", required=True, type=str,
                        help="Source lang")
    parser.add_argument("--tgt", required=True, type=str,
                        help="Target lang")
    parser.add_argument("--filename", type=str, default='corpus',
                        help="Filename to save the result into")
    parser.add_argument("--minsent", type=int, default=1,
                        help="Minimum number of sentence pairs in document")
    parser.add_argument("--keepfiles", action='store_true',
                        default=False, help="""Keep the raw and aligned files
                                               downloaded from OPUS""")

    arguments = parser.parse_args()

    main(arguments)
