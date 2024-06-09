---
title: "Impeller: a path-based heterogeneous graph learning method for spatial transcriptomic data imputation"
publication_types:
  - "2"
authors:
  - "**Ziheng Duan**"
  - Dylan Riffle
  - Ren Li
  - Junhao Liu
  - Martin Renqiang Min
  - Jing Zhang
doi: https://doi.org/10.1093/bioinformatics/btae339
publication: Bioinformatics
abstract: Recent advances in spatial transcriptomics allow spatially resolved gene expression measurements with cellular or even sub-cellular resolution, directly characterizing the complex spatiotemporal gene expression landscape and cell-to-cell interactions in their native microenvironments. Due to technology limitations, most spatial transcriptomic technologies still yield incomplete expression measurements with excessive missing values. Therefore, gene imputation is critical to filling in missing data, enhancing resolution, and improving overall interpretability. However, existing methods either require additional matched single-cell RNA-seq data, which is rarely available, or ignore spatial proximity or expression similarity information. To address these issues, we introduce Impeller, a path-based heterogeneous graph learning method for spatial transcriptomic data imputation. Impeller has two unique characteristics distinct from existing approaches. First, it builds a heterogeneous graph with two types of edges representing spatial proximity and expression similarity. Therefore, Impeller can simultaneously model smooth gene expression changes across spatial dimensions and capture similar gene expression signatures of faraway cells from the same type. Moreover, Impeller incorporates both short- and long-range cell-to-cell interactions (e.g., via paracrine and endocrine) by stacking multiple GNN layers. We use a learnable path operator in Impeller to avoid the over-smoothing issue of the traditional Laplacian matrices. Extensive experiments on diverse datasets from three popular platforms and two species demonstrate the superiority of Impeller over various state-of-the-art imputation methods.

draft: false
url_pdf: publication/Journal/Impeller-a-path-based-heterogeneous-graph-learning-method-for-spatial-transcriptomic-data-imputation/btae339.pdf
featured: false
image:
  filename: featured
  focal_point: Smart
  preview_only: false
date: 2024-05-28
url_code: "https://github.com/aicb-ZhangLabs/Impeller"
tags:
  - Highlight
---
