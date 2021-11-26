#!/bin/bash

# set variables
SRCLANG=source_language
TGTLANG=target_language
DATAPATH=/path/to/data

CORPUS_NAME=corpus_name

# If using a conda environment
ENV_NAME=environment_name

conda activate $ENV_NAME

# Paste source and target data into one file to shuffle them in parallel
# Shuffle, then cut source and target back into separate files

for set in train dev test
do
 paste $DATAPATH/$CORPUS_NAME.$set.$SRCLANG $DATAPATH/$CORPUS_NAME.$set.$TGTLANG | shuf > $DATAPATH/shuf-$CORPUS_NAME.$set.both
 cut -f1 $DATAPATH/shuf-$CORPUS_NAME.$set.both > $DATAPATH/shuf-$CORPUS_NAME.$set.$SRCLANG
 cut -f2 $DATAPATH/shuf-$CORPUS_NAME.$set.both > $DATAPATH/shuf-$CORPUS_NAME.$set.$TGTLANG
done

# Copy data into $DATAPATH/fairseq-data-$SRCLANG-$TGTLANG-$CORPUS_NAME with filenames like train.$SRCLANG, valid.$TGTLANG, etc.

mkdir -p $DATAPATH/fairseq-data-$SRCLANG-$TGTLANG-$CORPUS_NAME
mkdir -p $DATAPATH/bin-data-$SRCLANG-$TGTLANG-$CORPUS_NAME

for lang in $SRCLANG $TGTLANG
do
 cp $DATAPATH/shuf-$CORPUS_NAME.train.$lang $DATAPATH/fairseq-data-$SRCLANG-$TGTLANG-$CORPUS_NAME/train.$lang
 cp $DATAPATH/shuf-$CORPUS_NAME.dev.$lang $DATAPATH/fairseq-data-$SRCLANG-$TGTLANG-$CORPUS_NAME/valid.$lang
 cp $DATAPATH/shuf-$CORPUS_NAME.test.$lang $DATAPATH/fairseq-data-$SRCLANG-$TGTLANG-$CORPUS_NAME/test.$lang
done

# Finally, binarize for fairseq
# If fine-tuning, do not forget to use the original dictionary (set parameter --srcdict)

fairseq-preprocess --source-lang $SRCLANG --target-lang $TGTLANG \
    --trainpref $DATAPATH/fairseq-data-$SRCLANG-$TGTLANG-$CORPUS_NAME/train \
    --validpref $DATAPATH/fairseq-data-$SRCLANG-$TGTLANG-$CORPUS_NAME/valid \
    --testpref $$DATAPATH/fairseq-data-$SRCLANG-$TGTLANG-$CORPUS_NAME/test \
    --destdir $DATAPATH/bin-data-$SRCLANG-$TGTLANG-$CORPUS_NAME --joined-dictionary
