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
        tools="",
        x_axis_label='time', y_axis_label='polarity',
        x_axis_type='datetime'
    )

    # Format background colors:
    low_box = bokeh.models.BoxAnnotation(top=0, fill_alpha=0.1, fill_color='red')
    high_box = bokeh.models.BoxAnnotation(bottom=0, fill_alpha=0.1, fill_color='green')
    p.add_layout(low_box)
    p.add_layout(high_box)

    # Format gridlines:
    p.xgrid[0].grid_line_color = None
    p.ygrid[0].grid_line_alpha = 0.5

    # Format view range:
    p.y_range = bokeh.models.Range1d(-1.0, 1.0)

    # p.sizing_mode = "stretch_both"

    # Prepare data:
    cd_source = bokeh.models.ColumnDataSource({'timestamp': df.index, 'polarity': df[polarity_column]})

    # Prepare plotting series:
    p.line('timestamp', 'polarity', source=cd_source, line_width=2)
    p.circle('timestamp', 'polarity', source=cd_source, fill_color="white", size=2)

    # Prepare hover tooltips:
    p.add_tools(bokeh.models.HoverTool(
        tooltips=[
            ('time', '@timestamp{%F %H:%M}'),
            ("polarity", "@polarity{+0.00}")
        ],
        formatters={'timestamp': 'datetime', 'polarity': 'numeral'},
        mode='vline'
    ))

    return p
