import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import datetime as dt
from pytz import timezone
from dash.dependencies import Input, Output
import dash_table
from dash_table.Format import Format, Scheme
#from memory_profiler import profile 

from app import app
from apps.data import df_user_info, df_media_insights, df_user_insights_audience_city, \
    df_user_insights_audience_country, df_user_insights_audience_gender_age, df_media_info
from apps.functions import get_navbar, overview_topline_metrics_by_day, \
    overview_topline_metrics_hour_day_variances, overview_topline_metrics_audience_country_city_age, \
        overview_topline_metrics_audience_gender, TABLE_FONT_SIZE, TABLE_HEADER_FONT_SIZE


#pull most recent followers, media count etc
#put when the most recent data was generated
max_date = df_user_info["created_date"].max()

#get the figures for the top level metrics
followers_count = df_user_info.loc[(df_user_info["user_account"] == "nomadpursuit") & (df_user_info["created_date"] == max_date), "followers_count"].tolist()[0]
follows_count = df_user_info.loc[(df_user_info["user_account"] == "nomadpursuit") & (df_user_info["created_date"] == max_date), "follows_count"].tolist()[0]
media_count = df_user_info.loc[(df_user_info["user_account"] == "nomadpursuit") & (df_user_info["created_date"] == max_date), "media_count"].tolist()[0]


#create the dataframe to contain the daily metrics so select all data that was pulled at midday just for nomad pursuit
start_time = dt.time(11,50)
end_time = dt.time(12,10)

df_user_info_overview_daily = df_user_info.loc[(df_user_info["user_account"] == "nomadpursuit") & 
                        (df_user_info["created_date_time"] >= start_time) &
                        (df_user_info["created_date_time"] < end_time)].copy()

#get the weekday from the date in the daily table
df_user_info_overview_daily["created_date_weekday"] = df_user_info_overview_daily["created_date"].dt.weekday
df_user_info_overview_daily["created_date_weekday"] = df_user_info_overview_daily["created_date_weekday"].map({
    0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5:"Sat", 6: "Sun"}
    )

#now calculate the increase in followers each day
df_user_info_overview_daily.sort_values(by = "created_date", inplace = True)
df_user_info_overview_daily["followers_variance"] = df_user_info_overview_daily["followers_count"] - df_user_info_overview_daily["followers_count"].shift() 

#create the hourly table just for nomad pursuit
df_user_info_overview_hourly = df_user_info.loc[(df_user_info["user_account"] == "nomadpursuit")].copy()

#now calculate the the increase in followers every 2 hours
df_user_info_overview_hourly.sort_values(by = "created_date", inplace = True)
df_user_info_overview_hourly["followers_variance"] = df_user_info_overview_hourly["followers_count"] - df_user_info_overview_hourly["followers_count"].shift() 


#add on likes and comments to df media insights table
df_media_insights = df_media_insights.merge(df_media_info[["media_id", "created_date_date", "created_date_hour", "likes_count", "comments_count"]],
                                how = "left",
                                on = ["media_id", "created_date_date", "created_date_hour"])

#get the reach variance for the hourly graph
df_media_insights.sort_values(by = "created_date", inplace = True)
df_media_insights["reach_variance"] = df_media_insights["reach"] - df_media_insights.groupby("media_id")["reach"].shift()
df_media_insights["engagement_variance"] = df_media_insights["engagement"] - df_media_insights.groupby("media_id")["engagement"].shift()
df_media_insights["likes_variance"] = df_media_insights["likes_count"] - df_media_insights.groupby("media_id")["likes_count"].shift()
df_media_insights["comments_variance"] = df_media_insights["comments_count"] - df_media_insights.groupby("media_id")["comments_count"].shift()

df_media_insights_hourly = df_media_insights.groupby(["created_date", "created_date_date", "created_date_weekday", "created_date_hour"]).agg(reach = ("reach", "sum"),
                                                                                                                                            reach_variance = ("reach_variance", "sum"),
                                                                                                                                            engagement = ("engagement", "sum"),
                                                                                                                                            engagement_variance = ("engagement_variance", "sum"),
                                                                                                                                            likes = ("likes_count", "sum"),
                                                                                                                                            likes_variance = ("likes_variance", "sum"),
                                                                                                                                            comments = ("comments_count", "sum"),
                                                                                                                                            comments_variance = ("comments_variance", "sum")).reset_index()

