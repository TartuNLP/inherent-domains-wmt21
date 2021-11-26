#!/bin/bash

# set variables
SRCLANG=source_language
TGTLANG=target_language
CORPUS=corpus_name

# If using a conda environment
ENV_NAME=environment_name

conda activate $ENV_NAME

EXP_NAME=${SRCLANG}_${TGTLANG}_${CORPUS}_ft
SAVE_DIR=/path/to/checkpoints/$EXP_NAME
BIN_DATA_PATH=/path/to/binarized/data

mkdir $SAVE_DIR

fairseq-train \
    $BIN_DATA_PATH \
    --finetune-from-model /path/to/checkpoint/checkpoint60.pt \
    --arch transformer --max-epoch 50 \
    --optimizer adam --adam-betas '(0.9, 0.98)' --clip-norm 0.0 \
    --lr 0.000125 --lr-scheduler reduce_lr_on_plateau --lr-patience 3 --lr-shrink 0.5 \
    --dropout 0.3 --weight-decay 0.0 \
    --criterion label_smoothed_cross_entropy --label-smoothing 0.1 \
    --eval-bleu --eval-bleu-remove-bpe=sentencepiece \
    --max-tokens 15000 \
    --log-format json \
    --save-dir $SAVE_DIR \
    --tensorboard-logdir $SAVE_DIR/log-tb \
    2>&1 | tee $SAVE_DIR/log.out
