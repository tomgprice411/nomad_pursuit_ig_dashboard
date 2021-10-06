import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash_table.Format import Format, Scheme

# from nltk.stem.snowball import SnowballStemmer

from apps.data import df_media_info, df_stopwords
from app import app
from apps.functions import get_navbar, clean_text, TABLE_HEADER_FONT_SIZE, TABLE_FONT_SIZE


#get the maximum date for each media
df_max_posting_date = df_media_info.groupby("media_id").agg(max_date = ("created_date", "max")).reset_index()

#use the the max date for each media to get a table of the most recent captions and hashtags for each media
df_captions_hashtags = df_media_info.merge(df_max_posting_date, how = "inner", left_on = ["media_id", "created_date"], right_on = ["media_id", "max_date"])


#separate hashtags and captions out into separate columns
df_captions_hashtags["hashtags"] = df_captions_hashtags["caption"].str.split("#", 1, expand = True)[1]
df_captions_hashtags["caption"] = df_captions_hashtags["caption"].str.split("#", 1, expand = True)[0]
df_captions_hashtags["hashtags"] = "#" + df_captions_hashtags["hashtags"]

#now create a new dataframe for the hashtags where each hashtag for each media will appear in it's own row
df_captions_hashtags["hashtags"] = df_captions_hashtags["hashtags"].str.split(" ")
df_hashtags = df_captions_hashtags.explode("hashtags")
df_hashtags["hashtags"] = df_hashtags["hashtags"].str.replace("\n", "")

df_hashtags = df_hashtags[["media_id", "comments_count", "likes_count", "created_date", "created_date_date", "hashtags"]].copy()
df_hashtags.dropna(inplace = True)
df_hashtags.drop_duplicates(inplace = True)

#create final hashtag table
df_hashtags = df_hashtags.groupby(["hashtags"]).agg(appearances = ("media_id", "nunique"),
                                        average_likes = ("likes_count", "mean"),
                                        average_comments = ("comments_count", "mean")).reset_index()

#remove hashtags only used once
df_hashtags = df_hashtags.loc[(df_hashtags["appearances"] > 2) & (df_hashtags["hashtags"] != "")].copy()


#now create a new dataframe for the caption where each word for each media will appear in it's own row
df_captions_hashtags["caption"] = df_captions_hashtags["caption"].str.split(" ")
df_caption = df_captions_hashtags.explode("caption")
df_caption["caption"] = df_caption["caption"].str.replace("\n", "")

df_caption = df_caption[["media_id", "comments_count", "likes_count", "created_date", "created_date_date", "caption"]].copy()
df_caption.drop_duplicates(inplace = True)

#create stop word list
stop_words = set(df_stopwords["stopwords"])

#convert all words to lower case
df_caption["caption"] = df_caption["caption"].str.lower()

#remove the stop words from the words
df_caption = df_caption.loc[~(df_caption["caption"].isin(stop_words))].copy()

#create a new column with the clean words in
df_caption["caption_clean"] = df_caption["caption"].map(lambda x: clean_text(x))

#remove the stop words from the cleaned words
df_caption = df_caption.loc[~(df_caption["caption_clean"].isin(stop_words))].copy()

#create final caption table
df_caption = df_caption.groupby(["caption_clean"]).agg(appearances = ("media_id", "nunique"),
                                        average_likes = ("likes_count", "mean"),
                                        average_comments = ("comments_count", "mean")).reset_index()

#remove caption used twice or less and any blank captions
df_caption = df_caption.loc[(df_caption["appearances"] > 2) & (df_caption["caption_clean"] != "")].copy()

#####################################################################
##### MOVE TEXT ANALYTICS BITS TO THE API CALL FILE (SOME ABOVE BITS) #####
#####################################################################

#rename the columns and label the type and format for each column
hashtags_column_format = [Format(), Format(),
                Format(precision = 0, scheme=Scheme.decimal_integer), 
                Format(precision = 0, scheme=Scheme.decimal_integer)]

hashtags_column_type = ["text", "numeric", "numeric", "numeric"]

df_hashtags.rename(columns = {"hashtags": "Hashtags", "appearances": "Post Appearances", 
                        "average_likes": "Average Likes",
                        "average_comments": "Average Comments"}, inplace = True)