df_media_insights_daily = df_media_insights_hourly.groupby(["created_date_date", "created_date_weekday"]).agg(reach = ("reach", "max"),
                                                                                                                reach_variance = ("reach_variance", "sum"),
                                                                                                                engagement = ("engagement", "max"),
                                                                                                                engagement_variance = ("engagement_variance", "sum"),
                                                                                                                likes = ("likes", "max"),
                                                                                                                likes_variance = ("likes_variance", "sum"),
                                                                                                                comments = ("comments", "max"),
                                                                                                                comments_variance = ("comments_variance", "sum"),
                                                                                                                created_date = ("created_date", "max")).reset_index()


#get the overall engagement, like and comment rate figure for the topline metrics

engagement_rate = df_media_insights_hourly.loc[(df_media_insights_hourly["created_date"] == df_media_insights_hourly["created_date"].max()), "engagement"].tolist()[0] / df_media_insights_hourly.loc[(df_media_insights_hourly["created_date"] == df_media_insights_hourly["created_date"].max()), "reach"].tolist()[0]
engagement_rate = "{:.1%}".format(engagement_rate)
like_rate = df_media_insights_hourly.loc[(df_media_insights_hourly["created_date"]== df_media_insights_hourly["created_date"].max()), "likes"].tolist()[0] / df_media_insights_hourly.loc[(df_media_insights_hourly["created_date"] == df_media_insights_hourly["created_date"].max()), "reach"].tolist()[0]
like_rate = "{:.1%}".format(like_rate)
comment_rate = df_media_insights_hourly.loc[(df_media_insights_hourly["created_date"]== df_media_insights_hourly["created_date"].max()), "comments"].tolist()[0] / df_media_insights_hourly.loc[(df_media_insights_hourly["created_date"] == df_media_insights_hourly["created_date"].max()), "reach"].tolist()[0]
comment_rate = "{:.1%}".format(comment_rate)


#add on followers, followers variance and posts
df_overview_table = df_media_insights_daily.merge(df_user_info_overview_daily[["created_date_date", "followers_count", "followers_variance", "media_count"]],
                        how = "left", on = "created_date_date")

df_overview_table["media_count_variance"] = df_overview_table["media_count"] - df_overview_table["media_count"].shift()

#add on week number and year
df_overview_table["created_date_week_number"] = df_overview_table["created_date"].dt.strftime("%V")
df_overview_table["created_date_year"] = df_overview_table["created_date"].dt.strftime("%Y")

#create a separate table to hold the week ending dates
df_week_ending = df_overview_table.groupby(["created_date_year", "created_date_week_number"]).agg(week_ending_date = ("created_date_date", "max"),
                                                                                                week_starting_date = ("created_date_date", "min")).reset_index()

#add week ending dates onto overview table
df_overview_table = df_overview_table.merge(df_week_ending, how = "left", on = ["created_date_year", "created_date_week_number"])

#calculate the weekly amounts for reach, engagement, likes etc.
df_overview_table = df_overview_table.groupby(["week_ending_date", "week_starting_date"]).agg(weekly_engagement = ("engagement_variance", "sum"),
                                                    weekly_likes = ("likes_variance", "sum"),
                                                    weekly_comments = ("comments_variance", "sum"),
                                                    weekly_reach = ("reach_variance", "sum"),
                                                    weekly_followers_gained = ("followers_variance", "sum"),
                                                    weekly_posts = ("media_count_variance", "sum"),
                                                    days_in_week = ("created_date_date", "nunique")).reset_index()

#add on the cumulative total of reach, likes, engagement and comments for the WEEK STARTING
df_overview_table = df_overview_table.merge(df_media_insights_daily[["created_date_date", "engagement", "likes", "comments", "reach"]],
                                            how = "left", left_on = "week_starting_date", right_on = "created_date_date")

df_overview_table.rename(columns = {"engagement": "total_ws_engagement", "likes": "total_ws_likes", "comments": "total_ws_comments", "reach": "total_ws_reach"}, inplace = True)

#add on the week ending total of followers
df_overview_table = df_overview_table.merge(df_user_info_overview_daily[["created_date_date", "followers_count"]],
                        how = "left", left_on = "week_ending_date", right_on = "created_date_date")

df_overview_table.drop(columns = ["created_date_date_x", "created_date_date_y"], inplace = True)

