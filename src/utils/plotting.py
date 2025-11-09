import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Optional, Dict, Any


def plot_correlation_heatmap(
    df,
    *,
    numeric_only: bool = True,
    cmap: str = "plasma",
    figsize: tuple = (12, 10),
    annot: bool = True,
    fmt: str = ".2f",
    show_mask_upper: bool = True,
    show_clustermap: bool = True,
    clustermap_kwargs: Optional[Dict[str, Any]] = None,
    set_style: bool = True,
):
    """
    Trace une heatmap de corrélation (et facultativement un clustermap).

    Paramètres:
    - df: DataFrame source
    - numeric_only: calculer la corrélation sur les colonnes numériques
    - cmap: nom de la palette seaborn/matplotlib à utiliser
    - figsize: taille de la figure pour la heatmap
    - annot: afficher les annotations (valeurs)
    - fmt: format des annotations
    - show_mask_upper: masquer la triangle supérieur (True recommande pour symétrie)
    - show_clustermap: tracer aussi un clustermap (optionnel)
    - clustermap_kwargs: dict supplémentaire passé à sns.clustermap
    - set_style: appliquer sns.set_theme / set_context (peut être désactivé si appelé plusieurs fois)
    """
    if set_style:
        sns.set_theme(style="white")
        sns.set_context("notebook", font_scale=1)

    corr = df.corr(numeric_only=numeric_only)

    mask = np.triu(np.ones_like(corr, dtype=bool)) if show_mask_upper else None
    cmap_obj = sns.color_palette(cmap, as_cmap=True)

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        corr,
        mask=mask,
        cmap=cmap_obj,
        vmin=-1,
        vmax=1,
        center=0,
        annot=annot,
        fmt=fmt,
        annot_kws={"size": 10},
        linewidths=0.6,
        linecolor="white",
        square=False,
        cbar_kws={"shrink": 0.8, "label": "Pearson r"},
        ax=ax,
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.set_title("Feature correlation (numeric) — Pearson r", fontsize=14)
    plt.tight_layout()
    plt.show()

    cg = None
    if show_clustermap:
        cm_kwargs = dict(
            cmap=cmap_obj,
            center=0,
            method="average",
            metric="euclidean",
            figsize=(11, 11),
            annot=annot,
            fmt=fmt,
            annot_kws={"size": 8},
            cbar_kws={"label": "Pearson r", "shrink": 0.7},
        )
        if clustermap_kwargs:
            cm_kwargs.update(clustermap_kwargs)
        cg = sns.clustermap(corr, **cm_kwargs)
        plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
        plt.setp(cg.ax_heatmap.xaxis.get_majorticklabels(), rotation=45, ha="right")
        plt.show()


def plot_outliers(data, feature):
    """
    Plots outliers for a given feature in the provided data using the percentile method.
    Outliers are detected based on the specified feature and are determined by values
    falling outside the 1% and 99% percentiles for each interval.

    Parameters:
    - data (DataFrame): The input DataFrame containing the data.
    - feature (str): The name of the feature for which outliers will be detected and plotted.
    """

    df = data.copy()
    df = df.merge(
        df.groupby("interval")
        .quantile(0.01, numeric_only=True)[feature]
        .rename("OUTLIERS_LOW"),
        on="interval",
        how="left",
    )
    df = df.merge(
        df.groupby("interval")
        .quantile(0.99, numeric_only=True)[feature]
        .rename("OUTLIERS_HIGH"),
        on="interval",
        how="left",
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(
        data=df,
        y=feature,
        x="interval",
        hue="actual power",
        palette="gray",
        alpha=0.1,
        legend=False,
    )
    sns.scatterplot(
        data=df.query(f"`{feature}` > OUTLIERS_HIGH"), y=feature, x="interval"
    )
    sns.scatterplot(
        data=df.query(f"`{feature}` < OUTLIERS_LOW"), y=feature, x="interval"
    )

    plt.ylabel(feature)
    plt.xlabel("Hour of Day")
    ax.set_xticks([i for i in range(1, 97, 4)])
    ax.set_xticklabels([i for i in range(24)])
    ax.legend(["data", "outliers_high", "outliers_low"])
