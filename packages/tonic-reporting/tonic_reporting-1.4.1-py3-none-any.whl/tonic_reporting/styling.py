class Colors:
    REAL = "mediumpurple"
    SYNTH = "mediumturquoise"
    ALPHA = 0.5


class PlotsSizes:
    DEFAULT_WIDTH = 6
    DEFAULT_HEIGHT = 4
    TWO_COLUMNS = (12, 4)


class Labels:
    REAL = "Real"
    SYNTH = "Synth"


class FontSizes:
    DEFAULT = 14
    LARGE = 16


def format_stats_data(df):
    format_kwargs = {col: "{:.2%}" for col in df.columns if "p-value" in col}
    return df.style.format(format_kwargs)
