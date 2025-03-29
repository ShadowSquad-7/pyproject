#ЭТО ТЕСТОВЫЕ ДАННЫЕ
from dash import dcc, html, Dash
import plotly.graph_objs as go

dash_app = Dash(__name__)

dash_app.layout = html.Div([
    html.H1("всратый график для теста нормальный делайте сами"),
    dcc.Graph(figure=go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])]))
])

if __name__ == "__main__":
    dash_app.run(host="127.0.0.1", port=8050, debug=True)

