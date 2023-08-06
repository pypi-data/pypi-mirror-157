from nis import cat
from typing import Tuple, List, Callable
from dataclasses import dataclass
import math

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.preprocessing import OrdinalEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import r2_score, accuracy_score

from tonic_reporting.util import make_data_transformer


def split_columns(X, y_idx):
    x_idx = [i for i in range(X.shape[1]) if i != y_idx]
    return X[:, x_idx], X[:, y_idx]


def train_column_models(
    X_train_real: np.ndarray,
    X_train_fake: np.ndarray,
    column_idx: int,
    model_cls: BaseEstimator,
):
    X_train_real, y_train_real = split_columns(X_train_real, column_idx)
    X_train_fake, y_train_fake = split_columns(X_train_fake, column_idx)
    column_model_real = model_cls()
    column_model_real.fit(X_train_real, y_train_real)
    column_model_fake = model_cls()
    column_model_fake.fit(X_train_fake, y_train_fake)
    return column_model_real, column_model_fake


def score_column_model(
    X_train_real: np.ndarray,
    X_train_fake: np.ndarray,
    X_val: np.ndarray,
    column_idx: int,
    model_cls: BaseEstimator,
    score_metric: Callable,
):
    """Generic method for evaluating performance of model predicting selected column from remaining features"""

    column_model_real, column_model_fake = train_column_models(
        X_train_real, X_train_fake, column_idx, model_cls
    )
    X_val, y_val = split_columns(X_val, column_idx)
    y_hat_real = column_model_real.predict(X_val)
    y_hat_fake = column_model_fake.predict(X_val)
    return score_metric(y_val, y_hat_real), score_metric(y_val, y_hat_fake)


def score_ordinal_encoded_column(
    X_train_real: np.ndarray,
    X_train_fake: np.ndarray,
    X_val: np.ndarray,
    column_idx: int,
):
    """Evaluates accuracy of classification models for predicting selected categorical column from remaining features"""
    return score_column_model(
        X_train_real,
        X_train_fake,
        X_val,
        column_idx,
        RandomForestClassifier,
        accuracy_score,
    )


def score_numeric_column(
    X_train_real: np.ndarray,
    X_train_fake: np.ndarray,
    X_val: np.ndarray,
    column_idx: int,
):
    """Evalutes r2 of regression models for predicting selected numeric column from remaining features"""
    return score_column_model(
        X_train_real, X_train_fake, X_val, column_idx, RandomForestRegressor, r2_score
    )


def score_data_holdout(
    X_real: np.ndarray,
    X_fake: np.ndarray,
    X_holdout: np.ndarray,
    numeric_cols: List[str],
    categorical_cols: List[str],
):
    """Uses provided holdout dataset to compare predictive ability of models trained on synthetic data vs real data"""
    scores = []
    for i, col in enumerate(numeric_cols + categorical_cols):
        if i < len(numeric_cols):
            real_score, fake_score = score_numeric_column(X_real, X_fake, X_holdout, i)
        else:
            real_score, fake_score = score_ordinal_encoded_column(
                X_real, X_fake, X_holdout, i
            )
        scores.append(
            dict(
                real_score=real_score,
                fake_score=fake_score,
                relative_score=min(fake_score / real_score, 1),
                column=col,
            )
        )

    return pd.DataFrame(scores)


def score_data(
    X_real: np.ndarray,
    X_fake: np.ndarray,
    numeric_cols: List[str],
    categorical_cols: List[str],
    train_val_split=0.8,
):
    """Compares predictive ability of models trained on synthetic data vs real data"""
    scores = []
    n_rows = X_real.shape[0]
    n_train = int(math.floor(n_rows * train_val_split))
    idx = np.arange(0, n_rows)

    for i, col in enumerate(numeric_cols + categorical_cols):
        np.random.shuffle(idx)
        train_idx = idx[:n_train]
        val_idx = idx[n_train:]
        if i < len(numeric_cols):
            real_score, fake_score = score_numeric_column(
                X_real[train_idx], X_fake[train_idx], X_real[val_idx], i
            )
        else:
            real_score, fake_score = score_ordinal_encoded_column(
                X_real[train_idx], X_fake[train_idx], X_real[val_idx], i
            )
        scores.append(
            dict(
                real_score=real_score,
                fake_score=fake_score,
                relative_score=min(fake_score / real_score, 1),
                column=col,
            )
        )

    return pd.DataFrame(scores)


def score_data_holdout_from_df(
    source_df: pd.DataFrame,
    synth_df: pd.DataFrame,
    holdout_df: pd.DataFrame,
    numeric_cols: List[str],
    categorical_cols: List[str],
):
    data_transformer = make_data_transformer(
        source_df,
        numeric_cols,
        categorical_cols,
        numeric_transformer_cls="passthrough",
        categorical_transformer_cls=OrdinalEncoder,
    )
    X_real = data_transformer.transform(source_df)
    X_fake = data_transformer.transform(synth_df)
    X_hold = data_transformer.transform(holdout_df)
    return score_data_holdout(X_real, X_fake, X_hold, numeric_cols, categorical_cols)


def score_data_from_df(
    source_df: pd.DataFrame,
    synth_df: pd.DataFrame,
    numeric_cols: List[str],
    categorical_cols: List[str],
    train_val_split=0.8,
):
    data_transformer = make_data_transformer(
        source_df,
        numeric_cols,
        categorical_cols,
        numeric_transformer_cls="passthrough",
        categorical_transformer_cls=OrdinalEncoder,
    )
    X_real = data_transformer.transform(source_df)
    X_fake = data_transformer.transform(synth_df)
    return score_data(
        X_real, X_fake, numeric_cols, categorical_cols, train_val_split=train_val_split
    )
