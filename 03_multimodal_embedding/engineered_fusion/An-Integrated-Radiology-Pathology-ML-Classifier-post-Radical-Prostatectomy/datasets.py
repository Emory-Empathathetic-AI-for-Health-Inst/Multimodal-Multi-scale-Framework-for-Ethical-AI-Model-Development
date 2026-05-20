import numpy as np
import torch
from torch.utils.data import Dataset
import os
from math import ceil, floor
from medpy.io import load
import torch.nn.functional as F


def custom_collate(batch):
    mod1 = [item[0] for item in batch]
    mod2 = [item[1] for item in batch]
    pathology = [item[2] for item in batch]
    grade = torch.stack([item[3] for item in batch], dim=0)
    time = torch.stack([item[4] for item in batch], dim=0)
    event = torch.stack([item[5] for item in batch], dim=0)
    ID = [item[6] for item in batch]

    # radiology: [B, 1, D, H, W]
    mod1 = torch.stack(mod1, dim=0)
    mod2 = torch.stack(mod2, dim=0)

    if len(pathology) == 0:
        raise ValueError("Empty pathology batch")

    for i, p in enumerate(pathology):
        if p.ndim != 2:
            raise ValueError(f"Expected pathology tensor [N, F], got {p.shape} at item {i}")

    max_n = max(p.shape[0] for p in pathology)
    feat_dim = pathology[0].shape[1]

    padded_pathology = []
    for p in pathology:
        if p.shape[1] != feat_dim:
            raise ValueError(
                f"Inconsistent pathology feature dimension: expected {feat_dim}, got {p.shape[1]}"
            )
        n_pad = max_n - p.shape[0]
        if n_pad > 0:
            p = F.pad(p, (0, 0, 0, n_pad), mode="constant", value=0)
        padded_pathology.append(p)

    pathology = torch.stack(padded_pathology, dim=0)

    return mod1, mod2, pathology, grade, time, event, ID


def custom_collate_pathology(data):
    pathology, y, time, event, ID = zip(*data)
    max_sizes = (
        max([path.shape[0] for path in pathology]),
        max([path.shape[1] for path in pathology])
    )
    pathology = list(pathology)
    ID = list(ID)

    for i in range(len(pathology)):
        pathology[i] = torch.moveaxis(pathology[i], -1, 0)
        pad_2d = max_sizes[1] - pathology[i].shape[2]
        pad_3d = max_sizes[0] - pathology[i].shape[1]
        padding = (
            floor(pad_2d / 2), ceil(pad_2d / 2),
            floor(pad_2d / 2), ceil(pad_2d / 2),
            floor(pad_3d / 2), ceil(pad_3d / 2)
        )
        m = torch.nn.ConstantPad3d(padding, 0)
        pathology[i] = m(pathology[i])
        pathology[i] = torch.permute(pathology[i], (1, 0, 2, 3)).float()

    return torch.stack(pathology), torch.tensor(y), torch.tensor(time), torch.tensor(event), ID


class HandCraftedFeaturesDataset(Dataset):
    def __init__(self, df, index=None, random_noise_sigma=0):
        df = df.copy()
        if index is not None:
            df = df.iloc[index]

        self.mod1 = np.array(
            df[['rad0', 'rad1', 'rad2', 'rad3', 'rad4', 'rad5', 'rad6']]
        ).astype(np.float32)

        self.mod2 = np.array(
            df[['path0', 'path1', 'path2', 'path3', 'path4', 'path5', 'path6']]
        ).astype(np.float32)

        self.y = np.array(df["grade"]).astype(np.float32)
        self.time = np.array(df["DFS"]).astype(np.float32)
        self.event = np.array(df["DFS_censor"]).astype(np.float32)
        self.random_noise_sigma = random_noise_sigma

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        features_mod1 = self.mod1[idx]
        features_mod1 += np.random.randn(*features_mod1.shape) * self.random_noise_sigma
        mean1 = np.mean(features_mod1, 0)
        std1 = np.std(features_mod1, 0)
        features_mod1 = (features_mod1 - mean1) / (std1 + 1e-8)

        features_mod2 = self.mod2[idx]
        features_mod2 += np.random.randn(*features_mod2.shape) * self.random_noise_sigma
        mean2 = np.mean(features_mod2, 0)
        std2 = np.std(features_mod2, 0)
        features_mod2 = (features_mod2 - mean2) / (std2 + 1e-8)

        return features_mod1, features_mod2, self.y[idx], self.time[idx], self.event[idx]


