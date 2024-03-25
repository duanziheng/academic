---
title: "scENCORE: leveraging single-cell epigenetic data to predict chromatin conformation using graph embedding"
publication_types:
  - "2"
authors:
  - Ziheng Duan
  - Siwei Xu
  - Shushrruth Sai Srinivasan
  - Ahyeon Hwang
  - Che Yu Lee
  - Feng Yue
  - Mark Gerstein
  - Yu Luan
  - Matthew Girgenti
  - Jing Zhang
doi: https://doi.org/10.1093/bib/bbae096
publication: Briefings in Bioinformatics
abstract: Dynamic compartmentalization of eukaryotic DNA into active and repressed states enables diverse transcriptional programs to arise from a single genetic blueprint, whereas its dysregulation can be strongly linked to a broad spectrum of diseases. While single-cell Hi-C experiments allow for chromosome conformation profiling across many cells, they are still expensive and not widely available for most labs. Here, we propose an alternate approach, scENCORE, to computationally reconstruct chromatin compartments from the more affordable and widely accessible single-cell epigenetic data. First, scENCORE constructs a long-range epigenetic correlation graph to mimic chromatin interaction frequencies, where nodes and edges represent genome bins and their correlations. Then, it learns the node embeddings to cluster genome regions into A/B compartments and aligns different graphs to quantify chromatin conformation changes across conditions. Benchmarking using cell-type-matched Hi-C experiments demonstrates that scENCORE can robustly reconstruct A/B compartments in a cell-type-specific manner. Furthermore, our chromatin confirmation switching studies highlight substantial compartment-switching events that may introduce substantial regulatory and transcriptional changes in psychiatric disease. In summary, scENCORE allows accurate and cost-effective A/B compartment reconstruction to delineate higher-order chromatin structure heterogeneity in complex tissues.
draft: false
url_pdf: publication/Journal/scENCORE-leveraging-single-cell-epigenetic-data-to-predict-chromatin-conformation-using-graph-embedding/bbae096.pdf
featured: false
image:
  filename: featured
  focal_point: Smart
  preview_only: false
date: 2024-03-16
url_code: "https://github.com/aicb-ZhangLabs/scENCORE"
---
