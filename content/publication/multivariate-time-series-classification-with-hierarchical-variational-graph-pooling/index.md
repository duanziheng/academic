---
title: Multivariate Time Series Classification with Hierarchical Variational
  Graph Pooling
publication_types:
  - "2"
authors:
  - Ziheng Duan
  - Haoyan Xu
  - Yueyang Wang
  - Yida Huang
  - Anni Ren
  - Yizhou Sun
  - Wei Wang
doi: https://doi.org/10.1016/j.neunet.2022.07.032 
publication: Neural Networks
abstract: Over the past decade, multivariate time series classification (MTSC) has received great attention with the advance of sensing techniques. Current deep learning methods for MTSC are based on convolutional and recurrent neural network, with the assumption that time series variables have the same effect to each other. Thus they cannot model the pairwise dependencies among variables explicitly. What's more, current spatial-temporal modeling methods based on GNNs are inherently flat and lack the capability of aggregating node information in a hierarchical manner. To address this limitation and attain expressive global representation of MTS, we propose a graph pooling based framework MTPool and view MTSC task as graph classification task. With graph structure learning and temporal convolution, MTS slices are converted to graphs and spatial-temporal features are extracted. Then, we propose a novel graph pooling method, which uses an encoder-decoder mechanism to generate adaptive centroids for cluster assignments. GNNs and graph pooling layers are used for joint graph representation learning and graph coarsening. With multiple graph pooling layers, the input graphs are hierachically coarsened to one node. Finally, differentiable classifier takes this coarsened one-node graph as input to get the final predicted class. Experiments on 10 benchmark datasets demonstrate MTPool outperforms state-of-the-art methods in MTSC tasks.
draft: false
url_pdf: publication/multivariate-time-series-classification-with-hierarchical-variational-graph-pooling/1-s2.0-S0893608022002970-main.pdf
featured: false
image:
  filename: featured
  focal_point: Smart
  preview_only: false
date: 2022-08-02
---
