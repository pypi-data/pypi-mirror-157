from typing import Tuple, List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from tonic_reporting.util import make_data_transformer, filter_null_and_match_row_counts
from tonic_reporting.styling import Colors, PlotsSizes, FontSizes
from sklearn.neighbors import BallTree
from sklearn.neighbors import NearestNeighbors


def compute_dcr(
    real_data: pd.DataFrame,
    synth_data: pd.DataFrame,
    numeric_columns: List[str],
    categorical_columns: List[str],
) -> Tuple[np.ndarray, np.ndarray]:
    real_data, synth_data = filter_null_and_match_row_counts(
        real_data, synth_data, numeric_columns + categorical_columns
    )

    """Computes Distances-to-Closest-Record for synth-to-real and real-to-real
    Real and synthetic data is transformed to unit square in R^n by transforming
    numeric columns with MinMaxScaler and categorical columns via OneHotEncoder.
    Nearest-neighbors are computed and the corresponding distances returned.
    """
    column_transformer = make_data_transformer(
        real_data, numeric_columns, categorical_columns
    )
    X_real = column_transformer.transform(real_data)
    X_synth = column_transformer.transform(synth_data)
    tree = BallTree(X_real, leaf_size=2)
    synth_distances, syn_indices = tree.query(X_synth, k=1)
    nbrs = NearestNeighbors(n_neighbors=2, algorithm="ball_tree").fit(X_real)
    real_distances, real_indices = nbrs.kneighbors(X_real)

    return synth_distances[:, 0], real_distances[:, 1]


def plot_dcr(source_df, synth_df, numeric_cols, categorical_cols):
    syn_dcr, real_dcr = compute_dcr(source_df, synth_df, numeric_cols, categorical_cols)

    fig, ax = plt.subplots(1, 1, figsize=(PlotsSizes.DEFAULT_WIDTH, PlotsSizes.DEFAULT_HEIGHT))
    ax.hist(real_dcr, bins=300, label="Real vs. real", color=Colors.REAL)
    ax.hist(syn_dcr, bins=300, label="Synthetic vs. real", color=Colors.SYNTH)
    ax.tick_params(axis="both", which="major", labelsize=FontSizes.DEFAULT)
    ax.legend(fontsize=FontSizes.LARGE)
    plt.show(block=False)