class RadPathDataset(Dataset):
    def __init__(self, df, root_data, index=None, dim=None, ring=15, num_slices=4, out_h=128, out_w=128):
        if index is not None:
            df = df.iloc[index].reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

        self.df = df
        self.y = torch.tensor(np.array(df["grade"]).astype(np.float32))
        self.time = torch.tensor(np.array(df["DFS"]).astype(np.float32))
        self.event = torch.tensor(np.array(df["DFS_censor"]).astype(np.float32))
        self.ID = np.array(df["radiology_folder_name"])

        self.ring = ring
        self.root_data = root_data
        self.num_slices = num_slices
        self.out_h = out_h
        self.out_w = out_w

    def __len__(self):
        return len(self.y)

    def _load_mri(self, index):
        mri_file = os.path.join(
            self.root_data,
            "t2w",
            self.df.loc[index, "radiology_folder_name"] + ".nii.gz"
        )
        mri_image, _ = load(mri_file)
        mri_image = mri_image.astype(np.float32)

        mean = np.mean(mri_image)
        std = np.std(mri_image)
        if std > 0:
            mri_image = (mri_image - mean) / std

        return mri_image

    def _load_pathology(self, index):
        pathology_file = os.path.join(
            self.root_data,
            "hipt_features",
            str(self.df.loc[index, "pathology_folder_name"]) + ".pt"
        )

        pathology = torch.load(pathology_file, map_location="cpu")

        if isinstance(pathology, dict):
            for key in ["features", "embeddings", "feat", "x"]:
                if key in pathology:
                    pathology = pathology[key]
                    break

        if not isinstance(pathology, torch.Tensor):
            pathology = torch.tensor(pathology)

        pathology = pathology.float()

        if pathology.ndim == 1:
            pathology = pathology.unsqueeze(0)
        elif pathology.ndim > 2:
            pathology = pathology.reshape(-1, pathology.shape[-1])

        return pathology

    def _sample_even_z_indices(self, z_start, z_end, num_slices):
        z_candidates = np.arange(z_start, z_end + 1)
        if len(z_candidates) == 0:
            raise ValueError(f"Empty z range: {z_start}..{z_end}")

        if len(z_candidates) == 1:
            return np.array([z_candidates[0]] * num_slices, dtype=int)

        sample_pos = np.linspace(0, len(z_candidates) - 1, num_slices)
        sample_idx = np.round(sample_pos).astype(int)
        return z_candidates[sample_idx]

    def get_radiology(self, mri_image, index):
        concat_vols = []

        for location in ['tumor', 'lymph']:
            X_min = int(self.df.loc[index, "X_min_" + location])
            X_max = int(self.df.loc[index, "X_max_" + location])
            Y_min = int(self.df.loc[index, "Y_min_" + location])
            Y_max = int(self.df.loc[index, "Y_max_" + location])
            Z_min = int(self.df.loc[index, "Z_min_" + location])
            Z_max = int(self.df.loc[index, "Z_max_" + location])

            X_min = max(0, X_min - self.ring)
            Y_min = max(0, Y_min - self.ring)
            Z_min = max(0, Z_min - self.ring)

            X_max = min(mri_image.shape[0] - 1, X_max + self.ring)
            Y_max = min(mri_image.shape[1] - 1, Y_max + self.ring)
            Z_max = min(mri_image.shape[2] - 1, Z_max + self.ring)

            if X_max < X_min or Y_max < Y_min or Z_max < Z_min:
                raise ValueError(
                    f"Invalid bbox for {location} at index {index}: "
                    f"X=({X_min},{X_max}), Y=({Y_min},{Y_max}), Z=({Z_min},{Z_max})"
                )

            z_indices = self._sample_even_z_indices(Z_min, Z_max, self.num_slices)

            slices = []
            for z in z_indices:
                sl = mri_image[X_min:X_max+1, Y_min:Y_max+1, z].astype(np.float32)
                if sl.size == 0:
                    raise ValueError(
                        f"Empty slice crop for {location} at index {index}, z={z}: "
                        f"X=({X_min},{X_max}), Y=({Y_min},{Y_max})"
                    )
                slices.append(sl)

            sub = np.stack(slices, axis=0)  # [D, H, W]
            sub = torch.from_numpy(sub).unsqueeze(0)  # [1, D, H, W]

            sub = F.interpolate(
                sub.unsqueeze(0),  # [1, 1, D, H, W]
                size=(self.num_slices, self.out_h, self.out_w),
                mode="trilinear",
                align_corners=False,
            ).squeeze(0)  # [1, D, H, W]

            concat_vols.append(sub)

        return concat_vols

    def __getitem__(self, index):
        mri_image = self._load_mri(index)
        rad_vols = self.get_radiology(mri_image, index)
        tz_vol, pz_vol = rad_vols[0], rad_vols[1]
        pathology = self._load_pathology(index)

        return tz_vol, pz_vol, pathology, self.y[index], self.time[index], self.event[index], self.ID[index]


