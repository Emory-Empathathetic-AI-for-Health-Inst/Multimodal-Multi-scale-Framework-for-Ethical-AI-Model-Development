#!/usr/bin/env python3
import os
import random
import pickle

import numpy as np
import pandas as pd
import torch
import torch.backends.cudnn as cudnn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tqdm.auto import tqdm
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split

from losses import MultiTaskLoss
from models import Model
from utils import define_optimizer, define_scheduler, compute_metrics
from parameters import parse_args
from datasets import RadPathDataset, custom_collate


def set_seed(seed: int = 2023) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    cudnn.deterministic = True
    cudnn.benchmark = False


def make_model_name(args) -> str:
    return f"{args.fusion_type}_{args.task}_{args.n_epochs}_{args.lr}_{args.feature_type}_s{args.num_slices}"


def make_fixed_dev_test_split(
    data: pd.DataFrame,
    label_col: str = "grade",
    dev_size: float = 0.80,
    test_size: float = 0.20,
    min_pos_test: int = 5,
    max_trials: int = 5000,
):
    if abs(dev_size + test_size - 1.0) > 1e-6:
        raise ValueError("dev_size + test_size must sum to 1.0")

    y = data[label_col].astype(int)
    total_pos = int((y == 1).sum())
    total_neg = int((y == 0).sum())

    print("\nDataset summary")
    print("----------------")
    print("Total cases:", len(data))
    print("BCR+:", total_pos)
    print("BCR-:", total_neg)

    if total_pos < min_pos_test:
        raise ValueError(
            f"Not enough positives ({total_pos}) to guarantee at least {min_pos_test} positives in the test cohort."
        )

    for seed in range(max_trials):
        dev_df, test_df = train_test_split(
            data,
            test_size=test_size,
            stratify=data[label_col].astype(int),
            random_state=seed,
        )

        test_pos = int((test_df[label_col] == 1).sum())

        if test_pos >= min_pos_test:
            dev_df = dev_df.reset_index(drop=True)
            test_df = test_df.reset_index(drop=True)

            print("\nIndependent split chosen with seed:", seed)
            print("Development cohort:", len(dev_df), "| BCR+ =", int((dev_df[label_col] == 1).sum()))
            print("Independent test cohort:", len(test_df), "| BCR+ =", test_pos)

            print("\nDevelopment cohort label counts:")
            print(dev_df[label_col].value_counts().sort_index())
            print("\nIndependent test cohort label counts:")
            print(test_df[label_col].value_counts().sort_index())

            return dev_df, test_df

    raise RuntimeError(f"Could not find a valid independent split after {max_trials} trials.")


def make_train_val_split_with_min_pos(
    dev_df: pd.DataFrame,
    label_col: str = "grade",
    train_fraction_within_dev: float = 0.80,
    val_fraction_within_dev: float = 0.20,
    min_pos_val: int = 3,
    max_trials: int = 5000,
):
    if abs(train_fraction_within_dev + val_fraction_within_dev - 1.0) > 1e-6:
        raise ValueError("train_fraction_within_dev + val_fraction_within_dev must sum to 1.0")

    total_pos_dev = int((dev_df[label_col].astype(int) == 1).sum())
    if total_pos_dev < min_pos_val:
        raise ValueError(
            f"Not enough positives ({total_pos_dev}) in dev cohort to guarantee {min_pos_val} positives in validation."
        )

    for seed in range(max_trials):
        train_df, val_df = train_test_split(
            dev_df,
            test_size=val_fraction_within_dev,
            stratify=dev_df[label_col].astype(int),
            random_state=seed,
        )

        val_pos = int((val_df[label_col] == 1).sum())
        if val_pos >= min_pos_val:
            train_df = train_df.reset_index(drop=True)
            val_df = val_df.reset_index(drop=True)

            print("\nTrain/Val split inside development cohort chosen with seed:", seed)
            print("Train:", len(train_df), "| BCR+ =", int((train_df[label_col] == 1).sum()))
            print("Val:", len(val_df), "| BCR+ =", val_pos)

            print("\nTrain label counts:")
            print(train_df[label_col].value_counts().sort_index())
            print("\nVal label counts:")
            print(val_df[label_col].value_counts().sort_index())

            return train_df, val_df

    raise RuntimeError(f"Could not find a valid train/val split after {max_trials} trials.")


def build_loaders(args, train_df, val_df, test_df):
    num_workers = getattr(args, "num_workers", 0)
    pin_memory = torch.cuda.is_available()

    train_set = RadPathDataset(
        df=train_df,
        root_data=args.dataroot,
        index=None,
        ring=15,
        num_slices=4,   # fixed 4-slice setup
        out_h=128,
        out_w=128,
    )

    val_set = RadPathDataset(
        df=val_df,
        root_data=args.dataroot,
        index=None,
        ring=15,
        num_slices=4,   # fixed 4-slice setup
        out_h=128,
        out_w=128,
    )

    test_set = RadPathDataset(
        df=test_df,
        root_data=args.dataroot,
        index=None,
        ring=15,
        num_slices=4,   # fixed 4-slice setup
        out_h=128,
        out_w=128,
    )

    train_loader = DataLoader(
        train_set,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        collate_fn=custom_collate,
        drop_last=True,
    )

    val_loader = DataLoader(
        val_set,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        collate_fn=custom_collate,
        drop_last=False,
    )

    test_loader = DataLoader(
        test_set,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        collate_fn=custom_collate,
        drop_last=False,
    )

    return train_loader, val_loader, test_loader


