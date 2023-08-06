import calendar
from datetime import timedelta
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# TODO: check https://github.com/gisle/isoweek to make this dynamic
WEEKS_IN_A_YEAR = 52


def calculate_continuous_week(frame: pd.DataFrame) -> pd.Series:
    """
    Calculate the number of week starting from the first week available
    :param frame: A data frame containing a 'year' and 'week' columns
    :return: A pandas series with the continuous week number
    """
    min_year = frame["year"].min()
    min_week = frame[frame["year"] == min_year]["week"].min()

    year_week = (frame["year"] - min_year) * WEEKS_IN_A_YEAR

    return frame["week"] + year_week - min_week + 1


def hubify(time_series: pd.Series, plot_title: Union[str, None] = None):
    """
    Create a GitHub like plot of your time series data.

    :param time_series: A pandas series of type `datetime64` with the timestamps for the events to plot
    :param plot_title: The title of the plot
    """
    # Data transformation
    day_by_day = time_series.dt.floor("d")
    grouped = day_by_day.groupby(day_by_day).count()
    grouped = grouped.rename_axis("date").rename("events").reset_index()
    grouped["weekday"] = grouped["date"].dt.weekday
    grouped["week"] = grouped["date"].dt.week
    grouped["year"] = grouped["date"].dt.year

    # TODO: not all years have 52 weeks
    grouped["continuous_week"] = calculate_continuous_week(grouped)

    # Generate a heatmap from the time series data
    heatmap = np.full((7, grouped["continuous_week"].max() + 1), np.nan)

    for _, row in grouped.iterrows():
        heatmap[row["weekday"]][row["continuous_week"]] = row["events"]

    # Plot the timestamp
    fig = plt.figure(figsize=(20, 5))
    ax = plt.subplot()
    sns.heatmap(
        heatmap,
        ax=ax,
        cbar=False,
        linecolor="white",
        cmap="Greens",
        square=True,
        linewidth=2,
    )

    # Change Y labels
    y_labels = ["Mon", "", "Wed", "", "Fri", "", "Sun"]
    ax.set_yticklabels(y_labels, rotation=0)

    # Get the monday for the first week of the graph
    min_date = grouped["date"].min()
    first_monday = min_date - timedelta(min_date.weekday())
    all_mondays = [first_monday + timedelta(weeks=wk) for wk in range(grouped["continuous_week"].max() + 1)]
    x_labels = [calendar.month_abbr[monday.month] for monday in all_mondays]
    true_x_labels = []
    current_x_label = ""
    for x_label in x_labels:
        if current_x_label != x_label:
            true_x_labels.append(x_label)
            current_x_label = x_label
        else:
            true_x_labels.append("")
    if current_x_label != x_label:
        true_x_labels.append(x_label)
    ax.set_xticklabels(true_x_labels)

    # Set more plot details
    if plot_title:
        ax.set_title(plot_title, fontsize=20, pad=40)
    ax.xaxis.tick_top()
    ax.set_facecolor("#ebedf0")
    ax.tick_params(axis="both", which="both", length=0)

    plt.show()
