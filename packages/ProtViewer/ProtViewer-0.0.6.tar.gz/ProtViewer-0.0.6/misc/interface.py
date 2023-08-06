import base64
import json

import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go


app = dash.Dash(__name__)


@app.callback(
    Output("mol-view", "figure"),
    Input("upload-json", "contents"),
)
def visualize(content=None):
    mol = {
        "nodes": [],
        "edges": {
            "start": [],
            "end": [],
        }
    }
    if content is not None:
        _, content = content.split(",")
        decoded = base64.b64decode(content)
        mol = json.loads(decoded)
    colors = [255 * n['activity'] for n in mol['nodes']]
    acids = go.Scatter3d(
        x=[n['x'] for n in mol['nodes']],
        y=[n['y'] for n in mol['nodes']],
        z=[n['z'] for n in mol['nodes']],
        mode='markers',
        marker={
            'symbol': 'circle',
            'size': 20,
            'color': [f'rgb({c},0,0)' for c in colors],
        },
        text=[f"{n['name']}" for n in mol['nodes']],
        hoverinfo='text',
    )
    X, Y, Z = [], [], []
    for s, t in zip(mol['edges']['start'], mol['edges']['end']):
        if s < t:
            X += [mol['nodes'][s]["x"], mol['nodes'][t]["x"]]
            Y += [mol['nodes'][s]["y"], mol['nodes'][t]["y"]]
            Z += [mol['nodes'][s]["z"], mol['nodes'][t]["z"]]
    edges = go.Scatter3d(
        x=X,
        y=Y,
        z=Z,
        mode='lines',
        line={
            'color': 'rgb(0,0,0)',
            'width': 5,
        },
        hoverinfo='none',
    )
    axis = {
        'showbackground': False,
        'zeroline': False,
        'showgrid': False,
        'showticklabels': False,
        'showspikes': False,
        'title': '',
    }
    layout = go.Layout(
        title="Protein",
        width=1000,
        height=1000,
        showlegend=False,
        scene={
            'xaxis': axis,
            'yaxis': axis,
            'zaxis': axis,
        },
        margin={
            't': 100,
        },
        hovermode='closest',
        annotations=[],
    )
    return go.Figure(data=[edges, acids], layout=layout)


app.layout = html.Div(children=[
    html.H1(children="Protein Activity Prediction Visualizer"),
    html.Div(children=[
        html.H2(children="Input JSON with coordinates and activities"),
        dcc.Upload(
            id="upload-json",
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '95%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
        )
    ]),
    html.Div(children=[
        html.H2(children="Interactive Molecule Activity View"),
        dcc.Graph(id="mol-view"),
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True)