def one_epoch(args, split, model, optimizer, loader, criterion, device):
    if split == "train":
        model.train()
    else:
        model.eval()

    total = 0
    sum_loss = 0.0

    all_preds_grade = []
    all_grade = []
    all_time = []
    all_event = []
    all_ID = []

    for mod1, mod2, mod3, grade, time, event, ID in loader:
        mod1 = mod1.to(device).float()
        mod2 = mod2.to(device).float()
        mod3 = mod3.to(device).float()
        grade = grade.to(device)
        time = time.to(device)
        event = event.to(device)

        batch_size = mod1.shape[0]

        if split == "train":
            pred = model(mod1, mod2, mod3, batch_size)
        else:
            with torch.no_grad():
                pred = model(mod1, mod2, mod3, batch_size)

        if isinstance(pred, (tuple, list)):
            pred_grade = pred[0]
        else:
            pred_grade = pred

        pred_grade = pred_grade.reshape(-1).float()
        grade = grade.reshape(-1).float()
        time = time.reshape(-1).float()
        event = event.reshape(-1).float()

        loss = criterion("grade", pred_grade, None, grade, time, event)

        if split == "train":
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        total += batch_size
        sum_loss += loss.item() * batch_size

        all_preds_grade.append(pred_grade.detach().cpu())
        all_grade.append(grade.detach().cpu())
        all_time.append(time.detach().cpu())
        all_event.append(event.detach().cpu())
        all_ID.extend(ID)

    all_preds_grade = torch.cat(all_preds_grade)
    all_grade = torch.cat(all_grade)
    all_time = torch.cat(all_time)
    all_event = torch.cat(all_event)

    preds_tuple = (all_preds_grade, None, all_grade, all_time, all_event, all_ID)
    return sum_loss / total, preds_tuple


def train_model(args, data, model, device, model_name):
    # Step 1: fixed 70/30 development vs independent test cohort
    dev_df, test_df = make_fixed_dev_test_split(
        data=data,
        label_col="grade",
        dev_size=0.70,
        test_size=0.30,
        min_pos_test=5,
        max_trials=5000,
    )

    # Step 2: split development cohort into train/val
    train_df, val_df = make_train_val_split_with_min_pos(
        dev_df=dev_df,
        label_col="grade",
        train_fraction_within_dev=0.80,
        val_fraction_within_dev=0.20,
        min_pos_val=3,
        max_trials=5000,
    )

    train_loader, val_loader, test_loader = build_loaders(args, train_df, val_df, test_df)

    criterion = MultiTaskLoss()
    optimizer = define_optimizer(args, model)
    scheduler = define_scheduler(args, optimizer)

    out_dir = os.path.join(args.checkpoints_dir, args.exp_name, model_name)
    os.makedirs(out_dir, exist_ok=True)

    dev_df.to_csv(os.path.join(out_dir, "development_cohort.csv"), index=False)
    train_df.to_csv(os.path.join(out_dir, "train_split.csv"), index=False)
    val_df.to_csv(os.path.join(out_dir, "val_split.csv"), index=False)
    test_df.to_csv(os.path.join(out_dir, "independent_test_cohort.csv"), index=False)

    with open(os.path.join(out_dir, "run_config.txt"), "w") as f:
        for k, v in sorted(vars(args).items()):
            f.write(f"{k}: {v}\n")
        f.write("fixed_num_slices: 4\n")
        f.write("independent_test_fraction: 0.30\n")
        f.write("development_fraction: 0.70\n")

    metric_logger = {
        "train": {"loss": [], "grad_auc": []},
        "val": {"loss": [], "grad_auc": []},
        "test": {"loss": None, "grad_auc": None},
        "logged_epochs": [],
    }

    best_loss = float("inf")
    best_val_auc = -1.0

    for epoch in tqdm(range(args.n_epochs)):
        train_loss, train_preds = one_epoch(
            args, "train", model, optimizer, train_loader, criterion, device
        )
        val_loss, val_preds = one_epoch(
            args, "val", model, None, val_loader, criterion, device
        )

        scheduler.step()

        _, auc_train = compute_metrics(args, train_preds)
        _, auc_val = compute_metrics(args, val_preds)

        metric_logger["logged_epochs"].append(epoch)
        metric_logger["train"]["loss"].append(train_loss)
        metric_logger["train"]["grad_auc"].append(auc_train)
        metric_logger["val"]["loss"].append(val_loss)
        metric_logger["val"]["grad_auc"].append(auc_val)

        print(f"\nEpoch {epoch}")
        print(f"Train loss: {train_loss}")
        print(f"Train AUC:  {auc_train}")
        print(f"Val loss:   {val_loss}")
        print(f"Val AUC:    {auc_val}")

        # best-by-loss checkpoint
        if val_loss < best_loss:
            best_loss = val_loss
            ckpt_path = os.path.join(out_dir, f"{model_name}_best_loss.pt")
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                    "metrics": metric_logger,
                },
                ckpt_path,
            )
            print("Saved best-loss model:", ckpt_path)

        # best-by-AUC checkpoint
        if auc_val > best_val_auc:
            best_val_auc = auc_val
            ckpt_path = os.path.join(out_dir, f"{model_name}_best_auc.pt")
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                    "metrics": metric_logger,
                },
                ckpt_path,
            )
            print("Saved best-AUC model:", ckpt_path)

    final_path = os.path.join(out_dir, f"{model_name}_last.pt")
    torch.save(
        {
            "model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
            "metrics": metric_logger,
        },
        final_path,
    )
    print("Saved last model:", final_path)

    # Evaluate independent test cohort using best validation AUC checkpoint
    best_ckpt_path = os.path.join(out_dir, f"{model_name}_best_auc.pt")
    ckpt = torch.load(best_ckpt_path, map_location="cpu")
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)

    print("\nRunning INDEPENDENT TEST evaluation using BEST validation AUC checkpoint")
    test_loss, test_preds = one_epoch(
        args, "test", model, None, test_loader, criterion, device
    )
    _, auc_test = compute_metrics(args, test_preds)

    metric_logger["test"]["loss"] = test_loss
    metric_logger["test"]["grad_auc"] = auc_test

    print("Independent test loss:", test_loss)
    print("Independent test AUC: ", auc_test)

    with open(os.path.join(out_dir, "independent_test_preds.pkl"), "wb") as f:
        pickle.dump(test_preds, f)

    return metric_logger


