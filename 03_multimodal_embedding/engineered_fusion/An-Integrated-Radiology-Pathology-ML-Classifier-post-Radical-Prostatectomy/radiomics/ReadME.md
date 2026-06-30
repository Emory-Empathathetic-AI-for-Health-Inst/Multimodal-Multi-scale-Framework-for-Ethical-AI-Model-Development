## BCR Prediction

Install the required Python packages:

```bash
pip install numpy pandas
```

Place the following files in the same folder:

```text
bcr_fusion_model.json
<CSV file 1>
<CSV file 2>
<CSV file 3>
```

Set `DATA_DIR` to the folder containing these files, then run:

```bash
python predict_bcr.py
```

The script will generate the BCR prediction output file.
