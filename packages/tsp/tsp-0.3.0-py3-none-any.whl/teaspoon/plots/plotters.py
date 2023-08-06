import plotly.express as px
import plotly.graph_objects as go
from teaspoon import TSP


# # plotly


if __name__ == "__main__":
    z = TSP.synthetic(depths=[1,2,5,10])

    fig = go.Figure()

    chart = px.line(z.long,
                    x = 'time',
                    y = 'temperature_in_ground',
                    line_group = 'depth')
    chart.show()