#calculate the growth rate for each of the metrics
df_overview_table["engagement_growth_%"] = df_overview_table["weekly_engagement"] / df_overview_table["total_ws_engagement"]
df_overview_table["likes_growth_%"] = df_overview_table["weekly_likes"] / df_overview_table["total_ws_likes"]
df_overview_table["comment_growth_%"] = df_overview_table["weekly_comments"] / df_overview_table["total_ws_comments"]
df_overview_table["reach_growth_%"] = df_overview_table["weekly_reach"] / df_overview_table["total_ws_reach"]
df_overview_table["followers_growth_%"] = df_overview_table["weekly_followers_gained"] / (df_overview_table["followers_count"] - df_overview_table["weekly_followers_gained"])

#want to drop any rows which aren't full weeks
df_overview_table.drop(index = df_overview_table.loc[(df_overview_table["week_ending_date"] + dt.timedelta(7)).shift(1) != df_overview_table["week_ending_date"]].index, inplace = True)

#only have the columns that will be shwon in the table
df_overview_table = df_overview_table[["week_ending_date", "followers_count", "weekly_followers_gained", "followers_growth_%",  
                    "weekly_posts",
                    "weekly_engagement", "engagement_growth_%", "weekly_likes", "likes_growth_%",
                    "weekly_comments", "comment_growth_%", "weekly_reach", "reach_growth_%", 
                    ]]

#create a variable containing the format of each column to be passed to the data table
column_format = [Format(), Format(), Format(), Format(precision = 1, scheme=Scheme.percentage),
                Format(), 
                Format(), Format(precision = 1, scheme=Scheme.percentage),
                Format(), Format(precision = 1, scheme=Scheme.percentage),
                Format(), Format(precision = 1, scheme=Scheme.percentage),
                Format(), Format(precision = 1, scheme=Scheme.percentage) ]

#create a variable containing the type of each column to be passed to the data table
column_type = ["numeric", "numeric", "numeric", "numeric", "numeric", "numeric", "numeric", 
                "numeric", "numeric", "numeric", "numeric", "numeric", "numeric" ]

df_overview_table = df_overview_table.loc[df_overview_table["week_ending_date"]>= dt.datetime.strptime("2021-07-25", "%Y-%m-%d").date()].copy()

#rename the columns so they appear as desired in the table
df_overview_table.rename(columns = {"week_ending_date": "WE Date", "followers_count": "Followers", "weekly_followers_gained": "Followers Gained",
                        "followers_growth_%": "Followers Growth %", "weekly_posts": "Net Posts", 
                        "weekly_engagement": "Engagement", "engagement_growth_%": "Engagement Growth %",
                        "weekly_likes": "Likes", "likes_growth_%": "Likes Growth %", 
                        "weekly_comments": "Comments", "comment_growth_%": "Comments Growth %", 
                        "weekly_reach": "Reach", "reach_growth_%": "Reach Growth %"}, inplace = True)

#reduce the size of dataframes that are being passed to the callback by removing columns that aren't used
df_user_info_overview_daily = df_user_info_overview_daily[["created_date_date", "followers_count", "created_date_weekday", "followers_variance"]].copy()
df_user_info_overview_hourly = df_user_info_overview_hourly[["created_date_date", "created_date_hour", "followers_variance"]].copy()
df_media_insights_daily = df_media_insights_daily[["created_date_date", "created_date_weekday", "reach_variance", "reach", "engagement", "likes", "comments"]].copy()
df_media_insights_hourly = df_media_insights_hourly[["created_date_date", "created_date_hour", "reach_variance"]].copy()
df_user_insights_audience_city = df_user_insights_audience_city[["created_date_date", "city", "follower_count"]].copy()
df_user_insights_audience_country = df_user_insights_audience_country[["created_date_date", "country_code", "follower_count"]].copy()
df_user_insights_audience_gender_age = df_user_insights_audience_gender_age[["created_date_date", "gender", "age_range", "follower_count"]].copy()


