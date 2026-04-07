---
tool_name: Anomaly Detection
lab: "Mayo"
poc: "TBD"
repo_path: ""
short_description: "OOD detection for safe cross-institution deployment; also completes the RadIQ FM-OOD component."
category: "data-harmonization"
tags:
    - clinical: [radiology]
    - data: [imaging]
last_updated: "2026-04-07"
publication: ""
package_url: ""
---

# Model Card: Anomaly Detection

> **Status:** Missing | **Type:** placeholder | **Lab:** Mayo | **POC:** TBD

This tool is planned but not yet implemented. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path. Target path: `01_data_harmonization/radiology/`

**Description:** Out-of-distribution anomaly detection for safe cross-institution model deployment. Also intended to complete the FM-OOD component of [RadIQ](radiq-fm-ood.md). Detects images or data that fall outside the training distribution, enabling safe gating before downstream models are applied. Position in pipeline: `01_data_harmonization` — cross-institution deployment safety layer. Will complement [RadQy](../../01_data_harmonization/radiology/RadQy-master/MODEL_CARD.md) and [RadIQ FM-OOD](radiq-fm-ood.md); expected to gate input to all downstream MEFINDER models when deployed at new institutions.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Mayo
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
