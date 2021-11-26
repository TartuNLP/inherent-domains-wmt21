#!/bin/bash

# set variables
SRCLANG=source_language
TGTLANG=target_language

# If using a conda environment
ENV_NAME=environment_name

conda activate $ENV_NAME

DATA_PATH=/path/to/test/data/
BIN_DATA_PATH=/path/to/binarized/data/
RESULTS_PATH=/path/to/translations/
SCRIPTS_PATH=/path/to/scripts/
SP_MODEL=path/to/sentencepiece/model
set=test-cl

EXP_NAME=experiment_name
SAVE_DIR=${SRCLANG}_${TGTLANG}_${EXP_NAME}

for corpus in Europarl OpenSubtitles JRC-Acquis EMEA
do
  # translate
  cat $DATA_PATH/$corpus.$set.$SRCLANG \
    | fairseq-interactive $BIN_DATA_PATH \
      --source-lang $SRCLANG --target-lang $TGTLANG \
      --path $SAVE_DIR/checkpoint_best_dev_bleu.pt \
      --buffer-size 2000 --batch-size 32 --beam 5 \
    > $RESULTS_PATH/transl_${SRCLANG}_${TGTLANG}_${EXP_NAME}_${corpus}.sys
	
  # grep translations from the output file
  grep "^H" $RESULTS_PATH/transl_${SRCLANG}_${TGTLANG}_${EXP_NAME}_${corpus}.sys | cut -f3 > $RESULTS_PATH/hyp_${SRCLANG}_${TGTLANG}_${EXP_NAME}_${corpus}.txt
  
  # de-sentencepiece
  python3 $SCRIPTS_PATH/apply_sentencepiece.py --corpora $RESULTS_PATH/hyp_${SRCLANG}_${TGTLANG}_${EXP_NAME}_${corpus}.txt --model $SP_MODEL --action restore
  
  # calculate bleu w/sacrebleu

  translation=preprocessed_translation
  reference=reference_translation

  echo $EXP_NAME
  echo $corpus
  cat $translation | sacrebleu $reference
done
