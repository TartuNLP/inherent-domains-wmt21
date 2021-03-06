#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import logging
from bisect import bisect_left
from argparse import ArgumentParser

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


def count_lines_and_docs(input_file):
    """
    Count how many lines and documents the file contains
    """
    with open(input_file, 'r', encoding='utf8') as fh:
        line_count = 0
        for line in fh:
            line_count += 1
        # Number of docs is the doc ID of the last line + 1
        n_docs = int(line.split('\t')[0].split('_')[-1]) + 1
        n_lines = line_count
    return n_lines, n_docs


def shuffle_indices(n_docs, seed):
    """
    Shuffle document indices w/given seed
    """
    logging.info('Shuffling documents')
    np.random.seed(seed)
    indices = np.arange(n_docs)
    np.random.shuffle(indices)
    return indices


def find_doc_spans(input_file):
    """
    Find the start and end position of each doc in the original file
    """
    # logging.info('Finding document spans')
    doc_spans = {}
    with open(input_file, 'r', encoding='utf8') as fh:
        doc_num = None
        for i, line in enumerate(fh):
            line_doc_num = int(line.split('\t')[0].split('_')[-1])
            # If doc id in line is different than the current doc id,
            # then this line starts a new doc
            if line_doc_num != doc_num:
                doc_spans[line_doc_num] = [None, None]
                current_doc_start = i
                if i > 0:
                    # The previous line ends the previous doc
                    prev_doc_end = i
                    doc_spans[line_doc_num - 1][1] = prev_doc_end
                # Save start of current doc
                doc_spans[line_doc_num][0] = current_doc_start
                doc_num = line_doc_num
        # Save end of the last doc
        doc_spans[line_doc_num][1] = i + 1
    return doc_spans


def reorder(input_file, shuf_indices, doc_spans):
    """
    Write documents in shuffled order into file input_file+'-reord'
    """
    # logging.info('Reordering documents')
    with open(input_file, 'r', encoding='utf8') as fh:
        inp_lines = [line for line in fh.readlines()]
    with open(input_file + '-reord', 'w', encoding='utf8') as reord_fh:
        written_docs = 0
        for ind in shuf_indices:
            written_docs += 1
            reord_fh.writelines(inp_lines[doc_spans[ind][0]:
                                          doc_spans[ind][1]])
    return input_file + '-reord'