layout = dbc.Container([
    get_navbar("overview"),
    dbc.Container([      
        dbc.Row([dbc.Col(html.P("Headline Metrics", className = "p-title"))]),
        dbc.Row([
            dbc.Col(
                [html.Img(src = "assets/icons8-people-50-red.png", className = "image-center"),
                html.P(followers_count, className = "p-metric-value-overview"),
                html.P("Followers", className = "p-metric-title-overview")]
                , className = "col-2"
            ),
            dbc.Col(
                [html.Img(src = "assets/icons8-user-50-red.png", className = "image-center"),
                html.P(follows_count, className = "p-metric-value-overview"),
                html.P("Following", className = "p-metric-title-overview")]
                , className = "col-2"
            ),
            dbc.Col(
                [html.Img(src = "assets/icons8-camera-50-red.png", className = "image-center"),
                html.P(media_count, className = "p-metric-value-overview"),
                html.P("Media Count", className = "p-metric-title-overview")]
                , className = "col-2"
            ),
            dbc.Col(
                [html.Img(src = "assets/icons8-topic-50-engagement-red.png", className = "image-center"),
                html.P(engagement_rate, className = "p-metric-value-overview"),
                html.P("Engagement Rate", className = "p-metric-title-overview")]
                , className = "col-2"
            ),
            dbc.Col(
                [html.Img(src = "assets/icons8-heart-50-red.png", className = "image-center"),
                html.P(like_rate, className = "p-metric-value-overview"),
                html.P("Like Rate", className = "p-metric-title-overview")]
                , className = "col-2"
            ),
            dbc.Col(
                [html.Img(src = "assets/icons8-topic-50-red.png", className = "image-center"),
                html.P(comment_rate, className = "p-metric-value-overview"),
                html.P("Comment Rate", className = "p-metric-title-overview")]
                , className = "col-2"
            ),
        ]),
    ], className = "container-box"),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.P("Select Time Period:", className = "p-metric-title"),
                dcc.DatePickerRange(id = "overview-date-range",
                                    start_date = (df_user_info["created_date_date"].max() - dt.timedelta(13)).strftime("%Y-%m-%d"),
                                    end_date = df_user_info["created_date_date"].max().strftime("%Y-%m-%d"),
                                    display_format = "DD-MM-YYYY",
                                    min_date_allowed = "2021-07-28",
                                    max_date_allowed = df_user_info["created_date_date"].max(),
                                    initial_visible_month = (df_user_info["created_date_date"].max() - dt.timedelta(13)).strftime("%Y-%m-%d"),
                                    )
            ])
        ]),
    ], className = "container-box", style = {"width": "33%", "margin-left": "0%"}),
    dbc.Container([
        dbc.Row([dbc.Col(html.P("Key Metrics Overview", className = "p-title"))]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id = "daily-followers-count-graph",
                            config = {"displayModeBar": False}), className = "col-4"
            ),
            dbc.Col(
                dcc.Graph(id = "followers-variance-weekday-graph",
                            config = {"displayModeBar": False}), className = "col-4"
            ),
            dbc.Col(
                dcc.Graph(id = "followers-variance-hour-graph",
                            config = {"displayModeBar": False}), className = "col-4"
            )
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id = "daily-reach-graph", 
                            config = {"displayModeBar": False}), className = "col-4"
            ),
            dbc.Col(
                dcc.Graph(id = "average-reach-weekday-graph", 
                            config = {"displayModeBar": False}), className = "col-4"
            ),
            dbc.Col(
                dcc.Graph(id = "average-reach-hour-graph", 
                            config = {"displayModeBar": False}), className = "col-4"
            )
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id = "daily-engagement-rate-graph",
                            config = {"displayModeBar": False}), className = "col-4"
            ),
            dbc.Col(
                dcc.Graph(id = "daily-like-rate-graph",
                            config = {"displayModeBar": False}), className = "col-4"
            ),
            dbc.Col(
                dcc.Graph(id = "daily-comment-rate-graph",
                            config = {"displayModeBar": False}), className = "col-4"
            )

        ]),
    ], className = "container-box"),
    dbc.Container([
        dbc.Row([dbc.Col(html.P("Audience Overview", className = "p-title"))]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id = "audience-city-graph", 
                            config = {"displayModeBar": False}), className = "col-6"
            ),
            dbc.Col(
                dcc.Graph(id = "audience-country-graph", 
                            config = {"displayModeBar": False}), className = "col-6"
            )

        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id = "audience-age-range-graph", 
                            config = {"displayModeBar": False}), className = "col-6"
            ),
            dbc.Col(
                dcc.Graph(id = "audience-gender-graph", 
                            config = {"displayModeBar": False}), className = "col-6"
            )

        ])
    ], className = "container-box"),
    
    dbc.Container([
        dbc.Row([dbc.Col(html.P("Weekly Performance", className = "p-title"))]),
        dbc.Row([
            dbc.Col(dash_table.DataTable(id = "text-hashtag-table",
                                        columns = [{"name": i, "id": i, "format": j, "type": k} for i, j, k in zip(df_overview_table.columns, column_format, column_type)],
                                        data = df_overview_table.to_dict("records"),
                                        style_as_list_view = True,
                                        style_table={'height': '300px', 'overflowY': 'auto'},
                                        #filter_action="native",
                                        sort_action="native",
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
                                                'width': '100px',
                                                'maxWidth': '100px',
                                                'minWidth': '100px',
                                            },
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': 'WE Date'},
                                                'width': '150px'
                                            },
                                            {
                                                'if': {'column_id': 'Engagement'},
                                                'width': '150px'
                                            },
                                            {
                                                'if': {'column_id': 'Engagement Growth %'},
                                                'width': '150px'
                                            },
                                            {
                                                'if': {'column_id': 'Posts'},
                                                'width': '40px'
                                            },
                                        ],

                                        ))
        ])
    ], className = "container-box")
])