df_hashtags.sort_values(by = "Average Likes", ascending = False, inplace = True)

caption_column_format = [Format(), Format(),
                Format(precision = 0, scheme=Scheme.decimal_integer), 
                Format(precision = 0, scheme=Scheme.decimal_integer)]

caption_column_type = ["text", "numeric", "numeric", "numeric"]

df_caption.rename(columns = {"caption_clean_stem": "Caption Word", "appearances": "Post Appearances", 
                        "average_likes": "Average Likes",
                        "average_comments": "Average Comments"}, inplace = True)

df_caption.sort_values(by = "Average Likes", ascending = False, inplace = True)

layout = dbc.Container([
    get_navbar("text-analysis"),
    dbc.Container([
        dbc.Row([
            dbc.Col(html.P("Caption Analysis", className = "p-title")),
        ]),
        dbc.Row([
            dbc.Col(dash_table.DataTable(id = "text-caption-table",
                                        columns = [{"name": i, "id": i, "format": j, "type": k} for i, j, k in zip(df_caption.columns, caption_column_format, caption_column_type)],
                                        data = df_caption.to_dict("records"),
                                        style_as_list_view = True,
                                        style_table={'height': '300px', 'overflowY': 'auto'},
                                        filter_action="native",
                                        sort_action="native",
                                        fill_width = False,
                                        fixed_rows = { "headers":True},
                                        style_cell = {"textAlign": "left",
                                        'height': 'auto',
                                        'whiteSpace': 'normal',
                                        'padding': '0.5rem',
                                        "font-family": "Raleway",
                                        "border-top": "0px",
                                        "border-bottom": "0px",
                                        "color": "#616A6B"},
                                        style_data_conditional=[
                                            {
                                                'if': {'row_index': 'even'},
                                                'backgroundColor': '#F2F3F4'
                                            },
                                            ],
                                        style_header = {
                                                'fontSize': TABLE_HEADER_FONT_SIZE,
                                                "fontWeight": "400",
                                                "marginBottom": "1.5rem",
                                                'backgroundColor': 'white'
                                            },
                                        style_data = {
                                                'fontSize': TABLE_FONT_SIZE,
                                                'width': '200px',
                                                'maxWidth': '200px',
                                                'minWidth': '200px',
                                            },
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': 'Caption Words'},
                                                'width': '300px',
                                                'maxWidth': '300px',
                                                'minWidth': '300px',
                                            },
                                        ],
                                        ))
        ]),
    ], className = "container-box"),
    dbc.Container([
        dbc.Row([
            dbc.Col(html.P("Hashtags Analysis", className = "p-title"))
        ]),
        dbc.Row([
            dbc.Col(dash_table.DataTable(id = "text-hashtag-table",
                                        columns = [{"name": i, "id": i, "format": j, "type": k} for i, j, k in zip(df_hashtags.columns, hashtags_column_format, hashtags_column_type)],
                                        data = df_hashtags.to_dict("records"),
                                        style_as_list_view = True,
                                        style_table={'height': '300px', 'overflowY': 'auto'},
                                        filter_action="native",
                                        sort_action="native",
                                        fill_width = False,
                                        fixed_rows = { "headers": True},
                                        style_cell = {"textAlign": "left",
                                        'height': 'auto',
                                        'whiteSpace': 'normal',
                                        'padding': '0.5rem',
                                        "font-family": "Raleway",
                                        "border-top": "0px",
                                        "border-bottom": "0px",
                                        "color": "#616A6B"},
                                        style_data_conditional=[
                                            {
                                                'if': {'row_index': 'even'},
                                                'backgroundColor': '#F2F3F4'
                                            },
                                            ],
                                        style_header = {
                                                'fontSize': TABLE_HEADER_FONT_SIZE,
                                                "fontWeight": "400",
                                                "marginBottom": "1.5rem",
                                                'backgroundColor': 'white'
                                            },
                                        style_data = {
                                                'fontSize': TABLE_FONT_SIZE,
                                                'width': '200px',
                                                'maxWidth': '200px',
                                                'minWidth': '200px',
                                            },
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': 'Hashtags'},
                                                'width': '300px',
                                                'maxWidth': '300px',
                                                'minWidth': '300px',
                                            },
                                        ],
                                        ))
        ])
    ], className = "container-box")
    ])

