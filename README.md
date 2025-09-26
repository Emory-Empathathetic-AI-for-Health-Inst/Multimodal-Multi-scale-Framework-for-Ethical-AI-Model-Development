# Repo for Multimodal-Multi-scale-Framework-for-Ethical-AI-Model-Development grant


## Model 1: MOSCARD (MICCAI 2025)
Our study addresses bias in multimodal medical imaging by integrating causal reasoning techniques. We utilize chest X-ray (CXR) images as the primary source of information and employ electrocardiogram (ECG) signals as a complementary guiding modality. To effectively preserve and leverage the essential features from CXR images while incorporating insights from ECG data, we have adapted a [co-attention mechanism](https://github.com/mahmoodlab/MCAT/tree/master?tab=readme-ov-file) originally developed for processing H&E stained whole slide images alongside genomic factors. For single modality training, we employ a Vision Transformer (ViT) architecture, specifically utilizing the [MedCLIP](https://github.com/RyanWangZf/MedCLIP) image modality, to serve as a unified encoder for both ECG signals and CXR images during the encoder training phase. This integration allows for a cohesive and comprehensive analysis of the multimodal medical data.