@app.callback([Output("daily-followers-count-graph", "figure"),
                Output("followers-variance-weekday-graph", "figure"),
                Output("followers-variance-hour-graph", "figure"),
                Output("daily-reach-graph", "figure"),
                Output("average-reach-weekday-graph", "figure"),
                Output("average-reach-hour-graph", "figure"),
                Output("daily-engagement-rate-graph", "figure"),
                Output("daily-like-rate-graph", "figure"),
                Output("daily-comment-rate-graph", "figure"),
                Output("audience-city-graph", "figure"),
                Output("audience-country-graph", "figure"),
                Output("audience-age-range-graph", "figure"),
                Output("audience-gender-graph", "figure")],
                [Input("overview-date-range", "start_date"),
                Input("overview-date-range", "end_date")])

def create_overview_page_content(startdate, enddate):

    #create key metrics overview graphs
    daily_followers_fig = overview_topline_metrics_by_day(df_user_info_overview_daily, "followers_count", startdate, enddate)
    followers_variance_weekday_fig = overview_topline_metrics_hour_day_variances(df_user_info_overview_daily, "created_date_weekday", "followers_variance", startdate, enddate)
    followers_variance_hour_fig = overview_topline_metrics_hour_day_variances(df_user_info_overview_hourly, "created_date_hour", "followers_variance", startdate, enddate)

    daily_reach_fig = overview_topline_metrics_by_day(df_media_insights_daily, "reach_variance", startdate, enddate)
    average_reach_weekday_fig = overview_topline_metrics_hour_day_variances(df_media_insights_daily, "created_date_weekday", "reach_variance", startdate, enddate)
    average_reach_hour_fig = overview_topline_metrics_hour_day_variances(df_media_insights_hourly, "created_date_hour", "reach_variance", startdate, enddate)

    daily_engagement_rate_fig = overview_topline_metrics_by_day(df_media_insights_daily, "engagement_rate", startdate, enddate)
    daily_like_rate_fig = overview_topline_metrics_by_day(df_media_insights_daily, "like_rate", startdate, enddate)
    daily_comment_rate_fig = overview_topline_metrics_by_day(df_media_insights_daily, "comment_rate", startdate, enddate)

    audience_city_fig = overview_topline_metrics_audience_country_city_age(df_user_insights_audience_city, "city", enddate)
    audience_country_fig = overview_topline_metrics_audience_country_city_age(df_user_insights_audience_country, "country_code", enddate)
    audience_age_range_fig = overview_topline_metrics_audience_country_city_age(df_user_insights_audience_gender_age, "age_range", enddate)
    audience_gender_fig = overview_topline_metrics_audience_gender(df_user_insights_audience_gender_age, enddate)


    return daily_followers_fig, followers_variance_weekday_fig, \
    followers_variance_hour_fig, daily_reach_fig, average_reach_weekday_fig, average_reach_hour_fig, \
    daily_engagement_rate_fig, daily_like_rate_fig, daily_comment_rate_fig, audience_city_fig, \
    audience_country_fig, audience_age_range_fig, audience_gender_fig