class RadDataset(Dataset):
    def __init__(self, df, root_data, index=None, dim=None, ring=15, num_slices=4, out_h=128, out_w=128):
        if index is not None:
            df = df.iloc[index].reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

        self.df = df
        self.y = torch.tensor(np.array(df["grade"]).astype(np.float32))
        self.time = torch.tensor(np.array(df["DFS"]).astype(np.float32))
        self.event = torch.tensor(np.array(df["DFS_censor"]).astype(np.float32))
        self.ID = np.array(df["radiology_folder_name"])

        self.ring = ring
        self.root_data = root_data
        self.num_slices = num_slices
        self.out_h = out_h
        self.out_w = out_w

    def __len__(self):
        return len(self.y)

    def _load_mri(self, index):
        mri_file = os.path.join(
            self.root_data,
            "t2w",
            self.df.loc[index, "radiology_folder_name"] + ".nii.gz"
        )
        mri_image, _ = load(mri_file)
        mri_image = mri_image.astype(np.float32)

        mean = np.mean(mri_image)
        std = np.std(mri_image)
        if std > 0:
            mri_image = (mri_image - mean) / std

        return mri_image

    def _sample_even_z_indices(self, z_start, z_end, num_slices):
        z_candidates = np.arange(z_start, z_end + 1)
        if len(z_candidates) == 0:
            raise ValueError(f"Empty z range: {z_start}..{z_end}")

        if len(z_candidates) == 1:
            return np.array([z_candidates[0]] * num_slices, dtype=int)

        sample_pos = np.linspace(0, len(z_candidates) - 1, num_slices)
        sample_idx = np.round(sample_pos).astype(int)
        return z_candidates[sample_idx]

    def get_radiology(self, mri_image, index):
        concat_vols = []

        for location in ['tumor', 'lymph']:
            X_min = int(self.df.loc[index, "X_min_" + location])
            X_max = int(self.df.loc[index, "X_max_" + location])
            Y_min = int(self.df.loc[index, "Y_min_" + location])
            Y_max = int(self.df.loc[index, "Y_max_" + location])
            Z_min = int(self.df.loc[index, "Z_min_" + location])
            Z_max = int(self.df.loc[index, "Z_max_" + location])

            X_min = max(0, X_min - self.ring)
            Y_min = max(0, Y_min - self.ring)
            Z_min = max(0, Z_min - self.ring)

            X_max = min(mri_image.shape[0] - 1, X_max + self.ring)
            Y_max = min(mri_image.shape[1] - 1, Y_max + self.ring)
            Z_max = min(mri_image.shape[2] - 1, Z_max + self.ring)

            if X_max < X_min or Y_max < Y_min or Z_max < Z_min:
                raise ValueError(
                    f"Invalid bbox for {location} at index {index}: "
                    f"X=({X_min},{X_max}), Y=({Y_min},{Y_max}), Z=({Z_min},{Z_max})"
                )

            z_indices = self._sample_even_z_indices(Z_min, Z_max, self.num_slices)

            slices = []
            for z in z_indices:
                sl = mri_image[X_min:X_max+1, Y_min:Y_max+1, z].astype(np.float32)
                if sl.size == 0:
                    raise ValueError(
                        f"Empty slice crop for {location} at index {index}, z={z}: "
                        f"X=({X_min},{X_max}), Y=({Y_min},{Y_max})"
                    )
                slices.append(sl)

            sub = np.stack(slices, axis=0)  # [D, H, W]
            sub = torch.from_numpy(sub).unsqueeze(0)  # [1, D, H, W]

            sub = F.interpolate(
                sub.unsqueeze(0),  # [1, 1, D, H, W]
                size=(self.num_slices, self.out_h, self.out_w),
                mode="trilinear",
                align_corners=False,
            ).squeeze(0)  # [1, D, H, W]

            concat_vols.append(sub)

        return concat_vols

    def __getitem__(self, index):
        mri_image = self._load_mri(index)
        rad_vols = self.get_radiology(mri_image, index)
        tz_vol, pz_vol = rad_vols[0], rad_vols[1]

        return tz_vol, pz_vol, self.y[index], self.time[index], self.event[index], self.ID[index]


class PathDataset(Dataset):
    def __init__(self, df, root_data, index=None):
        if index is not None:
            df = df.iloc[index].reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

        self.df = df
        self.y = torch.tensor(np.array(df["grade"]).astype(np.float32))
        self.time = torch.tensor(np.array(df["OS"]).astype(np.float32))
        self.event = torch.tensor(np.array(df["OS_censor"]).astype(np.float32))
        self.ID = np.array(df["radiology_folder_name"])
        self.root_data = root_data

    def __len__(self):
        return len(self.y)

    def __getitem__(self, index):
        pathology_file = os.path.join(
            self.root_data,
            "hipt_features",
            str(self.df.loc[index, "pathology_folder_name"]) + ".pt"
        )

        pathology = torch.load(pathology_file, map_location="cpu")

        if isinstance(pathology, dict):
            for key in ["features", "embeddings", "feat", "x"]:
                if key in pathology:
                    pathology = pathology[key]
                    break

        if not isinstance(pathology, torch.Tensor):
            pathology = torch.tensor(pathology)

        pathology = pathology.float()

        if pathology.ndim == 1:
            pathology = pathology.unsqueeze(0)
        elif pathology.ndim > 2:
            pathology = pathology.reshape(-1, pathology.shape[-1])

        return pathology, self.y[index], self.time[index], self.event[index], self.ID[index]