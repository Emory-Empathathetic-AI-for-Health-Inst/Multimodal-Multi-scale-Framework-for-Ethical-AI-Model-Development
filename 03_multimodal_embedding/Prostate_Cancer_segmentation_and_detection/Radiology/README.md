# 🧠 Prostate MRI Projects

[![Docker](https://img.shields.io/badge/Docker-ready-blue)](https://hub.docker.com/u/zlzbme)
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Publication](https://img.shields.io/badge/DOI-10.1002/mp.18053-blue)](https://aapm.onlinelibrary.wiley.com/doi/10.1002/mp.18053)

This repository hosts a suite of deep learning models for 3D prostate MRI analysis, developed by **Zelin Zhang** in the **Emory Empathetic AI for Health Institute / Madabhushi Lab** at *Emory University*.

The repository provides Dockerized pipelines for reproducible segmentation and downstream biomarker analysis of:

- Prostate zonal anatomy (TZ/PZ)
- Whole prostate gland
- Clinically significant prostate cancer (csPCa)

These models are intended to support reproducible research, collaborative deployment, and translational prostate MRI analysis.

---

# 🧩 Overview

| Model | Purpose | Input Modality | Docker Image | Citation |
|:------|:---------|:---------------|:--------------|:----------|
| **ProZonaNet** | Zonal segmentation (Transitional Zone / Peripheral Zone) | T2w axial MRI | [`zlzbme/zlz_prostate_mri_tzpz_seg`](https://hub.docker.com/r/zlzbme/zlz_prostate_mri_tzpz_seg) | *Zhang et al.*, *Medical Physics*, 2025 ([DOI: 10.1002/mp.18053](https://aapm.onlinelibrary.wiley.com/doi/10.1002/mp.18053)) |
| **ProStaNet (Gland)** | Whole-gland segmentation | T2w axial MRI | [`zlzbme/zlz_prostate_mri_gland_seg`](https://hub.docker.com/r/zlzbme/zlz_prostate_mri_gland_seg) | *Zhang et al.*, *Journal of Urology*, 2025 ([DOI: 10.1097/01.JU.0001110136.41716.b7.25](https://www.auajournals.org/doi/abs/10.1097/01.JU.0001110136.41716.b7.25)) |
| **ProStaNet (csPCa)** | Clinically significant prostate cancer segmentation | T2w + ADC (co-registered) MRI | [`zlzbme/zlz_prostate_mri_cspca_seg`](https://hub.docker.com/r/zlzbme/zlz_prostate_mri_cspca_seg) | *Zhang et al.*, *Journal of Urology*, 2025 ([DOI: 10.1097/01.JU.0001110136.41716.b7.25](https://www.auajournals.org/doi/abs/10.1097/01.JU.0001110136.41716.b7.25)) |

---

# 📁 Folder Structure

Organize your input data as follows before running the models.

## For ProZonaNet (TZ/PZ) and ProStaNet (Gland)

```text
/data/
└── mri/
```

- Place all T2-weighted MRI volumes inside `/mri/`.

---

## For ProStaNet (csPCa)

```text
/data/
├── t2w/
└── adc/
```

- Place T2-weighted MRI volumes inside `/t2w/`
- Place ADC volumes inside `/adc/`

> ⚠️ T2W and ADC filenames must be identical between folders (e.g., `case001.nii.gz` in both directories).

---

# 🧪 Model Usage

## 1️⃣ ProZonaNet — Prostate Zonal Segmentation (TZ/PZ)

Performs automatic segmentation of the transitional zone (TZ) and peripheral zone (PZ) from T2-weighted MRI.

### Pull Docker Image

```bash
docker pull zlzbme/zlz_prostate_mri_tzpz_seg:latest
```

### Run Example

```bash
docker run -it \
  --name tzpz_seg_test \
  -v /path/to/your/data/mri:/usr/src/app/data \
  zlzbme/zlz_prostate_mri_tzpz_seg \
  --Data_dir /usr/src/app/data
```

---

## 2️⃣ ProStaNet (Gland) — Whole Prostate Gland Segmentation

Performs 3D segmentation of the entire prostate gland from T2-weighted MRI.

### Pull Docker Image

```bash
docker pull zlzbme/zlz_prostate_mri_gland_seg:latest
```

### Run Example

```bash
docker run -it \
  --name gland_seg_test \
  -v /path/to/your/data/mri:/usr/src/app/data \
  zlzbme/zlz_prostate_mri_gland_seg \
  --Data_dir /usr/src/app/data
```

---

## 3️⃣ ProStaNet (csPCa) — Clinically Significant Prostate Cancer Segmentation

Performs detection and segmentation of clinically significant prostate cancer (csPCa) using co-registered T2W and ADC MRI.

### Pull Docker Image

```bash
docker pull zlzbme/zlz_prostate_mri_cspca_seg:latest
```

### Run Example

```bash
docker run -it \
  --name cspca_seg_test \
  -v /path/to/your/data:/usr/src/app/data \
  zlzbme/zlz_prostate_mri_cspca_seg \
  --Data_dir /usr/src/app/data
```

> ⚠️ Ensure matching filenames between `/t2w/` and `/adc/`.

---

# 📚 Citation

If you use these models in your research, please cite the following works.

### ProZonaNet — Zonal Segmentation

Zhang et al.  
*Medical Physics*, 2025

DOI:  
https://aapm.onlinelibrary.wiley.com/doi/10.1002/mp.18053

---

### ProStaNet — Gland and csPCa Segmentation

Zhang et al.  
*Journal of Urology*, 2025

DOI:  
https://www.auajournals.org/doi/abs/10.1097/01.JU.0001110136.41716.b7.25

---

# 🐳 Docker Deployment

All models are distributed as Docker containers to support:

- Reproducible inference
- Cross-platform deployment
- Simplified dependency management
- Collaborative research integration

Docker images are publicly available through Docker Hub:

https://hub.docker.com/u/zlzbme

---

# 📬 Contact

For questions regarding model usage, deployment, collaboration, or research integration, please contact:

```text
Zelin Zhang
Emory University
Madabhushi Lab
zelinbmi@gmail.com
```

---

# 📜 License

This project is released under the MIT License.

---

# 🔗 Related Links

- Docker Hub: https://hub.docker.com/u/zlzbme
- Medical Physics Paper (ProZonaNet): https://aapm.onlinelibrary.wiley.com/doi/10.1002/mp.18053
- Journal of Urology Paper (ProStaNet): https://www.auajournals.org/doi/abs/10.1097/01.JU.0001110136.41716.b7.25

---

# ⚠️ Notes

This repository is intended primarily for academic and research use.

Please contact the developer prior to external redistribution, deployment in commercial environments, or integration into external collaborative studies.

---

> © 2025 Emory Empathetic AI for Health Institute  
> Madabhushi Lab — Emory University