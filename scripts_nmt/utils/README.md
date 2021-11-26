`copy_best_dev_bleu_checkpoint.py`: for fine-tuned models, choosing the checkpoint with the highest BLEU score on the development set

`extract_loss_ppl.py`: save training metrics into a JSON file

`separate_clusters.py`: separate data into clusters based on an external file, where each line corresponds to a line of the parallel data and contains the ID of the cluster which the line belongs to

`reference_based_reordering.py`: reordering for significance testing
