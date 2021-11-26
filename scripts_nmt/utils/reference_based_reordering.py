#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from collections import Counter
from argparse import ArgumentParser

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


def match_order(refs, hyps):
    first_ref_lines = list_of_lines_from_file(refs[0])
    first_ref_lines_counter = Counter(first_ref_lines)
    if len(set(first_ref_lines)) != len(first_ref_lines):
        logging.warning("Duplicate lines in reference")
    all_hyp_dict = {}
    for ref_sent in set(first_ref_lines):
        for i in range(first_ref_lines_counter[ref_sent]):
            all_hyp_dict[str(i)+"_"+ref_sent] = {n: None
                                                 for n in range(len(refs))}

    for i in range(len(refs)):
        ref_lines = list_of_lines_from_file(refs[i])
        assert sorted(list(ref_lines)) == sorted(list(first_ref_lines)), \
            "References do not match"
        hyp_lines = list_of_lines_from_file(hyps[i])

        ref_lines_used = {line: 0 for line in set(ref_lines)}
        for n, ref_line in enumerate(ref_lines):
            all_hyp_dict[str(ref_lines_used[ref_line]) + "_" +
                         ref_line][i] = hyp_lines[n]
            ref_lines_used[ref_line] += 1

    return all_hyp_dict, first_ref_lines


def list_of_lines_from_file(filename):
    with open(filename, 'r', encoding='utf8') as fh:
        lines = [line.strip() for line in fh.readlines()]
    return lines


def write_output(all_hyp_dict, first_ref_lines, hyp_names, ref_name, out_path):
    first_ref_lines_counter = Counter(first_ref_lines)
    with open(os.path.join(out_path, ref_name), 'w', encoding='utf8') as fh:
        fh.writelines([line+'\n' for line in first_ref_lines])
    for i in range(len(hyp_names)):
        ref_lines_used = {line: 0 for line in set(first_ref_lines)}
        with open(os.path.join(out_path, hyp_names[i]), 'w',
                  encoding='utf8') as fh:
            for line in first_ref_lines:
                fh.write(all_hyp_dict[str(ref_lines_used[line]) + "_" +
                                      line][i]+'\n')
                ref_lines_used[line] += 1
            assert dict(first_ref_lines_counter) == ref_lines_used, \
                "Reference counter does not match the written lines"


if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("--refs", required=True, nargs="+",
                        help="Reordered reference files")
    parser.add_argument("--hyps", required=True, nargs="+",
                        help="Reordered hypothesis files")
    parser.add_argument("--hyp-names", required=True, nargs="+",
                        help="Filenames under which the reordered hypotheses"
                             "will be saved")
    parser.add_argument("--ref-name", default="reference",
                        help="Filenames under which common reference "
                             "will be saved")
    parser.add_argument("--output-path", default="./",
                        help="Path to output files")

    args = parser.parse_args()

    assert (len(args.refs) == len(args.hyps) == len(args.hyp_names)), \
        "Number of hypotheses, references and output filenames does not match"

    all_hyps_dict, first_ref = match_order(refs=args.refs, hyps=args.hyps)
    write_output(all_hyp_dict=all_hyps_dict, first_ref_lines=first_ref,
                 hyp_names=args.hyp_names, ref_name=args.ref_name,
                 out_path=args.output_path)
