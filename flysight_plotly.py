import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import webbrowser

VECTORS = {# "Time Elapsed (s)": "time_elapsed",
    "Velocity-Horizontal": "velH",
    "Velocity-Vertical": "velD",
    "Velocity-Total": "velT",
    "Altitude (MSL)": "hMSL",
    "Glide Ratio": "gr",
    }
# TO-DO: Add dictionary lookup for line-colors & column
VECTOR_AXES = {
    "Velocity-Horizontal": "y1",
    "Velocity-Vertical": "y1",
    "Velocity-Total": "y1",
    "Altitude (MSL)": "y2",
    "Ground Elevation (MSL)": "y2",
    "Glide Ratio": "y3",
    }
WINDOW_PARAMS = {
    "height": 600,
    "width": 1200,
    "y1min": 0,
    "y1max": 100,
    "y2min": 0,
    "y2max": 100,
    }


def launch_browser(url="127.0.0.1:8050", browser="chrome"):
    """Launches web browser to the localhost or a provided URL.
    :param url: str: Default to 127.0.0.1:8050 for Plotly Dash
    :param browser: str: Default to "chrome" """
    browser_paths = {
        "chrome": "C://Program Files (x86)//Google//Chrome//Application//chrome.exe",
        "explorer": "C://Program Files (x86)//Internet Explorer//iexplore.exe",
        "firefox": "C://Program Files//Mozilla Firefox//firefox.exe"
    }
    webbrowser.register(
        browser,
        None,
        webbrowser.BackgroundBrowser(browser_paths[browser])
    )
    webbrowser.get("chrome").open(url)


def make_plotly(df, options: dict):
    """Proof of concept to generate a single plotly graph"""
    fig = go.Figure()
    x1 = df['time_elapsed']
    y1 = df['hMSL']
    fig.add_trace(go.Scatter(x=x1, y=y1,
                             line_color='rgb(0, 176, 246)',
                             name='Premium',
                             )
                  )
    # Fill/Surrounding error bars
    # fig.add_trace(go.Scatter(x=x1, y=y1,
    #                          fill='toself',
    #                          fillcolor='rgba(0, 176, 246, 0.2)',
    #                          line_color='rgba(255, 255, 255, 0)',
    #                          name='Premium',
    #                          showlegend=False,
    #                          )
    #               )
    fig.update_traces(mode="lines")
    fig.show()


def make_dash(flight_track):
    """Proof of concept to generate Dash application with plots
    :param flight_track: FlysightTrack"""
    df = flight_track.df
    options = flight_track.options
    x1 = df['time_elapsed']
    title = options.get('track_title')
    if options.get('elev_bool'):
        VECTORS["Ground Elevation (MSL)"] = "ground_elev"

    dashapp = Dash(__name__)
    dashapp.layout = html.Div([
        html.H4(title,),
        dcc.Graph(id="flysight_graph",
                  # figure=fig,
                  ),
        html.P("Toggle lines On/Off by clicking labels in the Legend above",),
        dcc.Dropdown(
            id="dropdown",
            options=list(VECTORS.keys()),
            value=list(VECTORS.keys()),
            multi=True,
        ),
    ])

    launch_browser()

    @dashapp.callback(
        Output("flysight_graph", "figure"),
        Input("dropdown", "value"),
    )
    def update_line_chart(vectors):
        fig = go.Figure()
        for vector in vectors:
            vector_col = VECTORS.get(vector)
            # Reference: https://plotly.com/python/multiple-axes/
            if vector_col:
                fig.add_trace(go.Scatter(
                    x=x1,
                    y=df[vector_col],
                    name=vector,
                    yaxis=VECTOR_AXES.get(vector),
                    fill={"ground_elev": "tozerox"}.get(vector_col),
                ))
        fig.update_traces(mode="lines")
        fig.update_layout(
            autosize=False,
            plot_bgcolor="rgb(255,255,255)",
            height=WINDOW_PARAMS["height"],
            width=WINDOW_PARAMS["width"],
            hovermode="x unified",
            xaxis={
                "title": "Time Elapsed (s)",
                "domain": [0, 0.9],  # Set range within window taken up by x-axis
                "showline": True,
                "linecolor": "black",
                "showgrid": False,
            },
            yaxis={
                "title": "Velocity (units)",
                "showline": True,
                "linecolor": "black",
                "mirror": True,
                "rangemode": "nonnegative",
                "showgrid": False,
                # "ticksuffix": "m/s",
                "ticks": "outside",
                "zeroline": True,
            },
            yaxis2={
                "title": "Elevation, MSL (units)",
                "anchor": "free",
                "overlaying": "y",
                "side": "right",
                "position": .94,  # Place axis 90% down x-axis
                "showgrid": False,
                "ticks": "outside",
                "ticksuffix": "m",
                "showline": True,
                "linecolor": "black"
            },
            yaxis3={
                # "title": "Glide Ratio",
                "range": [0, 4],
                "nticks": 5,
                "ticks": "outside",
                "ticksuffix": ":1",
                "anchor": "x",
                "overlaying": "y",
                "side": "right",
                "showgrid": False,
                "zeroline": False,
                "showline": True,
                "linecolor": "black",
            },
            legend={
                # "bordercolor": "black",
                # "borderwidth": 1,
                "orientation": "h",
                "xanchor": "center",
                "x": 0.5,
                "yanchor": "top",
                "y": -0.1

            },
        )
        return fig

    # TO-DO: Look into maybe avoiding multiple flask server instances running simultaneously (Tk & this)
    dashapp.run(debug=True, use_reloader=False)


# 1. build series, for each vector, for traces
# 	- Actual X
# 	- Reverse X
# 	- Actual Y
# 	- Upper Y (wrapper)
# 	- Lower Y (in reverse-X order) (wrapper)
# 2. create figure fig=go.Figure()
# 3. Add Traces:
# 	fig.add_trace(go.Scatter(
# 		x=
# 		y=
# 		line_color=
# 		name=
# 		showlegend=Bool,
# 		// OPTIONAL FOR SOLID FILL/WRAPPER AROUND LINE
# 		fill=
# 		fillcolor=
# 		))
# 4. fig.update_traces(mode='lines')
# 5. fig.show()
