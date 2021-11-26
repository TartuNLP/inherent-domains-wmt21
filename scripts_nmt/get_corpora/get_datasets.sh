#!/bin/bash

SRCLANG=en # set source language
TGTLANG=et # set target language
SEED=X # set random seed

mkdir corpora
DATA_PATH=corpora

for corpus in Europarl OpenSubtitles JRC-Acquis EMEA
do
 # Download $DATA_PATH from OPUS
 python opustools_to_documents.py --corpus $corpus \
                                  --src $SRCLANG --tgt $TGTLANG \
                                  --filename $DATA_PATH/$corpus.$SRCLANG-$TGTLANG.docs \
                                  --minsent 5
 
 # Basic cleaning
 python cleaning_docs.py --input $DATA_PATH/$corpus.$SRCLANG-$TGTLANG.docs \
                         --output $DATA_PATH/cl-$corpus.$SRCLANG-$TGTLANG.docs
 
 # Separate into test, dev and train in a fair way:
 # whole documents are written into sets,
 # the clean test and dev will not contain sentence pairs
 # that have exact matches in other sets
 python separate_test_dev_train.py --input $DATA_PATH/cl-$corpus.$SRCLANG-$TGTLANG.docs \
                                   --test_size 3000 --dev_size 3000 --train_size 500000 \
                                   --random_seed $SEED

done

# Download ParaCrawl
wget -P $DATA_PATH https://s3.amazonaws.com/web-language-models/paracrawl/release7.1/$SRCLANG-$TGTLANG.tmx.gz
gunzip $DATA_PATH/$SRCLANG-$TGTLANG.tmx.gz

# Parse TMX into URLs + plain text
python parse_paracrawl_tmx.py --ddir $DATA_PATH --input $SRCLANG-$TGTLANG.tmx \
                              --output doc-indices-ParaCrawl.$SRCLANG-$TGTLANG.txt \
                              --logfreq 100000 --srcl $SRCLANG --tgtl $TGTLANG

# Sort by URL
sort -s -k 1,1 -t$'\t' $DATA_PATH/doc-indices-ParaCrawl.$SRCLANG-$TGTLANG.txt > $DATA_PATH/sorted-doc-indices-ParaCrawl.$SRCLANG-$TGTLANG.txt

# Separate into test, dev and train
python separate_test_dev_train_paracrawl.py --input $DATA_PATH/sorted-doc-indices-ParaCrawl.$SRCLANG-$TGTLANG.txt \
                                            --test_size 3000 --dev_size 3000 --train_size 3000000 --random_seed $SEED
