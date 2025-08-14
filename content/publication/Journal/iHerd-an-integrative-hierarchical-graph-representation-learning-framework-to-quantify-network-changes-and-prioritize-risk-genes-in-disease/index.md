---
title: "iHerd: an integrative hierarchical graph representation learning framework to quantify network changes and prioritize risk genes in disease"
publication_types:
  - "2"
authors:
  - "**Ziheng Duan**"
  - Yi Dai
  - Ahyeon Hwang
  - Cheyu Lee
  - Kaichi Xie
  - Chutong Xiao
  - Min Xu
  - Matthew J. Girgenti
  - Jing Zhang 
doi: https://doi.org/10.1371/journal.pcbi.1011444
publication: Plos Computational Biology
abstract: Different genes form complex networks within cells to carry out critical cellular functions, while network alterations in this process can potentially introduce downstream transcriptome perturbations and phenotypic variations. Therefore, developing efficient and interpretable methods to quantify network changes and pinpoint driver genes across conditions is crucial. We propose a hierarchical graph representation learning method, called iHerd. Given a set of networks, iHerd first hierarchically generates a series of coarsened sub-graphs in a data-driven manner, representing network modules at different resolutions (e.g., the level of signaling pathways). Then, it sequentially learns low-dimensional node representations at all hierarchical levels via efficient graph embedding. Lastly, iHerd projects separate gene embeddings onto the same latent space in its graph alignment module to calculate a rewiring index for driver gene prioritization. To demonstrate its effectiveness, we applied iHerd on a tumor-to-normal GRN rewiring analysis and cell-type-specific GCN analysis using single-cell multiome data of the brain. We showed that iHerd can effectively pinpoint novel and well-known risk genes in different diseases. Distinct from existing models, iHerd’s graph coarsening for hierarchical learning allows us to successfully classify network driver genes into early and late divergent genes (EDGs and LDGs), emphasizing genes with extensive network changes across and within signaling pathway levels. This unique approach for driver gene classification can provide us with deeper molecular insights. The code is freely available at https://github.com/aicb-ZhangLabs/iHerd. All other relevant data are within the manuscript and supporting information files.
draft: false
url_pdf: publication/Journal/iHerd-an-integrative-hierarchical-graph-representation-learning-framework-to-quantify-network-changes-and-prioritize-risk-genes-in-disease/journal.pcbi.1011444.pdf
featured: false
image:
  filename: featured
  focal_point: Smart
  preview_only: false
date: 2023-09-11
url_code: "https://github.com/aicb-ZhangLabs/iHerd"
# tags:
#   - Highlight
---
