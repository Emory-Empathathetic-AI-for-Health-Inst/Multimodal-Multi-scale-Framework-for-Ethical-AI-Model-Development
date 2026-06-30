#!/usr/bin/env python3
# aging_analysis_plots.py
#
# Comprehensive Aging Analysis for TZ–PZ Asymmetry Features
# Includes PCA, t-SNE, age regressions, group comparisons, and biomarker summary.

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import ttest_ind, mannwhitneyu, f_oneway, pearsonr

sns.set(style="whitegrid", context="talk")

# -----------------------------------------------------------
# Utility
# -----------------------------------------------------------

def clean_numeric(df, cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def regression_plot(df, x, y, out_dir, color):
    df2 = df[[x, y]].dropna()
    if df2.empty:
        return
    plt.figure(figsize=(7,6))
    sns.regplot(data=df2, x=x, y=y, color=color, scatter_kws={'alpha':0.6}, line_kws={'lw':3})
    r, p = pearsonr(df2[x], df2[y])
    plt.title(f"{y} vs {x}\nPearson r={r:.3f}, p={p:.3g}")
    plt.tight_layout()
    out_path = Path(out_dir)/f"{y}_vs_{x}.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"[saved] {out_path}")

# -----------------------------------------------------------
# PCA + tSNE Visualization
# -----------------------------------------------------------

def pca_tsne_maps(df, features, age_col, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_df = df.dropna(subset=[age_col])
    X = clean_df[features].astype(float).fillna(0)
    y = pd.to_numeric(clean_df[age_col], errors="coerce")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA
    pca = PCA(n_components=2)
    pcs = pca.fit_transform(X_scaled)
    clean_df["PC1"] = pcs[:,0]
    clean_df["PC2"] = pcs[:,1]

    # t-SNE
    tsne = TSNE(n_components=2, random_state=42, perplexity=25, init="pca", learning_rate="auto", n_iter=2000)
    tsne_coords = tsne.fit_transform(X_scaled)
    clean_df["tSNE1"], clean_df["tSNE2"] = tsne_coords[:,0], tsne_coords[:,1]

    plt.figure(figsize=(12,5))
    plt.subplot(1,2,1)
    sns.scatterplot(data=clean_df, x="PC1", y="PC2", hue=y, palette="coolwarm", s=70)
    plt.title("PCA Map colored by Age")
    plt.subplot(1,2,2)
    sns.scatterplot(data=clean_df, x="tSNE1", y="tSNE2", hue=y, palette="coolwarm", s=70)
    plt.title("t-SNE Map colored by Age")
    plt.tight_layout()
    plt.savefig(out_dir/"pca_tsne_maps.png", dpi=200)
    plt.close()

    # PCA loadings
    load = pd.DataFrame(pca.components_.T, index=features, columns=["PC1","PC2"])
    plt.figure(figsize=(7,8))
    sns.heatmap(load, cmap="vlag", center=0)
    plt.title("Feature Loadings on PCA")
    plt.tight_layout()
    plt.savefig(out_dir/"pca_feature_loadings.png", dpi=200)
    plt.close()
    print("[saved] PCA + tSNE maps and loadings")

# -----------------------------------------------------------
# Random Forest Feature Importance
# -----------------------------------------------------------

def rf_importance(df, features, age_col, out_dir):
    out_dir = Path(out_dir)
    clean_df = df.dropna(subset=[age_col])
    X = clean_df[features].astype(float).fillna(0)
    y = pd.to_numeric(clean_df[age_col], errors="coerce")
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)
    imp = pd.Series(model.feature_importances_, index=features).sort_values(ascending=True)
    plt.figure(figsize=(8,7))
    imp.tail(15).plot.barh(color="teal")
    plt.title("Feature Importance for Age Prediction (RF)")
    plt.tight_layout()
    plt.savefig(out_dir/"rf_importance.png", dpi=200)
    plt.close()
    print("[saved] RandomForest feature importance")
    return imp.sort_values(ascending=False)

# -----------------------------------------------------------
# Age Group Comparison + Biomarker Summary
# -----------------------------------------------------------

def assign_age_groups(df, age_col):
    age = pd.to_numeric(df[age_col], errors="coerce")
    bins = [0, 50, 70, 120]
    labels = ["<50", "50-70", ">70"]
    df["age_group"] = pd.cut(age, bins=bins, labels=labels, include_lowest=True)
    return df

def group_comparison(df, age_col, features, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = assign_age_groups(df, age_col)
    results = []

    for feat in features:
        if df[feat].dtype not in [np.float64, np.float32, np.int64, np.int32]:
            continue
        clean = df[[feat, "age_group"]].dropna()
        if clean["age_group"].nunique() < 2:
            continue
        groups = [clean.loc[clean["age_group"] == g, feat] for g in clean["age_group"].unique()]
        try:
            fstat, p_anova = f_oneway(*groups)
        except Exception:
            p_anova = np.nan
        younger, older = groups[0], groups[-1]
        tstat, p_t = ttest_ind(younger, older, equal_var=False)
        _, p_mw = mannwhitneyu(younger, older, alternative="two-sided")
        cohen_d = (np.nanmean(older)-np.nanmean(younger)) / (np.nanstd(np.concatenate(groups)) + 1e-8)
        results.append({
            "feature": feat,
            "p_ANOVA": p_anova,
            "p_ttest_<50_vs_>70": p_t,
            "p_MannWhitney_<50_vs_>70": p_mw,
            "cohen_d_(>70-<50)": cohen_d,
            "older_mean": np.nanmean(older),
            "younger_mean": np.nanmean(younger)
        })

        # Violin plot
        plt.figure(figsize=(5,5))
        sns.violinplot(data=clean, x="age_group", y=feat, palette="coolwarm", inner="box")
        sns.stripplot(data=clean, x="age_group", y=feat, color="black", alpha=0.4)
        plt.title(f"{feat} (ANOVA p={p_anova:.3g})")
        plt.tight_layout()
        plt.savefig(out_dir/f"{feat}_age_groups.png", dpi=200)
        plt.close()

    res_df = pd.DataFrame(results)
    res_df.to_csv(out_dir/"age_group_stats.csv", index=False)
    return res_df

def summarize_biomarkers(stats_df, rf_importances, out_dir):
    """Highlight statistically significant aging biomarkers."""
    sig = stats_df.copy()
    sig = sig.loc[sig["p_ttest_<50_vs_>70"] < 0.05]
    sig["abs_d"] = sig["cohen_d_(>70-<50)"].abs()
    sig = sig.sort_values("abs_d", ascending=False)

    top_rf = rf_importances.head(15).reset_index()
    top_rf.columns = ["feature","rf_importance"]

    bio_df = pd.merge(sig, top_rf, on="feature", how="left")
    bio_df = bio_df.sort_values(["abs_d","rf_importance"], ascending=False)

    # Save CSV
    bio_df.to_csv(out_dir/"biomarker_summary.csv", index=False)

    # Pretty print
    print("\n🧬 Top Aging Biomarkers (p<0.05):")
    if len(bio_df) == 0:
        print("  None found.")
    else:
        print(bio_df[["feature","p_ttest_<50_vs_>70","cohen_d_(>70-<50)","rf_importance"]].head(10))

# -----------------------------------------------------------
# Main
# -----------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Aging analysis: PCA, t-SNE, group tests, biomarker summary.")
    ap.add_argument("--features_csv", required=True, help="Output CSV from tzpz_symmetry_features.py")
    ap.add_argument("--excel", required=True, help="Metadata with ages")
    ap.add_argument("--output_dir", required=True, help="Directory to save results")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df_feat = pd.read_csv(args.features_csv)
    df_meta = pd.read_csv(args.excel)

    id_candidates = {"patient_id","PatientID","pid"}
    pid_feat = next((c for c in df_feat.columns if c in id_candidates), None)
    pid_meta = next((c for c in df_meta.columns if c in id_candidates), None)

    df = pd.merge(df_feat, df_meta, left_on=pid_feat, right_on=pid_meta, how="left")
    age_col = next((c for c in df.columns if "age" in c.lower()), None)
    if not age_col:
        raise SystemExit("No 'age' column found.")
    clean_numeric(df, [age_col])

    print(f"[merged] {len(df)} samples for analysis")

    # Regression plots
    targets = ["tz_left_right_ratio","tz_abs_diff_mm3","pz_left_right_ratio","pz_abs_diff_mm3","tz_to_pz_ratio"]
    for y in targets:
        if y in df.columns:
            color = "green" if "tz" in y else "red"
            regression_plot(df, age_col, y, out_dir, color)

    feature_cols = [c for c in df.columns if (("tz_" in c.lower()) or ("pz_" in c.lower())) and df[c].dtype != "object"]
    pca_tsne_maps(df, feature_cols, age_col, out_dir)
    rf_imp = rf_importance(df, feature_cols, age_col, out_dir)
    stats_df = group_comparison(df, age_col, feature_cols, out_dir)
    summarize_biomarkers(stats_df, rf_imp, out_dir)

    print(f"\n✅ Analysis complete. Results saved in {out_dir}")

if __name__ == "__main__":
    main()
