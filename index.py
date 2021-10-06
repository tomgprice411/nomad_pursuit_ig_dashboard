import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from apps import overview, media_posts, post_performance, competitors, text
from app import server



header = dbc.Container([
    dbc.Row([
        dbc.Col(dcc.Link(html.Img(src = "assets/nomadpursuit3.png"), href = "https://www.instagram.com/nomadpursuit/"), className = "col-4"),
        dbc.Col(html.H1("Instagram Performance"), className = "col-6 col-center"),
        dbc.Col(html.P(), className = "col-2")
    ], className = "col-center")
])


#create the page layout using the previously created sidebar
app.layout = html.Div([
    dcc.Location(id = "url", refresh = False),
    header,
    html.Div(id = "page-content")
])

#callback to load the correct page content
@app.callback(Output("page-content", "children"),
                Input("url", "pathname"))
def create_page_content(pathname):
    if pathname == "/overview":
        return overview.layout
    elif pathname == "/media-posts":
        return media_posts.layout
    elif pathname == "/competitors":
        return competitors.layout
    elif pathname == "/post-performance":
        return post_performance.layout
    elif pathname == "/text-analysis":
        return text.layout
    else:
        return overview.layout


if __name__ == "__main__":
    app.run_server(debug = False)


