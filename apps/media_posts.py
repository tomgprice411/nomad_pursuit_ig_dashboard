
import dash_html_components as html
import dash_bootstrap_components as dbc


from app import app
from apps.data import df_media_info, df_media_insights, df_media_images
from apps.functions import get_navbar, MAX_DATETIME, MAX_DATETIME_DATE, MAX_DATETIME_HOUR, create_media_post_cards



df_media_images.sort_values(by = "timestamp", ascending = False, inplace = True)

layout = dbc.Container([
    get_navbar("media-posts"),

    dbc.Row([
        create_media_post_cards(df_media_images, 0),
        create_media_post_cards(df_media_images, 1),
        create_media_post_cards(df_media_images, 2)
    ]),
    
    html.Hr(className = "media-post-divider"),
    dbc.Row([
        create_media_post_cards(df_media_images, 3),
        create_media_post_cards(df_media_images, 4),
        create_media_post_cards(df_media_images, 5)
    ]),
    html.Hr(className = "media-post-divider"),
    
], className = "no-gutters-2")