def write_test_dev_train(reord_file, input_file, doc_spans,
                         test_size=3000, dev_size=3000, train_size=1000000):
    """
    From a file with shuffled docs, first write whole documents into test
    until total number of test lines that are not also present in dev or train
    exceeds test_size, then repeat the same for dev, the rest
    of the lines are written into train until train_size is exceeded
    """

    # Read in all lines to check for overlapping later
    with open(reord_file, 'r', encoding='utf8') as reord_fh:
        all_lines = [line for line in reord_fh.readlines()]

    logging.info('Separating test, dev and train')
    # Keep count of clean test, dev and train lines
    n_test_lines, n_dev_lines, n_train_lines = 0, 0, 0
    # Keep count of full test and dev lines and of documents (for logging)
    n_full_test_lines, n_full_dev_lines = 0, 0
    docs_count, n_test_docs, n_dev_docs, n_train_docs = 0, 0, 0, 0

    # Open reordered docs file for reading and all output files for writing
    with open(reord_file, 'r', encoding='utf8') as reord_fh, \
            open(input_file + '.test', 'w', encoding='utf8') as test_fh, \
            open(input_file + '.dev', 'w', encoding='utf8') as dev_fh, \
            open(input_file + '.train', 'w', encoding='utf8') as train_fh, \
            open(input_file + '.dev-cl', 'w', encoding='utf8') as cl_dev_fh, \
            open(input_file + '.test-cl', 'w', encoding='utf8') as cl_test_fh:
        for doc in range(len(doc_spans)):
            docs_count += 1
            if docs_count % 1000 == 0:
                logging.info('Processed {} documents'.format(docs_count))
            full_doc_lines = []
            line = reord_fh.readline()
            current_doc_id = int(line.split('\t')[0].
                                 split('_')[-1])
            current_doc_span = doc_spans[current_doc_id]
            current_doc_len = current_doc_span[1] - current_doc_span[0]

            # If the clean test set is not yet large enough,
            # the current document goes into the test set
            if n_test_lines < test_size:
                n_test_docs += 1
                test_fh.write(line)
                full_doc_lines.append(line)
                for i in range(current_doc_len - 1):
                    line = reord_fh.readline()
                    test_fh.write(line)
                    full_doc_lines.append(line)
                # Compare document content with all lines that come after
                # the current document, so that the clean test set does not
                # contain any lines that are also in dev or train
                del all_lines[:current_doc_len]
                clean_doc_lines = remove_overlapping_lines(full_doc_lines,
                                                           all_lines)
                n_full_test_lines += len(full_doc_lines)
                n_test_lines += len(clean_doc_lines)
                cl_test_fh.writelines(clean_doc_lines)

            # If the clean test set is already filled, but the clean
            # dev set is not, the current document goes into the dev set
            elif n_dev_lines < dev_size:
                n_dev_docs += 1
                dev_fh.write(line)
                full_doc_lines.append(line)
                for i in range(current_doc_len - 1):
                    line = reord_fh.readline()
                    dev_fh.write(line)
                    full_doc_lines.append(line)
                # Compare document content with all lines that come after
                # the current document, so that the clean dev set does not
                # contain any lines that are also in train
                del all_lines[:current_doc_len]
                clean_doc_lines = remove_overlapping_lines(full_doc_lines,
                                                           all_lines)
                n_full_dev_lines += len(full_doc_lines)
                n_dev_lines += len(clean_doc_lines)
                cl_dev_fh.writelines(clean_doc_lines)

            # After clean test and dev are filled, fill train
            elif n_train_lines < train_size:
                n_train_docs += 1
                train_fh.write(line)
                full_doc_lines.append(line)
                n_train_lines += 1
                for i in range(current_doc_len - 1):
                    train_fh.write(reord_fh.readline())
                    full_doc_lines.append(line)
                    n_train_lines += 1

    # Log test, dev and train statistics
    logging.info('Test set: {0} clean lines, {1} full lines, {2} documents'.
                 format(n_test_lines, n_full_test_lines, n_test_docs))
    logging.info('Dev set: {0} clean lines, {1} full lines, {2} documents'.
                 format(n_dev_lines, n_full_dev_lines, n_dev_docs))
    logging.info('Train set: {0} lines, {1} documents'.
                 format(n_train_lines, n_train_docs))

    return (input_file+'.test', input_file+'.test-cl',
            input_file+'.dev', input_file+'.dev-cl',
            input_file+'.train')


def item_in_list(items, key):
    """
    Modified from https://stackoverflow.com/a/56537451
    Find if the element key is present in the list items using binary search;
    items MUST be sorted
    """
    idx = bisect_left(items, key)
    try:
        if items[idx] != key:
            return False
    except IndexError:
        return False
    return True


def remove_overlapping_lines(test_lines, train_lines):
    """
    Return test without the lines that are also in train
    (the first column is the doc id and is not taken into account)
    """
    train_lines = sorted([line.split('\t', 1)[1]
                          for line in train_lines])
    clean_test_lines = []
    for line in test_lines:
        if not item_in_list(train_lines, line.split('\t', 1)[1]):
            clean_test_lines.append(line)
    return clean_test_lines


if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("--input", help="Input filename, format "
                                        "doc_id\\tsrc\\ttgt")
    parser.add_argument("--test_size", help="Min size of test set",
                        type=int, default=3000)
    parser.add_argument("--dev_size", help="Min size of dev set",
                        type=int, default=3000)
    parser.add_argument("--train_size", help="Approx size of train set",
                        type=int, default=1000000)
    parser.add_argument("--random_seed", help="Seed for shuffling docs",
                        type=int, default=0)
    # parser.add_argument("--output", help="Filename for cleaned data")

    args = parser.parse_args()

    # Separate the file
    logging.info('Input file: {}'.format(args.input))
    num_lines, num_docs = count_lines_and_docs(args.input)
    shuffled_indices = shuffle_indices(num_docs, args.random_seed)
    spans = find_doc_spans(args.input)
    reordered_file = reorder(args.input, shuffled_indices, spans)
    result_files = write_test_dev_train(reordered_file, args.input, spans,
                                        args.test_size, args.dev_size,
                                        args.train_size)
    test_full, test_clean, dev_full, dev_clean, train = result_files
    logging.info('Output files: {}'.format(result_files))

    # Clean up: remove the reordered file
    if os.path.exists(reordered_file):
        os.remove(reordered_file)

    logging.info('Done')
