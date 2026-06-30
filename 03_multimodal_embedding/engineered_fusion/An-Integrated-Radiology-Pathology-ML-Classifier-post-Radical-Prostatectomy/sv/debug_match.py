# save as debug_match.py and run it
import os, re
from typing import Optional, List

def iter_nii_files(root):
    out = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".nii") or fn.endswith(".nii.gz"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)

def strip_nii_ext(name):
    if name.endswith(".nii.gz"): return name[:-7]
    if name.endswith(".nii"):    return name[:-4]
    return name

def strip_channel_suffix(stem):
    return re.sub(r'_\d{4}$', '', stem)

def find_matching_file(case_id, search_dir):
    case_id_clean = strip_channel_suffix(case_id)
    print(f"  Looking for case_id_clean: '{case_id_clean}' in {search_dir}")

    for ext in [".nii.gz", ".nii"]:
        p = os.path.join(search_dir, f"{case_id_clean}{ext}")
        print(f"  Step1 check: {p} -> exists={os.path.exists(p)}")
        if os.path.exists(p):
            return p

    for ext in [".nii.gz", ".nii"]:
        p = os.path.join(search_dir, f"{case_id_clean}_0000{ext}")
        print(f"  Step2 check: {p} -> exists={os.path.exists(p)}")
        if os.path.exists(p):
            return p

    print(f"  Step3: walking directory...")
    for p in iter_nii_files(search_dir):
        file_stem = strip_nii_ext(os.path.basename(p))
        cleaned   = strip_channel_suffix(file_stem)
        print(f"    file_stem='{file_stem}' -> cleaned='{cleaned}' == case_id_clean='{case_id_clean}'? {cleaned == case_id_clean}")
        if cleaned == case_id_clean:
            return p

    return None

# --- run test ---
sv_dir   = "/home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026/PICCAI_extended/ciPCA/sv"
t2w_dir  = "/home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026/PICCAI_extended/ciPCA/t2w"
tzpz_dir = "/home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026/PICCAI_extended/ciPCA/tzpz"

sv_files = iter_nii_files(sv_dir)
print(f"Found {len(sv_files)} SV files\n")

for sv_path in sv_files[:3]:  # test first 3 cases
    case_id = strip_nii_ext(os.path.basename(sv_path))
    print(f"=== case_id from SV: '{case_id}' ===")

    t2w   = find_matching_file(case_id, t2w_dir)
    tzpz  = find_matching_file(case_id, tzpz_dir)

    print(f"  T2W match  : {t2w}")
    print(f"  TZPZ match : {tzpz}")
    print()
