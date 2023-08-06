import plotly.express as px
import plotly.graph_objects as go

from teaspoon import TSP


def simple_timeseries(tsp: TSP):

    chart = px.line(tsp.long,
               x = 'time',
               y = 'temperature_in_ground',
               line_group = 'depth')

    return chart