def save_training_plot(metric_logger, args, model_name):
    out_dir = os.path.join(args.checkpoints_dir, args.exp_name, model_name)
    os.makedirs(out_dir, exist_ok=True)

    epochs = metric_logger["logged_epochs"]

    plt.figure(figsize=(10, 8))

    plt.subplot(2, 1, 1)
    plt.plot(epochs, metric_logger["train"]["loss"], label="train")
    plt.plot(epochs, metric_logger["val"]["loss"], label="val")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(epochs, metric_logger["train"]["grad_auc"], label="train")
    plt.plot(epochs, metric_logger["val"]["grad_auc"], label="val")
    plt.xlabel("Epoch")
    plt.ylabel("AUC")
    plt.title("Training and Validation AUC (BCR)")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "training_curves.png"), dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    args = parse_args()

    print("\n================= RUN CONFIG =================")
    for k, v in sorted(vars(args).items()):
        print(f"{k}: {v}")
    print("fixed_num_slices: 4")
    print("independent_test_fraction: 0.30")
    print("development_fraction: 0.70")
    print("==============================================\n")

    set_seed(2023)

    if isinstance(args.gpu_ids, str):
        args.gpu_ids = [int(x) for x in args.gpu_ids.split(",") if x.strip() != ""]

    if args.task != "grade":
        raise ValueError("This main.py is for BCR classification only. Use --task grade")

    if args.batch_size < 2:
        raise ValueError("Use --batch_size >= 2 because the pathology branch has BatchNorm.")

    device = torch.device(f"cuda:{args.gpu_ids[0]}") if args.gpu_ids else torch.device("cpu")
    print("Using device:", device)

    model_name = make_model_name(args)
    print("Experiment:", model_name)

    train_csv = os.path.join(args.dataroot, "data_table_bcr.csv")
    if not os.path.exists(train_csv):
        raise FileNotFoundError(f"Missing training CSV: {train_csv}")

    data = pd.read_csv(
        train_csv,
        dtype={
            "pathology_folder_name": str,
            "radiology_folder_name": str,
        },
    )

    required = [
        "radiology_folder_name",
        "pathology_folder_name",
        "grade",
        "DFS",
        "DFS_censor",
        "OS",
        "OS_censor",
        "X_min_tumor",
        "X_max_tumor",
        "Y_min_tumor",
        "Y_max_tumor",
        "Z_min_tumor",
        "Z_max_tumor",
        "X_min_lymph",
        "X_max_lymph",
        "Y_min_lymph",
        "Y_max_lymph",
        "Z_min_lymph",
        "Z_max_lymph",
    ]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns in training CSV: {missing}")

    print("\nLabel distribution in full dataset:")
    print(data["grade"].value_counts().sort_index())

    model = Model(args)
    model.to(device)

    metric_logger = train_model(args, data, model, device, model_name)
    save_training_plot(metric_logger, args, model_name)