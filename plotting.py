import bokeh.plotting


def plot_polarity_vs_time(df):
    """
    Prepare a Bokeh timeseries plot: tweet polarity versus time (hours).
    Expects df to have a datetime index and a polarity column.

    :param df: Source dataframe
    :return: Bokeh figure
    """

    fig = bokeh.plotting.figure(plot_width=600, plot_height=400)
    fig.xaxis.axis_label = 'hour'
    fig.yaxis.axis_label = 'polarity'
    fig.line(x=df.index.values, y=df['polarity'].values)

    return fig


def plot_polarity_vs_subjectivity(df):
    """
    Prepare a Bokeh scatter plot: tweet polarity versus subjectivity.
    Expects df to have polarity and subjectivity columns.

    :param df: Source dataframe
    :return: Bokeh figure
    """

    fig = bokeh.plotting.figure(plot_width=600, plot_height=400)
    fig.xaxis.axis_label = 'subjectivity'
    fig.yaxis.axis_label = 'polarity'
    fig.circle(x=df['subjectivity'].values, y=df['polarity'].values, size=5)

    return fig
