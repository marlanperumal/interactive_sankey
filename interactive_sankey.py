import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from collections import defaultdict
import json
from textwrap import dedent as d
import pandas as pd

app = dash.Dash(__name__)

def sankey(periods, segments, movements, highlight_type=None, highlight_filter=None):
    nodes = {}
    label = []
    node_id = 0
    for period_id, period in enumerate(periods):
        for segment_id, segment in enumerate(segments[period]):
            nodes[(period_id, segment_id)] = node_id
            label.append(period + " " + segment)
            node_id += 1

    flows = defaultdict(int)
    if highlight_type == "node":
        h_period, h_segment = [h_node for h_node, h_node_id in nodes.items() if h_node_id == highlight_filter][0]
    for movement in movements:
        for period in range(len(periods)-1):
            from_segment = movement[period]
            to_segment = movement[period+1]
            from_node = nodes[(period, from_segment)]
            to_node = nodes[(period+1, to_segment)]
            if highlight_type == "node":
                filtered = movement[h_period] == h_segment
            else:
                filtered = False
            if filtered:
                flows[(from_node, to_node, True)] += movement[-1]
            else:
                flows[(from_node, to_node, False)] += movement[-1]
    source = [flow[0] for flow in sorted(flows)]
    target = [flow[1] for flow in sorted(flows)]
    value = [flows[flow] for flow in sorted(flows)]
    flow_color = [
        "rgba(255,0,0,0.8)" if flow[2] else "rgba(50,50,50,0.2)"
        for flow in sorted(flows)
    ]

    data = [{
        "type": "sankey",
        "node": {
            "pad": 15,
            "thickness": 20,
            "line": {
                "color": "black",
                "width": 0.5
            },
            "label": label,
            "color": ["blue" for l in label]
        },
        "link": {
            "source": source,
            "target": target,
            "value": value,
            "color": flow_color,
        },
    }]

    layout = {
        "title": "Period Sankey Diagram",
        "font": {
            "family": "Arial",
            "size": 10
        }
    }

    figure = {
        "data": data,
        "layout": layout
    }

    return figure

df = pd.read_csv("PN_voucher_redemption_201805201656.csv")

periods = list(df.columns)[:-1]

segments = {
    col: [str(x) for x in sorted(list(df[col].unique()))] for col in periods
}

movements = df.values.tolist()

app.layout = html.Div([
    dcc.Graph(
        id="sankey",
        hoverData={"points": [{}]}
    ),
])

@app.callback(
    Output('sankey', 'figure'),
    [Input('sankey', 'hoverData')])
def apply_sankey_highlight(hoverData):
    highlight_type = None
    highlight_filter = None
    if "originalLayerIndex" in hoverData["points"][0]:
        highlight_type = "node"
        highlight_filter = hoverData["points"][0]["pointNumber"]
    elif "originalIndex" in hoverData["points"][0]:
        highlight_type = "link"
        highlight_filter = hoverData["points"][0]["pointNumber"]
    return sankey(periods, segments, movements, highlight_type, highlight_filter)


if __name__ == "__main__":
    app.run_server(debug=True)
