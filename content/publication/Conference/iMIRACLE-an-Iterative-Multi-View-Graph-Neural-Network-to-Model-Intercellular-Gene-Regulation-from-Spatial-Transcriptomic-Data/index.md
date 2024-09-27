---
abstract: Spatial transcriptomics has transformed genomic research by measuring spatially resolved gene expressions, allowing us to investigate how cells adapt to their microenvironment via modulating their expressed genes. This essential process usually starts from cell-cell communication (CCC) via ligand-receptor (LR) interaction, leading to regulatory changes within the receiver cell. However, few methods were developed to connect them to provide biological insights into intercellular regulation. To fill this gap, we propose iMiracle, an iterative multi-view graph neural network that models each cell’s intercellular regulation with three key features. Firstly, iMiracle integrates inter- and intra-cellular networks to jointly estimate cell-type- and micro-environment-driven gene expressions. Optionally, it allows prior knowledge of intra-cellular networks as pre-structured masks to maintain biological relevance. Secondly, iMiracle employs iterative learning to overcome the sparsity of spatial transcriptomic data and gradually fill in the missing edges in the CCC network. Thirdly, iMiracle infers a cell-specific ligand-gene regulatory score based on the contributions of different LR pairs to interpret inter-cellular regulation. We applied iMiracle to nine simulated and eight real datasets from three sequencing platforms and demonstrated that iMiracle consistently outperformed ten methods in gene expression imputation and four methods in regulatory score inference. Lastly, we developed iMiracle as an open-source software and anticipate that it can be a powerful tool in decoding the complexities of inter-cellular transcriptional regulation.
slides: ""
url_pdf: "publication/Conference/iMIRACLE-an-Iterative-Multi-View-Graph-Neural-Network-to-Model-Intercellular-Gene-Regulation-from-Spatial-Transcriptomic-Data/iMiracle.pdf"
publication_types:
  - "1"
authors:
  - "**Ziheng Duan**"
  - Siwei Xu
  - Cheyu Lee
  - Dylan Riffle
  - Jing Zhang
author_notes: []
publication: CIKM-2024
summary: ""
url_dataset: ""
url_project: ""
publication_short: ""
url_source: ""
url_video: ""
title: "iMIRACLE: an Iterative Multi-View Graph Neural Network to Model Intercellular Gene Regulation from Spatial Transcriptomic Data"
doi: https://doi.org/10.1145/3627673.3679574
featured: false
tags:
  - Highlight
projects: []
image:
  caption: ""
  focal_point: ""
  preview_only: false
date: 2024-10-21T16:00:00.000Z
url_slides: ""
publishDate: 2017-01-01T00:00:00.000Z
url_poster: ""
url_code: "https://github.com/aicb-ZhangLabs/iMiracle"
---