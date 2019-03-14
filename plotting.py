import datetime

import bokeh.plotting
import bokeh.models


def plot_polarity_vs_time(df, polarity_column='polarity'):
    """
    Prepare a Bokeh timeseries plot: tweet polarity versus time (hours).
    Expects df to have a datetime index and a polarity column.

    :param df: Source dataframe
    :return: Bokeh figure
    """

    p = bokeh.plotting.figure(
        plot_width=800, plot_height=450,
        sizing_mode='scale_width',
        tools='xpan,xwheel_zoom',
        x_axis_label='Time (UTC)', y_axis_label='Mean Hourly Sentiment',
        x_axis_type='datetime'
    )

    # Format background colors:
    low_box = bokeh.models.BoxAnnotation(top=0.5, fill_alpha=0.1, fill_color='red')
    high_box = bokeh.models.BoxAnnotation(bottom=0.5, fill_alpha=0.1, fill_color='green')
    p.add_layout(low_box)
    p.add_layout(high_box)

    # Format gridlines:
    p.xgrid[0].grid_line_color = None
    p.ygrid[0].grid_line_alpha = 0.5

    # Format the time axis:
    p.xaxis.formatter = bokeh.models.DatetimeTickFormatter(hours=['%m/%d %H:%M'])

    # Format view range:
    # TODO: Allow users to select time range.
    now = datetime.datetime.now()
    p.x_range = bokeh.models.Range1d(now - datetime.timedelta(days=3), now + datetime.timedelta(hours=6))
    p.y_range = bokeh.models.Range1d(0.0, 1.0)

    # p.sizing_mode = "stretch_both"

    # Prepare data:
    cd_source = bokeh.models.ColumnDataSource({'timestamp': df.index, 'sentiment': df[polarity_column]})

    # Prepare plotting series:
    p.line('timestamp', 'sentiment', source=cd_source, line_width=2)
    p.circle('timestamp', 'sentiment', source=cd_source, fill_color="white", size=2)

    # Prepare hover tooltips:
    p.add_tools(bokeh.models.HoverTool(
        tooltips=[
            ('time', '@timestamp{%F %H:%M}'),
            ("sentiment", "@sentiment{+0.00}")
        ],
        formatters={'timestamp': 'datetime', 'sentiment': 'numeral'},
        mode='vline'
    ))

    return p


def build_plot_scores(df, values_column):
    """
    Prepare a Bokeh timeseries plot: mean tweet scores versus time (hours).
    Expects df to have a datetime index.

    :param df: Source dataframe
    :param values_column: Column from which to extract values
    :return: Bokeh figure
    """

    p = bokeh.plotting.figure(
        plot_width=800, plot_height=450,
        sizing_mode='scale_width',
        tools='xpan,xwheel_zoom',
        x_axis_label='Time (UTC)', y_axis_label='Mean Tweet Scores',
        x_axis_type='datetime'
    )

    # Format background colors:
    # low_box = bokeh.models.BoxAnnotation(top=0.5, fill_alpha=0.1, fill_color='red')
    # high_box = bokeh.models.BoxAnnotation(bottom=0.5, fill_alpha=0.1, fill_color='green')
    # p.add_layout(low_box)
    # p.add_layout(high_box)

    # Format gridlines:
    p.xgrid[0].grid_line_color = None
    p.ygrid[0].grid_line_alpha = 0.5

    # Format the time axis:
    p.xaxis.formatter = bokeh.models.DatetimeTickFormatter(hours=['%m/%d %H:%M'])

    # Format view range:
    # TODO: Allow users to select time range.
    now = datetime.datetime.now()
    p.x_range = bokeh.models.Range1d(now - datetime.timedelta(days=3), now + datetime.timedelta(hours=6))
    # p.y_range = bokeh.models.Range1d(0.0, 1.0)

    # Prepare data:
    cd_source = bokeh.models.ColumnDataSource({'timestamp': df.index, 'values': df[values_column]})

    # Prepare plotting series:
    p.line('timestamp', 'values', source=cd_source, line_width=2)
    p.circle('timestamp', 'values', source=cd_source, fill_color="white", size=2)

    # Prepare hover tooltips:
    p.add_tools(bokeh.models.HoverTool(
        tooltips=[
            ('time', '@timestamp{%F %H:%M}'),
            ("mean score", "@values{+0.00}")
        ],
        formatters={'timestamp': 'datetime', 'values': 'numeral'},
        mode='vline'
    ))

    return p
