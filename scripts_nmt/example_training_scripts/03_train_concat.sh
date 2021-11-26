#!/bin/bash

# set variables
SRCLANG=source_language
TGTLANG=target_language

# If using a conda environment
ENV_NAME=environment_name

conda activate $ENV_NAME

EXP_NAME=${SRCLANG}_${TGTLANG}_concat
SAVE_DIR=/path/to/checkpoints/$EXP_NAME
BIN_DATA_PATH=/path/to/binarized/data

mkdir $SAVE_DIR

fairseq-train \
    $BIN_DATA_PATH \
    --arch transformer --max-epoch 60 \
    --optimizer adam --adam-betas '(0.9, 0.98)' --clip-norm 0.0 \
    --lr 5e-4 --lr-scheduler inverse_sqrt --warmup-updates 4000 \
    --dropout 0.3 --weight-decay 0.0 \
    --criterion label_smoothed_cross_entropy --label-smoothing 0.1 \
    --eval-bleu --eval-bleu-remove-bpe=sentencepiece \
    --max-tokens 15000 \
    --log-format json \
    --save-dir $SAVE_DIR \
    --tensorboard-logdir $SAVE_DIR/log-tb \
    2>&1 | tee $SAVE_DIR/log.out
