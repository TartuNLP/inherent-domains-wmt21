#!/bin/bash

# set variables
SRCLANG=source_language
TGTLANG=target_language
DATAPATH=/path/to/data
MODELSPATH=/path/to/preprocessing/model
SCRIPTSPATH=/path/to/scripts

CORPUS_NAME=corpus_name

# If using a conda environment
ENV_NAME=environment_name

conda activate $ENV_NAME

# Train SentencePiece
# Script apply_sentencepiece.py is included in this repo as well
python $SCRIPTSPATH/apply_sentencepiece.py --size 32000 \
                                           --corpora $DATAPATH/$CORPUS_FILENAME* \
                                           --model $MODELSPATH/sp-$SRCLANG-$TGTLANG \
                                           --action train

# Apply SentencePiece model
python3 $SCRIPTSPATH/apply_sentencepiece.py --corpora $DATAPATH/$CORPUS_NAME*$SRCLANG --model $MODELSPATH/sp-$SRCLANG-$TGTLANG --action split
python3 $SCRIPTSPATH/apply_sentencepiece.py --corpora $DATAPATH/$CORPUS_NAME*$TGTLANG --model $MODELSPATH/sp-$SRCLANG-$TGTLANG --action split
