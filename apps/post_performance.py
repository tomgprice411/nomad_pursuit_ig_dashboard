import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


from apps.data import df_media_insights, df_media_images
from app import app
from apps.functions import post_performance_hours_live, get_navbar


RADIO_OPTIONS = ["First 24 Hours", "First 7 Days", "All Time"]

layout = dbc.Container([
    get_navbar(""),
    dcc.Location(id = "url-post-performance", refresh = False),

    dbc.Container([dbc.Row([dbc.Col(html.A(html.H5("Back", className = "p-no-margins"), href = "/media-posts"), className = "col-4 back-button-col")], className = "back-button-row")], className = "back-button-container"),
    dbc.Row([
        dbc.Col([
            dbc.Container([
                html.Img(id = "post-performance-media-image", height = "300px", className = "image-center"),
                dbc.Row([
                    dbc.Col(className = "col-1 no-gutters-2"),
                    dbc.Col([
                        #list out all the titles for the metrics that I want to show, these will be left aligned on the card
                        html.P("Upload date:", className = "post-performance-metric-title col-left"),
                        html.P("Upload day:", className = "post-performance-metric-title col-left"),
                        html.P("Upload time:", className = "post-performance-metric-title col-left"),
                        html.P("Impressions:", className = "post-performance-metric-title col-left"),
                        html.P("Reach:", className = "post-performance-metric-title col-left"),
                        html.P("Engagement:", className = "post-performance-metric-title col-left"),
                        html.P("Likes:", className = "post-performance-metric-title col-left"),
                        html.P("Comments:", className = "post-performance-metric-title col-left"),
                        html.P("Saves:", className = "post-performance-metric-title col-left")
                    ], className = "col-6 no-gutters-2"),
                    dbc.Col([
                        #list out all the values for the metrics that I want to show, these will be right aligned on the card
                        html.P(id = "post-performance-media-upload-date", className = "post-performance-metric-title col-right"),
                        html.P(id = "post-performance-media-upload-weekday", className = "post-performance-metric-title col-right"),
                        html.P(id = "post-performance-media-upload-time", className = "post-performance-metric-title col-right"),
                        html.P(id = "post-performance-media-impressions", className = "post-performance-metric-value col-right"),
                        html.P(id = "post-performance-media-reach", className = "post-performance-metric-value col-right"),
                        html.P(id = "post-performance-media-engagement", className = "post-performance-metric-value col-right"),
                        html.P(id = "post-performance-media-likes", className = "post-performance-metric-value col-right"),
                        html.P(id = "post-performance-media-comments", className = "post-performance-metric-value col-right"),
                        html.P(id = "post-performance-media-saves", className = "post-performance-metric-value col-right")
                    ], className = "col-4 no-gutters-2"),
                    dbc.Col(className = "col-1 no-gutters-2")
                ])

            ], className = "container-box")
        ], className = "col-4"),


        dbc.Col(
            dbc.Container([
                html.P("Caption:", className = "post-performance-text",
                        style = {"font-weight": "bold"}),
                html.P(id = "post-performance-media-caption", className = "post-performance-text"),
                html.P(""),
                html.P("Hastags:", className = "post-performance-text",
                        style = {"font-weight": "bold"}),
                html.P(id = "post-performance-media-hashtags", className = "post-performance-text"), 
            ], className = "container-box"),
        className = "col-8"),
    ]),
    html.Hr(className = "media-post-divider"),
    dbc.Row([
        dbc.Col(
            dbc.Container([
                html.P("Select Time Period:", className = "p-metric-title"),
                    dbc.RadioItems(id = "radio-id",
                                    options = [{"label": i, "value": i} for i in RADIO_OPTIONS],
                                    value = "First 24 Hours",
                                    inline = True,
                                    labelClassName = "radio-button-label",
                                    labelCheckedClassName = "radio-button-checked",)
            ], className = "container-box", style = {"width": "33%", "margin-left": "0"})
        )
    ]),
    dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Graph(id = "post-performance-engagement-graph",
                                config = {"displayModeBar": False}), className = "col-6"),
            dbc.Col(dcc.Graph(id = "post-performance-reach-graph",
                                config = {"displayModeBar": False}), className = "col-6")
        ])
    ], className = "container-box")
])

@app.callback([Output("post-performance-media-image", "src"),
                Output("post-performance-media-caption", "children"),
                Output("post-performance-media-upload-date", "children"),
                Output("post-performance-media-upload-weekday", "children"),
                Output("post-performance-media-upload-time", "children"),
                Output("post-performance-media-impressions", "children"),
                Output("post-performance-media-reach", "children"),
                Output("post-performance-media-engagement", "children"),
                Output("post-performance-media-likes", "children"),
                Output("post-performance-media-comments", "children"),
                Output("post-performance-media-saves", "children"),
                Output("post-performance-media-hashtags", "children"),
                Output("post-performance-reach-graph", "figure"),
                Output("post-performance-engagement-graph", "figure")],
                [Input("url-post-performance", "search"),
                Input("radio-id", "value")])

def create_page_content_post_performance(id, time_period):

    MEDIA_ID = int(id.split("=")[1])

    #create new dataframe containing only selected image
    df_selected_image = df_media_images.loc[df_media_images["media_id"] == MEDIA_ID].copy()

    caption = df_selected_image["caption"].tolist()[0].split("#")[0]

    try:
        hashtag = df_selected_image["caption"].tolist()[0].split("#", 1)[1]
        hashtag = "#" + hashtag
    except:
        hashtag = "Hashtags not available (either not used or entered in comments)"

    
    cropped_im = df_selected_image["cropped_image"].tolist()[0]
    upload_date = "{}".format(df_selected_image["timestamp_date"].tolist()[0])
    upload_time = "{}".format(df_selected_image["timestamp_time"].tolist()[0])

    impressions = "{:,.0f}".format(df_selected_image["impressions"].tolist()[0])
    reach = "{:,.0f}".format(df_selected_image["reach"].tolist()[0])
    engagement = "{:,.0f}".format(df_selected_image["engagement"].tolist()[0])

    likes = "{:,.0f}".format(df_selected_image["likes_count"].tolist()[0])
    comments = "{:,.0f}".format(df_selected_image["comments_count"].tolist()[0])
    saves = "{:,.0f}".format(df_selected_image["saved"].tolist()[0])

    upload_weekday = "{}".format(df_selected_image["timestamp_weekday"].tolist()[0])

    #create variable for number of hours live
    df_media_insights_2 = df_media_insights.loc[df_media_insights["media_id"] == MEDIA_ID].copy()

    reach_hours_live = post_performance_hours_live(df_media_insights_2, "reach", df_media_insights, time_period)
    engagement_hours_live = post_performance_hours_live(df_media_insights_2, "engagement", df_media_insights, time_period)


    return cropped_im, caption, upload_date, upload_weekday, upload_time, impressions, reach, engagement, \
        likes, comments, saves, hashtag, reach_hours_live, engagement_hours_live




