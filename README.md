# Repo for Multimodal-Multi-scale-Framework-for-Ethical-AI-Model-Development grant


## Model 1: MOSCARD (MICCAI 2025)
Our study addresses bias in multimodal medical imaging by integrating causal reasoning techniques. We utilize chest X-ray (CXR) images as the primary source of information and employ electrocardiogram (ECG) signals as a complementary guiding modality. To effectively preserve and leverage the essential features from CXR images while incorporating insights from ECG data, we have adapted a [co-attention mechanism](https://github.com/mahmoodlab/MCAT/tree/master?tab=readme-ov-file) originally developed for processing H&E stained whole slide images alongside genomic factors. For single modality training, we employ a Vision Transformer (ViT) architecture, specifically utilizing the [MedCLIP](https://github.com/RyanWangZf/MedCLIP) image modality, to serve as a unified encoder for both ECG signals and CXR images during the encoder training phase. This integration allows for a cohesive and comprehensive analysis of the multimodal medical data.

## Model 2: VLM Mammogram+text (MICCAI 2024)
We develop a multimodal framework to automatize the relevant case-selection based on both text and image representation of the individual screening exams. We validate the efficacy of our proposed approach across two distinct VLMs: the in-domain VLM (MedCLIP) and out-of-domain VLM (ALBEF). Our evaluation spans zero-shot, few-shot, and supervised scenarios using UW Madison datasets containing mammograms and their corresponding reports. The model was also externally validated on screening mammogram data from Mayo Clinic.

## Model 3. Multimodal spatiotemporal graph neural networks for improved prediction ( IEEE Journal of Biomedical and Health Informatics, 2023)
While deep-learning-based studies have shown promising empirical results, several limitations exist in prior models for hospital readmission prediction, such as: (a) only patients with certain conditions are considered, (b) do not leverage data temporality, (c) individual admissions are assumed independent of each other, which ignores patient similarity, (d) limited to single modality or single center data. In this study, we propose a multimodal, spatiotemporal graph neural network (MM-STGNN) for prediction of 30-day all-cause hospital readmission, which fuses in-patient multimodal, longitudinal data and models patient similarity using a graph. Using longitudinal chest radiographs and electronic health records from two independent centers, we show that MM-STGNN achieved an area under the receiver operating characteristic curve (AUROC) of 0.79 on both datasets.

## Model 4. NLP Model Toolkits for clinical notes parsing (breast cancer) - 
### Patient-Centered Outcome extraction (JCO informatics) – We designed a fine-tuning framework for Large language models (LLM) to extract treatment-related side effects after breast cancer therapy from multiple types of clinical notes. We compared the performance of light-weight (GPT-2), middle-weight (BioGPT), and heavy-weight (LLaMA) LLMs for the same extraction task on the in-domain and out-of-domain test sets. We released our extraction code with the academic open-source license in GitHub and packaged the execution code in Docker.

### Treatment extraction  (JCO informatics) – We developed a hybrid information extraction framework by combining Unified Medical Language System (UMLS) parser and a fine-tuned LLM to extract longitudinal treatment timelines from time-stamped clinical notes - specifically designed for breast cancer. Our framework not only determines whether a patient is receiving a specific therapy, but also constructs a longitudinal treatment timeline of the patient based on time-stamped clinical notes. We released our extraction code with the academic open-source license in GitHub and packaged the execution code in Docker.

### Recurrence extraction and site detection  (JCO informatics) – We developed a fully automated framework for extracting recurrence timeline and sites. We used an innovative framework, weak supervision strategy for smaller-sized LLMs, incorporating entropy optimization to fine-tune the model for domain-specific language while addressing data imbalance for breast recurrence. We released our extraction code with the academic open-source license in GitHub and packaged the execution code in Docker.


All the models are validated on multi-institutional data (Mayo, Stanford, Emory and UC Davis).



