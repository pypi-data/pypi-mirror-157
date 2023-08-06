import adopt_pytorch.config as config
import logging
import numpy as np
import pandas as pd
from typing import List, Union
from matplotlib.axes._axes import Axes
from matplotlib import pyplot as plt

from adopt_pytorch.feature_ranking import identify_start_end_threshold


if 'debug' in config.log['visualization'].lower():
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('visualization')

FIGSIZE = config.FIGSIZE
PLOT_FACE = config.PLOT_FACE
GRID = config.GRID
N_COLUMNS = config.N_COLUMNS
LABEL_SIZE = config.LABEL_SIZE


def plot_precursor_scores(precursor_scores_dict: dict,
                          parameters_list: list,
                          sorted_precursor_params_list: list = None,
                          score_list: list = None,
                          standard_deviation_scale: List[int] = None,
                          thresold: float = 0.5,
                          flight_data: pd.DataFrame = None,
                          filename: str = None, dpi: int = 300):

    if standard_deviation_scale is None:
        standard_deviation_scale = config.standard_deviation_scale

    n_features = len(parameters_list)
    n_rows = 1 if n_features < N_COLUMNS else int(np.ceil((n_features + 1) / N_COLUMNS))

    fig, axes = plt.subplots(n_rows, N_COLUMNS,
                             figsize=(N_COLUMNS * FIGSIZE[0], FIGSIZE[1] * int(n_features / N_COLUMNS + 1)))
    y_label = 'Precursor Score'
    x_label = 'Time'

    current_row = -1
    current_column = 0
    for current_subplot_idx in range(n_features + 1):
        if (current_subplot_idx % N_COLUMNS) == 0:
            current_row += 1
        current_column = current_subplot_idx % N_COLUMNS

        ax = axes[current_row, current_column]
        if current_subplot_idx == 0:
            title = 'Original Precursor Score'
        else:
            title = parameters_list[current_subplot_idx - 1] if sorted_precursor_params_list is\
                    None else sorted_precursor_params_list[current_subplot_idx - 1]
        title_plot = f"{title} ({score_list[current_subplot_idx - 1]} % diff)" \
                     if (score_list is not None) and (current_subplot_idx > 0) else title

        data = precursor_scores_dict['original_score'].flatten()

        ax.plot(data, c='r', label='Original')
        if current_subplot_idx > 0:
            logger.debug(f'Plotting {title}')
            data_up = precursor_scores_dict[title]['upper'].flatten()
            data_low = precursor_scores_dict[title]['lower'].flatten()
            ax.plot(data_up,  label=f"{standard_deviation_scale[0]} σ", c='b')
            ax.plot(data_low, label=f"{standard_deviation_scale[1]} σ", c='g')
            if flight_data is not None:
                ax2 = ax.twinx()
                ax2.plot(flight_data[title].values, label='Feature Values', c='k', ls='dashed')
                ax2 = axis_setup(ax2, y_label='Feature Value')

        start_idx, end_idx = identify_start_end_threshold(data, thresold)
        for start, end in zip(*[start_idx, end_idx]):
            ax.axvspan(start, end,
                       alpha=0.25,
                       color='gray')

        ax = axis_setup(ax,
                        title=title_plot,
                        y_label=y_label,
                        x_label=x_label,
                        legend=True)

    fig.tight_layout(pad=0.95)

    if filename is not None:
        fig.save(filename, dpi=dpi)


def axis_setup(ax: Axes, title: str = None,
               y_label: str = None, x_label: str = None,
               tick_axis: str = 'both',
               which_tick_axis: str = 'major',
               legend: Union[bool, str] = None):

    ax.set_facecolor(PLOT_FACE)
    ax.grid(GRID)
    if y_label is not None:
        ax.set_ylabel(y_label, fontsize=LABEL_SIZE)
    if x_label is not None:
        ax.set_xlabel(x_label, fontsize=LABEL_SIZE)
    ax.tick_params(axis=tick_axis, which=which_tick_axis, labelsize=LABEL_SIZE)
    if title is not None:
        ax.set_title(title)
    if isinstance(legend, bool):
        ax.legend()
    elif isinstance(legend, str):
        ax.legend(legend)

    return ax
