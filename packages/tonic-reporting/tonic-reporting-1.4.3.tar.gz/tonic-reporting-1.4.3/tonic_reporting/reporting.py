from IPython.display import Markdown, display

from tonic_reporting.univariate import plot_all_marginals
from tonic_reporting.multivariate import plot_correlations
from tonic_reporting.privacy import plot_dcr


def plot_simple_report(
    source_df, synth_df, numeric_cols, categorical_cols, is_events=False
):
    if len(numeric_cols) > 0:
        display(Markdown("## Numeric Columns"))
        plot_all_marginals(source_df, synth_df, numeric_cols, [])
    if len(categorical_cols) > 0:
        display(Markdown("## Categorical Columns"))
        plot_all_marginals(source_df, synth_df, [], categorical_cols)
    display(Markdown("## Numeric Correlations"))
    plot_correlations(
        source_df,
        synth_df,
        numeric_cols,
    )
    if is_events:
        pass
    else:
        display(Markdown("## Privacy: Distance-to-closest record"))
        plot_dcr(source_df, synth_df, numeric_cols, categorical_cols)
