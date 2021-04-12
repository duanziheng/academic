---
title: Multivariate Time Series Classification with Hierarchical Variational
  Graph Pooling
publication_types:
  - "3"
authors:
  - Haoyan Xu
  - Ziheng Duan
  - Yunsheng Bai
  - Yida Huang
  - Anni Ren
  - Qianru Yu
  - Qianru Zhang
  - Yueyang Wang
  - Xiaoqian Wang
  - Yizhou Sun
  - Wei Wang
author_notes:
  - Equal Contribution
  - Equal Contribution
abstract: Over the past decade, multivariate time series classification (MTSC) has received great attention with the advance of sensing techniques. Current deep learning methods for MTSC are based on convolutional and recurrent neural network, with the assumption that time series variables have the same effect to each other. Thus they cannot model the pairwise dependencies among variables explicitly. What's more, current spatial-temporal modeling methods based on GNNs are inherently flat and lack the capability of aggregating node information in a hierarchical manner. To address this limitation and attain expressive global representation of MTS, we propose a graph pooling based framework MTPool and view MTSC task as graph classification task. With graph structure learning and temporal convolution, MTS slices are converted to graphs and spatial-temporal features are extracted. Then, we propose a novel graph pooling method, which uses an encoder-decoder mechanism to generate adaptive centroids for cluster assignments. GNNs and graph pooling layers are used for joint graph representation learning and graph coarsening. With multiple graph pooling layers, the input graphs are hierachically coarsened to one node. Finally, differentiable classifier takes this coarsened one-node graph as input to get the final predicted class. Experiments on 10 benchmark datasets demonstrate MTPool outperforms state-of-the-art methods in MTSC tasks.
draft: false
url_pdf: publication/multivariate-time-series-classification-with-hierarchical-variational-graph-pooling/2010.05649.pdf
featured: false
image:
  filename: featured
  focal_point: Smart
  preview_only: false
date: 2020-10-12T15:47:06.259Z
---
