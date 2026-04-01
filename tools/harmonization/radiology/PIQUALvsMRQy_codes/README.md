The repository contains five core scripts and notebooks, each corresponding to one of the experimental stages:

**Unsupervised_Clustering.ipynb** implements Experiment 1. This notebook extracts quantitative MRQy metrics from T2-weighted and ADC sequences, applies dimensionality reduction using UMAP, and performs k-means clustering to identify site-specific patterns. The outputs include cluster assignments and visualizations of the clustering results.

**3dVnet.py** supports Experiment 2 (baseline segmentation). It trains a baseline V-Net deep learning model for prostate gland segmentation using scans classified as high-quality according to PI-QUAL.

**3dVnet_multiclusters.py** extends Experiment 2 (cluster effects). This script evaluates the impact of MRQy-defined clusters by training the V-Net model with cluster-specific data and balanced multi-cluster subsets, thereby testing model generalizability across acquisition sites.

**Registration_train_with_dataaugment.py** is used in Experiment 3 (training phase). It trains a deformable image registration framework with pre-alignment (rigid and affine) and data augmentation, using T2-weighted images as fixed references and ADC maps as moving images.

**apply_voxelmorph.py** completes Experiment 3 (inference). It applies the trained VoxelMorph registration model to unseen T2w/ADC pairs and evaluates performance metrics such as Dice similarity coefficient (DSC) and target registration error (TRE).
