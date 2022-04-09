# Translation Transformers Rediscover Inherent Data Domains

This repository is the outdated official implementation of [Translation Transformers Rediscover Inherent Data Domains](https://aclanthology.org/2021.wmt-1.65.pdf). 

Instead, see [this code repo](https://github.com/TartuNLP/inherent-domains-wmt21) for paper notebooks and NMT training scipts and [this repo](https://github.com/maksym-del/domain_clusters) for updated clustering pipeline.

NMT training and data scripts are in the ```scripts_nmt``` folder.

Analysis results were generated with the code in the ```notebooks``` folder.



Cite:
```
@inproceedings{del-etal-2021-translation,
    title = "Translation Transformers Rediscover Inherent Data Domains",
    author = "Del, Maksym  and
      Korotkova, Elizaveta  and
      Fishel, Mark",
    booktitle = "Proceedings of the Sixth Conference on Machine Translation",
    month = nov,
    year = "2021",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.wmt-1.65",
    pages = "599--613",
    abstract = "Many works proposed methods to improve the performance of Neural Machine Translation (NMT) models in a domain/multi-domain adaptation scenario. However, an understanding of how NMT baselines represent text domain information internally is still lacking. Here we analyze the sentence representations learned by NMT Transformers and show that these explicitly include the information on text domains, even after only seeing the input sentences without domains labels. Furthermore, we show that this internal information is enough to cluster sentences by their underlying domains without supervision. We show that NMT models produce clusters better aligned to the actual domains compared to pre-trained language models (LMs). Notably, when computed on document-level, NMT cluster-to-domain correspondence nears 100{\%}. We use these findings together with an approach to NMT domain adaptation using automatically extracted domains. Whereas previous work relied on external LMs for text clustering, we propose re-using the NMT model as a source of unsupervised clusters. We perform an extensive experimental study comparing two approaches across two data scenarios, three language pairs, and both sentence-level and document-level clustering, showing equal or significantly superior performance compared to LMs.",
}
