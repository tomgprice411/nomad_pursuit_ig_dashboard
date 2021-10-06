import datetime as dt
import math
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import math
import re


from apps.data import df_media_info, df_country_codes

#####################
## Graph Variables ##
#####################

PLOT_BGCOLOR = "white"
FONT_COLOR_TEXT = "rgb(166, 166, 166)"
FONT_SIZE_TEXT = 9
FONT_COLOR_TITLE = "rgb(102, 102, 102)"
FONT_SIZE_TITLE = 18
FONT_SIZE_LEGEND_SUBTITLE = 12
FONT_SIZE_TITLE_ROW_3 = 14

#alignment of axes and title
X_ALIGNMENT_X_AXIS_TITLE_ROW_3 = -0.1

MARKER_COLOR_TY = "#532C63"
MARKER_COLOR_LY = "rgb(189, 195, 199)"
MARKER_COLOR_BM = "rgb(106, 117, 124)"


MARKER_COLOR_HIGH = "#1C699C"
MARKER_COLOR_MEDIUM = "#B86114"
MARKER_COLOR_LOW = "#F4CF3E"
MARKER_COLOR_EXTRA_LOW = "#C82A19"

GRAPH_HEIGHT_ROW_3 = 320
GRAPH_HEIGHT_ROW_2 = 370
GRAPH_HEIGHT_ROW_3_HEATMAP = 300

GRAPH_MARGINS = {'l' : 55, 'r' : 60, 't' : 40, 'b' : 40}
GRAPH_MARGINS_ROW_3 = {'l' : 50, 'r' : 5, 't' : 40, 'b' : 40}
GRAPH_MARGINS_HEATMAP = {'l' : 40, 'r' : 50, 't' : 35, 'b' : 35}

#####################
## Other Variables ##
#####################

MAX_DATETIME = df_media_info["created_date"].max()
MAX_DATETIME_DATE = df_media_info["created_date"].dt.date.max()
MAX_DATETIME_HOUR = MAX_DATETIME.hour

TABLE_FONT_SIZE = "0.875rem"
TABLE_HEADER_FONT_SIZE = "0.875rem"


##############################
## Overview Graph Functions ##
##############################

#create a navbar for each page so that nav highlights the current page that is selected

def get_navbar(page_name = "overview"):
    if page_name == "overview":
        navbar = dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Link(html.H5("Overview"), href = "/overview", className = "active-link"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Media Posts"), href = "/media-posts"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Competitors"), href = "/competitors"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Text Analysis"), href = "/text-analysis"), className = "navbar-col")
                ], className = "navbar-row",)
            ], className = "navbar-container no-gutters-2")
    elif page_name == "media-posts":
        navbar = dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Link(html.H5("Overview"), href = "/overview"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Media Posts"), href = "/media-posts", className = "active-link"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Competitors"), href = "/competitors"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Text Analysis"), href = "/text-analysis"), className = "navbar-col")
                ], className = "navbar-row",)
            ], className = "navbar-container no-gutters-2")
    elif page_name == "competitors":
        navbar = dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Link(html.H5("Overview"), href = "/overview"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Media Posts"), href = "/media-posts"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Competitors"), href = "/competitors", className = "active-link"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Text Analysis"), href = "/text-analysis"), className = "navbar-col")
                ], className = "navbar-row",)
            ], className = "navbar-container no-gutters-2")
    elif page_name == "text-analysis":
        navbar = dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Link(html.H5("Overview"), href = "/overview"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Media Posts"), href = "/media-posts"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Competitors"), href = "/competitors"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Text Analysis"), href = "/text-analysis", className = "active-link"), className = "navbar-col")
                ], className = "navbar-row",)
            ], className = "navbar-container no-gutters-2")

    elif page_name == "":
        navbar = dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Link(html.H5("Overview"), href = "/overview"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Media Posts"), href = "/media-posts"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Competitors"), href = "/competitors"), className = "navbar-col"),
                    dbc.Col(dcc.Link(html.H5("Text Analysis"), href = "/text-analysis"), className = "navbar-col")
                ], className = "navbar-row",)
            ], className = "navbar-container no-gutters-2")
    return navbar

##############################
## Overview Graph Functions ##
##############################

def overview_topline_metrics_by_day(df, metric, start_date, end_date):

    #filter dataframe so that only dates that are selected are included
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    df = df.loc[df["created_date_date"].between(start_date, end_date)].copy()

    
    #create the graph variables specific to each metric
    if metric == "followers_count":
        HOVER_TEXT = "Date: %{x}<br>Followers: %{y}<extra></extra>"
        Y_AXIS_TITLE = "FOLLOWERS"
        Y_TICKFORMAT = ","
        TITLE = "Daily Followers"
        Y_AXIS_TITLE_X_POS = -0.13
        TITLE_X_POS = -0.125
    elif metric == "reach_variance":
        HOVER_TEXT = "Date: %{x}<br>Reach: %{y}<extra></extra>"
        Y_AXIS_TITLE = "REACH"
        Y_TICKFORMAT = ","
        TITLE = "Daily Reach"
        Y_AXIS_TITLE_X_POS = -0.14
        TITLE_X_POS = -0.135
    elif metric == "engagement_rate":
        df["engagement_rate"] = df["engagement"] / df["reach"]
        HOVER_TEXT = "Date: %{x}<br>Engagement Rate: %{y:.1%}<extra></extra>"
        Y_AXIS_TITLE = "ENGAGEMENT RATE"
        Y_TICKFORMAT = ".1%"
        TITLE = "Daily Engagement Rate"
        Y_AXIS_TITLE_X_POS = -0.16
        TITLE_X_POS = -0.16

    elif metric == "like_rate":
        df["like_rate"] = df["likes"] / df["reach"]
        HOVER_TEXT = "Date: %{x}<br>Like Rate: %{y:.1%}<extra></extra>"
        Y_AXIS_TITLE = "LIKE RATE"
        Y_TICKFORMAT = ".1%"
        TITLE = "Daily Like Rate"
        Y_AXIS_TITLE_X_POS = -0.16
        TITLE_X_POS = -0.16
    elif metric == "comment_rate":
        df["comment_rate"] = df["comments"] / df["reach"]
        HOVER_TEXT = "Date: %{x}<br>Comment Rate: %{y:.2%}<extra></extra>"
        Y_AXIS_TITLE = "COMMENT RATE"
        Y_TICKFORMAT = ".2%"
        TITLE = "Daily Comment Rate"
        Y_AXIS_TITLE_X_POS = -0.16
        TITLE_X_POS = -0.16

    fig = go.Figure()

    fig.add_trace(go.Scattergl(x = df["created_date_date"], y = df[metric],
                            mode = "lines",
                            marker = dict(color = MARKER_COLOR_EXTRA_LOW),
                            hovertemplate = HOVER_TEXT))

    fig.update_layout(plot_bgcolor = PLOT_BGCOLOR,
                        paper_bgcolor = PLOT_BGCOLOR,
                        xaxis = dict(linecolor = PLOT_BGCOLOR, gridcolor = PLOT_BGCOLOR, tickformat = "%d-%b"),
                        yaxis = dict(linecolor = PLOT_BGCOLOR, gridcolor = PLOT_BGCOLOR, tickformat = Y_TICKFORMAT),
                        font = dict(color = FONT_COLOR_TEXT, size = FONT_SIZE_TEXT),
                        margin = GRAPH_MARGINS_ROW_3,
                        height = GRAPH_HEIGHT_ROW_3
                        )
    #title
    fig.add_annotation(text = TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = TITLE_X_POS,
                        y = 1.12,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_TITLE_ROW_3, color = FONT_COLOR_TITLE))

    #y-axis title
    fig.add_annotation(text = Y_AXIS_TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = Y_AXIS_TITLE_X_POS,
                        y = 1.03,
                        # y = 0,
                        showarrow = False,
                        textangle= -90,
                        align = "right",
                        
                        yanchor = "top",
                        font = dict(size = FONT_SIZE_TEXT, color = FONT_COLOR_TEXT))

    #x-axis title
    fig.add_annotation(text = "DATE",
                        xref = "paper",
                        yref = "paper",
                        x = -0.015,
                        y = -0.13,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_TEXT, color = FONT_COLOR_TEXT))

    #show what the average daily growth rate is on the graph
    if metric == "followers_count":
        start_followers = df.loc[df["created_date_date"] == df["created_date_date"].min(), metric].tolist()[0]
        end_followers = df.loc[df["created_date_date"] == df["created_date_date"].max(), metric].tolist()[0]
        number_of_days = (df["created_date_date"].max() - df["created_date_date"].min()).days
        number_of_days += 1
        growth_rate = (end_followers - start_followers) / number_of_days
        growth_rate_text = "AVG DAILY FOLLOWER VARIANCE: {:.1f}".format(growth_rate)

        fig.add_annotation(text = growth_rate_text,
                        xref = "paper",
                        yref = "paper",
                        x = 1,
                        y = 0.1,
                        showarrow = False,
                        align = "right",
                        xanchor = "right",
                        font = dict(size = FONT_SIZE_TEXT, color = MARKER_COLOR_TY))

    return fig




def overview_topline_metrics_hour_day_variances(df, time_period, metric, start_date, end_date):

    #filter the dataframe so that only dates that are selected are included
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    df = df.loc[df["created_date_date"].between(start_date, end_date)].copy()


    if time_period == "created_date_weekday" and metric == "followers_variance":
        TITLE = "Avg Followers Variance by Day of Week"
        X_AXIS_TITLE = "DAY OF WEEK"
        Y_AXIS_TITLE = "AVERAGE FOLLOWERS VARIANCE"
        Y_TICKFORMAT = ",."
        HOVER_TEXT = "Day of Week: %{x}<br>Followers Variance: %{y:.1f}<extra></extra>"
        CATEGORY_ARRAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        Y_AXIS_TITLE_X_POS = -0.09
        TITLE_X_POS = -0.085
        DTICK = 1
    elif time_period == "created_date_hour" and metric == "followers_variance":
        TITLE = "Avg Followers Variance by Hour"
        X_AXIS_TITLE = "HOUR"
        Y_AXIS_TITLE = "AVERAGE FOLLOWERS VARIANCE"
        Y_TICKFORMAT = ",."
        HOVER_TEXT = "Hour: %{x}<br>Followers Variance: %{y:.1f}<extra></extra>"
        Y_AXIS_TITLE_X_POS = -0.11
        TITLE_X_POS = -0.105
        CATEGORY_ARRAY = ["12AM", "1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", 
                        "8AM", "9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM",
                        "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM", "11PM"]
        DTICK = 3
    elif time_period == "created_date_weekday" and metric == "reach_variance":
        TITLE = "Avg Reach by Day of Week"
        X_AXIS_TITLE = "DAY OF WEEK"
        Y_AXIS_TITLE = "AVERAGE REACH"
        Y_TICKFORMAT = ",."
        HOVER_TEXT = "Day of Week: %{x}<br>Average Reach: %{y:.1f}<extra></extra>"
        CATEGORY_ARRAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        Y_AXIS_TITLE_X_POS = -0.12
        TITLE_X_POS = -0.115
        DTICK = 1
    elif time_period == "created_date_hour" and metric == "reach_variance":
        TITLE = "Avg Reach by Hour"
        X_AXIS_TITLE = "HOUR"
        Y_AXIS_TITLE = "AVERAGE REACH"
        Y_TICKFORMAT = ",."
        HOVER_TEXT = "Hour: %{x}<br>Average Reach: %{y:.1f}<extra></extra>"
        Y_AXIS_TITLE_X_POS = -0.1
        TITLE_X_POS = -0.095
        CATEGORY_ARRAY = ["12AM", "1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", 
                        "8AM", "9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM",
                        "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM", "11PM"]
        DTICK = 3

    if metric == "followers_variance":
        df_new = df.groupby(time_period).agg(followers_variance = (metric, "mean")).reset_index()
    elif metric == "reach_variance":
        df_new = df.groupby(time_period).agg(reach_variance = (metric, "mean")).reset_index()

    if time_period == "created_date_hour":
        df_new[time_period] = df_new[time_period].map({0: "12AM", 1: "1AM", 2: "2AM", 3: "3AM", 4: "4AM", 5:"5AM", 6: "6AM",
                                                            7: "7AM", 8: "8AM", 9: "9AM", 10: "10AM", 11: "11AM", 12:"12PM", 13: "1PM",
                                                            14: "2PM", 15: "3PM", 16: "4PM", 17: "5PM", 18: "6PM", 19:"7PM", 20: "8PM",
                                                            21: "9PM", 22: "10PM", 23:"11PM",})
    

    fig = go.Figure()

    fig.add_trace(go.Bar(x = df_new[time_period], y = df_new[metric],
                            marker = dict(color = MARKER_COLOR_TY),
                            hovertemplate = HOVER_TEXT))

    fig.update_layout(plot_bgcolor = PLOT_BGCOLOR,
                        paper_bgcolor = PLOT_BGCOLOR,
                        xaxis = dict(linecolor = PLOT_BGCOLOR, gridcolor = PLOT_BGCOLOR, 
                                    categoryarray = CATEGORY_ARRAY, dtick = DTICK
                                    ),
                        yaxis = dict(linecolor = PLOT_BGCOLOR, gridcolor = PLOT_BGCOLOR, tickformat = Y_TICKFORMAT),
                        font = dict(color = FONT_COLOR_TEXT, size = FONT_SIZE_TEXT),
                        margin = GRAPH_MARGINS_ROW_3,
                        height = GRAPH_HEIGHT_ROW_3
                        )

    fig.add_annotation(text = TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = TITLE_X_POS,
                        y = 1.12,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_TITLE_ROW_3, color = FONT_COLOR_TITLE))

    fig.add_annotation(text = Y_AXIS_TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = Y_AXIS_TITLE_X_POS,
                        y = 1.03,
                        showarrow = False,
                        textangle= -90,
                        align = "right",
                        xanchor = "left",
                        yanchor = "top",
                        font = dict(size = FONT_SIZE_TEXT, color = FONT_COLOR_TEXT))

    fig.add_annotation(text = X_AXIS_TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = -0.015,
                        y = -0.13,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_TEXT, color = FONT_COLOR_TEXT))

    return fig


def overview_topline_metrics_audience_country_city_age(df, metric, end_date):

    #filter the dataframe so that only dates that are selected are included
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    df = df.loc[df["created_date_date"] == end_date-dt.timedelta(1)].copy()

    #calculate graph variables specific to the metric selected
    if metric == "city":
        TITLE = "Followers % Split by City - Top 10"
        HOVER_TEXT = "% of Followers: %{x:.1%}<br>City: %{y}<extra></extra>"
        CATEGORYARRAY = None
        LABELS_Y_AXIS = 0.003
    elif metric == "country_code":
        TITLE = "Followers % Split by Country - Top 10"
        df = df.merge(df_country_codes[["Country", "CountryCode"]], how = "left", left_on = "country_code", right_on = "CountryCode")
        metric = "Country"
        HOVER_TEXT = "% of Followers: %{x:.1%}<br>Country: %{y}<extra></extra>"
        CATEGORYARRAY = None
        LABELS_Y_AXIS = 0.01
    elif metric == "age_range":
        TITLE = "Followers % Split by Age Range"
        df = df.groupby("age_range").agg(follower_count = ("follower_count", "sum")).reset_index()
        HOVER_TEXT = "% of Followers: %{x:.1%}<br>Age Range: %{y}<extra></extra>"
        CATEGORYARRAY = ["65+", "55-64", "45-54", "35-44", "25-34", "18-24", "13-17"]
        LABELS_Y_AXIS = 0.01


    #get the percentage of follower count
    df["follower_count_perc"] = df["follower_count"] / df["follower_count"].sum()

    df["label"] = df["follower_count_perc"].mul(100).round(1).astype(str) + "%"
    df.sort_values(by = "follower_count_perc", ascending = True, inplace = True)
    df = df.tail(10)

    fig = go.Figure()

    fig.add_trace(go.Bar(x = df["follower_count_perc"], y = df[metric],
                        orientation = "h",
                        marker = dict(color = MARKER_COLOR_TY),
                        hovertemplate = HOVER_TEXT))

    fig.update_layout(plot_bgcolor = PLOT_BGCOLOR,
                        paper_bgcolor = PLOT_BGCOLOR,
                        xaxis = dict(linecolor = PLOT_BGCOLOR, gridcolor = PLOT_BGCOLOR,
                                    tickformat = ".1%", visible = False),
                        yaxis = dict(linecolor = PLOT_BGCOLOR, gridcolor = PLOT_BGCOLOR, categoryarray = CATEGORYARRAY),
                        font = dict(color = FONT_COLOR_TEXT, size = FONT_SIZE_TEXT),
                        margin = GRAPH_MARGINS,
                        height = GRAPH_HEIGHT_ROW_3
                        )

    fig.add_annotation(text = TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = 0,
                        y = 1.1,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_TITLE_ROW_3, color = FONT_COLOR_TITLE))

    #loop over each of the values within the selected metric (city or country) and label each bar
    for i in df[metric]:
        df_annotation = df.loc[df[metric] == i].copy()
        fig.add_annotation(text = "<b>{}</b>".format(df_annotation["label"].tolist()[0]),
                            xref = "x",
                            yref = "y",
                            x = df_annotation["follower_count_perc"].tolist()[0] + LABELS_Y_AXIS,
                            y = df_annotation[metric].tolist()[0],
                            showarrow = False,
                            align = "left",
                            xanchor = "left",
                            font = dict(size = 10))


    return fig



def overview_topline_metrics_audience_gender(df, end_date):

    #filter the dataframe so that only dates that are selected are included
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()

    #only included male and females
    df = df.loc[(df["gender"].isin(["F","M"]))].groupby("gender").agg(follower_count = ("follower_count", "sum")).reset_index()
    
    #get the percentage of follower count
    df["follower_count_perc"] = df["follower_count"] / df["follower_count"].sum()

    #set the colors for the pie chart
    df["color"] = MARKER_COLOR_TY
    df.loc[df["gender"] == "M", "color"] = MARKER_COLOR_EXTRA_LOW

    #change the genders to male and female
    df["gender"] = df["gender"].map({"M": "Male", "F": "Female"})

    fig = go.Figure()

    fig.add_trace(go.Pie(values = df["follower_count_perc"], labels = df["gender"],
                        marker = dict(colors = df["color"]),
                        textinfo = "label+percent",
                        hovertemplate = 
                        "Gender: %{label}<br>" +
                        "Follower Split: %{percent}<extra></extra>"))

    fig.update_layout(showlegend = False,
                        font = dict(color = PLOT_BGCOLOR),
                        margin = {'l' : 60, 'r' : 60, 't' : 60, 'b' : 60},
                        height = GRAPH_HEIGHT_ROW_3)

    #title
    fig.add_annotation(text = "Followers % Split by Gender",
                        xref = "paper",
                        yref = "paper",
                        x = 0.5,
                        y = 1.23,
                        showarrow = False,
                        align = "center",
                        xanchor = "center",
                        font = dict(size = FONT_SIZE_TITLE_ROW_3, color = FONT_COLOR_TITLE))

    return fig


###########################
## Media Posts Functions ##
###########################

def create_media_post_cards(df, number):
    return dbc.Col([
                dbc.Container([
                    dcc.Link(html.Img(src = df["cropped_image"].tolist()[number], height = "300px", className = "image-center"), 
                                        id = "{}".format(df["media_id"].tolist()[number]), href = "/post-performance?media-id={}".format(df["media_id"].tolist()[number])),
                    dbc.Row([
                        dbc.Col(html.P(""), className = "col-1 no-gutters-2"),
                        dbc.Col(html.P("Click image for post performance", className = "post-performance-metric-title col-left", style = {"font-weight": "bold"}), className = "col-10 no-gutters-2"),
                        dbc.Col(html.P(""), className = "col-1 no-gutters-2")
                    ], style = {"margin-bottom": "6px"}),
                    dbc.Row([
                        dbc.Col(className = "col-1 no-gutters-2"),
                        dbc.Col([
                            #list out all of the metrics that I want to be displayed under the post image
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
                            html.P("{}".format(df["timestamp_date"].tolist()[number]), className = "post-performance-metric-title col-right"),
                            html.P("{}".format(df["timestamp_weekday"].tolist()[number]), className = "post-performance-metric-title col-right"),
                            html.P("{}".format(df["timestamp_time"].tolist()[number]), className = "post-performance-metric-title col-right"),
                            html.P("{:,.0f}".format(df["impressions"].tolist()[number]), className = "post-performance-metric-value col-right"),
                            html.P("{:,.0f}".format(df["reach"].tolist()[number]), className = "post-performance-metric-value col-right"),
                            html.P("{:,.0f}".format(df["engagement"].tolist()[number]), className = "post-performance-metric-value col-right"),
                            html.P("{:,.0f}".format(df["likes_count"].tolist()[number]), className = "post-performance-metric-value col-right"),
                            html.P("{:,.0f}".format(df["comments_count"].tolist()[number]), className = "post-performance-metric-value col-right"),
                            html.P("{:,.0f}".format(df["saved"].tolist()[number]), className = "post-performance-metric-value col-right")
                        ], className = "col-4 no-gutters-2"),
                        dbc.Col(className = "col-1 no-gutters-2")
                    ])
                ], className = "container-box")
            ], className = "col-4")

################################
## Post Performance Functions ##
################################


def post_performance_hours_live(df, metric, df_avg, time_period):

    
    #create all the variables that are specific to each time frame
    #this includes creating a benchmark dataframe to have a comparison for the performance of each post
    if time_period == "First 24 Hours":
        df_new = df.loc[df["hours_live"] <= 24].copy()
        X_AXIS = "hours_live"
        AVG_GROUP = df_avg.loc[df_avg["hours_live"] > 24, ["media_id", "timestamp"]].drop_duplicates().sort_values(by = "timestamp").tail(5)["media_id"].tolist()
        df_benchmark = df_avg.loc[(df_avg["media_id"].isin(AVG_GROUP)) & (df_avg["hours_live"] <= 24)].copy()
        TICKVALS = [2 * i for i in range(0, 13)]
        Y_TICKFORMAT = ","
        X_AXIS_TITLE = "Number of Hours Live"
        TITLE = "First 24 Hours {}".format(metric.title())
        HOVERTEMPLATE = "Hours live: %{x}<br>" + metric.title() + ": %{y:.0f}<extra></extra>"
    elif time_period == "First 7 Days":
        df_new = df.loc[(df["hours_live"] <= 168) & (df["hours_live"] % 6 == 0)].copy()
        X_AXIS = "days_live"
        AVG_GROUP = df_avg.loc[df_avg["hours_live"] > 168, ["media_id", "timestamp"]].drop_duplicates().sort_values(by = "timestamp").tail(5)["media_id"].tolist()
        df_benchmark = df_avg.loc[(df_avg["media_id"].isin(AVG_GROUP)) & (df_avg["hours_live"] <= 168) & (df_avg["hours_live"] % 6 == 0)].copy()
        TICKVALS = [i / 2.0 for i in range(0, 15)]
        Y_TICKFORMAT = ","
        X_AXIS_TITLE = "Number of Days Live"
        TITLE = "First 7 Days {}".format(metric.title())
        HOVERTEMPLATE = "Days live: %{x}<br>" + metric.title() + ": %{y:.0f}<extra></extra>"
    elif time_period == "All Time":
        df_new = df.loc[df["hours_live"] % 24 == 0].copy()
        X_AXIS = "days_live"
        Y_TICKFORMAT = ","
        AVG_GROUP = df_avg[["media_id", "timestamp"]].drop_duplicates().sort_values(by = "timestamp").tail(5)["media_id"].tolist()
        df_benchmark = df_avg.loc[(df_avg["media_id"].isin(AVG_GROUP)) & (df_avg["hours_live"] % 24 == 0)].copy()
        X_AXIS_TITLE = "Number of Days Live"
        TITLE = "Overall {}".format(metric.title())
        HOVERTEMPLATE = "Days live: %{x}<br>" + metric.title() + ": %{y:.0f}<extra></extra>"
        TICKVALS = None
    
    #create the final benchmark dataframe which will be plotted
    df_benchmark = df_benchmark.groupby(["hours_live"]).agg(avg_metric = (metric, "mean")).reset_index()
    
    #create the maximum y-axis value
    try:
        Y_MAX = max(math.ceil(df_new[metric].max() / 50) * 50, math.ceil(df_benchmark["avg_metric"].max() / 50) * 50)
    except:
        Y_MAX = max(0, math.ceil(df_benchmark["avg_metric"].max() / 50) * 50)

    #convert hours live to days live for the longer timeline graphs
    df_new["days_live"] = df_new["hours_live"] / 24
    df_benchmark["days_live"] = df_benchmark["hours_live"] / 24

    #add in the zero's to the dataframe
    NEW_ROW = {"media_id": df_new["media_id"].tolist()[0], "engagement": 0, "reach": 0,
                "hours_live": 0, "days_live": 0}
    df_new = df_new.append(NEW_ROW, ignore_index=True)
    df_new.sort_values(by = X_AXIS, inplace = True)

    NEW_ROW_BM = {"avg_metric": 0, "hours_live": 0, "days_live": 0}
    df_benchmark = df_benchmark.append(NEW_ROW_BM, ignore_index=True)
    df_benchmark.sort_values(by = X_AXIS, inplace = True)

    #create the graph
    fig = go.Figure()

    fig.add_trace(go.Scatter(x = df_new[X_AXIS],
                                y = df_new[metric],
                                mode = "lines",
                                marker = dict(color = MARKER_COLOR_TY),
                                hovertemplate = HOVERTEMPLATE))
    
    fig.add_trace(go.Scatter(x = df_benchmark[X_AXIS],
                                y = df_benchmark["avg_metric"],
                                mode = "lines",
                                marker = dict(color = MARKER_COLOR_BM),
                                hovertemplate = HOVERTEMPLATE))

    fig.update_layout(plot_bgcolor = PLOT_BGCOLOR,
                        paper_bgcolor = PLOT_BGCOLOR,
                        font = dict(color = FONT_COLOR_TEXT, size = FONT_SIZE_TEXT),
                        showlegend = False,
                        xaxis = dict(linecolor = FONT_COLOR_TEXT, tickvals = TICKVALS),
                        yaxis = dict(linecolor = FONT_COLOR_TEXT, range = [0, Y_MAX], tickformat = Y_TICKFORMAT),
                        margin = GRAPH_MARGINS,
                        height = GRAPH_HEIGHT_ROW_2)

    #x-axis title
    fig.add_annotation(text = X_AXIS_TITLE.upper(),
                        xref = "paper",
                        yref = "paper",
                        x = -0.01,
                        y = -0.1,
                        showarrow = False,
                        align = "left",
                        xanchor = "left")

    #y-axis title
    fig.add_annotation(text = metric.upper(),
                        xref = "paper",
                        yref = "paper",
                        x = -0.09,
                        y = 1.02,
                        showarrow = False,
                        textangle = -90,
                        align = "right",
                        yanchor = "top")

    #title
    fig.add_annotation(text = TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = -0.09,
                        y = 1.15,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_TITLE_ROW_3, color = FONT_COLOR_TITLE))

    #sub title
    fig.add_annotation(text = '<span style="color:' + MARKER_COLOR_TY +'">This Post </span>| <span style="color:' + MARKER_COLOR_BM +'">Latest 5 Post Average</span>',
                        xref = "paper",
                        yref = "paper",
                        x = -0.09,
                        y = 1.08,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_LEGEND_SUBTITLE))     

    return fig



###########################
## Competitors Functions ##
###########################



def competitors_over_time_index(df, comp_view_type, metric, start_date, end_date, competitor = None):
    
    #filter the dataframe to only include the dates specified
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    df = df.loc[(df["created_date_hour"] == 0) & (df["created_date_date"].between(start_date, end_date))].copy()

    #create all the variables that are specific to each metric
    if metric == "followers":
        avg_metric = "avg_followers_count"
        TITLE = "Followers Index - Competitors"
    elif metric == "media_count":
        avg_metric = "avg_media_count"
        TITLE = "Media Count Index - Competitors"
    elif metric == "following":
        avg_metric = "avg_follows_count"
        TITLE = "Following Index - Competitors"

    #create all the variables that are specific to each competitor view type
    if comp_view_type == "competitor":
        BRAND_GROUP = "brand"

        df = df[["created_date_date", BRAND_GROUP, "followers_count", "media_count", "follows_count"]].groupby([BRAND_GROUP, "created_date_date"]).agg(avg_followers_count = ("followers_count", "mean"),
                                                                                            avg_media_count = ("media_count", "mean"),
                                                                                            avg_follows_count = ("follows_count", "mean")).reset_index()
        
        NP_INDEX_VALUE = df.loc[(df["created_date_date"] == df["created_date_date"].min()) & (df[BRAND_GROUP] == "nomadpursuit"), avg_metric].tolist()[0]
        COMP_INDEX_VALUE = df.loc[(df["created_date_date"] == df["created_date_date"].min()) & (df[BRAND_GROUP] == "competitor"), avg_metric].tolist()[0]

        df["index_value"] = df[avg_metric] / NP_INDEX_VALUE
        df.loc[df[BRAND_GROUP] == "competitor", "index_value"] = df.loc[df[BRAND_GROUP] == "competitor", avg_metric] / COMP_INDEX_VALUE
        
        df["color"] = MARKER_COLOR_TY
        df.loc[df[BRAND_GROUP] == "competitor", "color"] = MARKER_COLOR_LY

        LEGEND = '<span style="color:' + MARKER_COLOR_TY + '">nomadpursuit</span> | <span style="color:' + MARKER_COLOR_LY + '">Competitors Overall</span>'
        TITLE = metric.title() + " Index - Competitors Overall"
        Y_LEGEND = 1.08
        Y_TITLE = 1.16

    elif comp_view_type == "Groups":
        BRAND_GROUP = "followers_count_group"
        
        df.loc[df["user_account"] == "nomadpursuit", BRAND_GROUP] = "nomadpursuit"
        df = df[["created_date_date", BRAND_GROUP, "followers_count", "media_count", "follows_count"]].groupby([BRAND_GROUP, "created_date_date"]).agg(avg_followers_count = ("followers_count", "mean"),
                                                                                            avg_media_count = ("media_count", "mean"),
                                                                                            avg_follows_count = ("follows_count", "mean")).reset_index()
        
        #create index value for each group
        NP_INDEX_VALUE = df.loc[(df["created_date_date"] == df["created_date_date"].min()) & (df[BRAND_GROUP] == "nomadpursuit"), avg_metric].tolist()[0]
        EXTRA_LOW_INDEX_VALUE = df.loc[(df["created_date_date"] == df["created_date_date"].min()) & (df[BRAND_GROUP] == "Under 1k"), avg_metric].tolist()[0]
        LOW_INDEX_VALUE = df.loc[(df["created_date_date"] == df["created_date_date"].min()) & (df[BRAND_GROUP] == "1k-5k"), avg_metric].tolist()[0]
        MEDIUM_INDEX_VALUE = df.loc[(df["created_date_date"] == df["created_date_date"].min()) & (df[BRAND_GROUP] == "5k-10k"), avg_metric].tolist()[0]
        HIGH_INDEX_VALUE = df.loc[(df["created_date_date"] == df["created_date_date"].min()) & (df[BRAND_GROUP] == "Over 10k"), avg_metric].tolist()[0]

        #now create a column for the indexes for each group
        df["index_value"] = df[avg_metric] / NP_INDEX_VALUE
        df.loc[df[BRAND_GROUP] == "Under 1k", "index_value"] = df.loc[df[BRAND_GROUP] == "Under 1k", avg_metric] / EXTRA_LOW_INDEX_VALUE
        df.loc[df[BRAND_GROUP] == "1k-5k", "index_value"] = df.loc[df[BRAND_GROUP] == "1k-5k", avg_metric] / LOW_INDEX_VALUE
        df.loc[df[BRAND_GROUP] == "5k-10k", "index_value"] = df.loc[df[BRAND_GROUP] == "5k-10k", avg_metric] / MEDIUM_INDEX_VALUE
        df.loc[df[BRAND_GROUP] == "Over 10k", "index_value"] = df.loc[df[BRAND_GROUP] == "Over 10k", avg_metric] / HIGH_INDEX_VALUE

        df["color"] = MARKER_COLOR_TY
        df.loc[df[BRAND_GROUP] == "Under 1k", "color"] = MARKER_COLOR_EXTRA_LOW
        df.loc[df[BRAND_GROUP] == "1k-5k", "color"] = MARKER_COLOR_LOW
        df.loc[df[BRAND_GROUP] == "5k-10k", "color"] = MARKER_COLOR_MEDIUM
        df.loc[df[BRAND_GROUP] == "Over 10k", "color"] = MARKER_COLOR_HIGH

        LEGEND = '<span style="color:' + MARKER_COLOR_TY + '">nomadpursuit</span> | <span style="color:' + MARKER_COLOR_EXTRA_LOW + '">Under 1k</span> | <span style="color:' + MARKER_COLOR_LOW + '">1k-5k</span> | <span style="color:' + MARKER_COLOR_MEDIUM + '">5k-10k</span> | <span style="color:' + MARKER_COLOR_HIGH + '">Over 10k</span>'
        TITLE = metric.title() + " Index - Competitor Group"
        Y_LEGEND = 1.08
        Y_TITLE = 1.16

    elif comp_view_type == "Individual":
        BRAND_GROUP = "user_account"

        if isinstance(competitor, str):
            competitor = [competitor]

        if competitor == None:
            df = df.loc[df["user_account"].isin(["nomadpursuit"]), ["created_date_date", BRAND_GROUP, "followers_count", "media_count", "follows_count"]].groupby([BRAND_GROUP, "created_date_date"]).agg(avg_followers_count = ("followers_count", "mean"),
                                                                                                avg_media_count = ("media_count", "mean"),
                                                                                                avg_follows_count = ("follows_count", "mean")).reset_index()
        else:
            df = df.loc[df["user_account"].isin(competitor + ["nomadpursuit"]), ["created_date_date", BRAND_GROUP, "followers_count", "media_count", "follows_count"]].groupby([BRAND_GROUP, "created_date_date"]).agg(avg_followers_count = ("followers_count", "mean"),
                                                                                                avg_media_count = ("media_count", "mean"),
                                                                                                avg_follows_count = ("follows_count", "mean")).reset_index()



        NP_INDEX_VALUE = df.loc[(df["created_date_date"] == df["created_date_date"].min()) & (df[BRAND_GROUP] == "nomadpursuit"), avg_metric].tolist()[0]
        df["index_value"] = df[avg_metric] / NP_INDEX_VALUE
        df["color"] = MARKER_COLOR_TY
        
        LEGEND = '<span style="color:' + MARKER_COLOR_TY + '">nomadpursuit</span>'
        Y_LEGEND = 1.08
        Y_TITLE = 1.16

        #now create the variables specific to how many competitors were selected (this isn't applicable to the comp view type because the legend fits on 1 line)
        if len(competitor) >= 1:
            COMP_1_INDEX_VALUE = df.loc[(df["created_date_date"] == df.loc[df[BRAND_GROUP] == competitor[0], "created_date_date"].min()) & (df[BRAND_GROUP] == competitor[0]), avg_metric].tolist()[0]
            df.loc[df[BRAND_GROUP] == competitor[0], "index_value"] = df.loc[df[BRAND_GROUP] == competitor[0], avg_metric] / COMP_1_INDEX_VALUE
            df.loc[df[BRAND_GROUP] == competitor[0], "color"] = MARKER_COLOR_EXTRA_LOW
            LEGEND = '<span style="color:' + MARKER_COLOR_TY + '">nomadpursuit</span> | <span style="color:' + MARKER_COLOR_EXTRA_LOW + '">' + competitor[0] + '</span>'
            Y_LEGEND = 1.08
            Y_TITLE = 1.16
        if len(competitor) >= 2:
            COMP_2_INDEX_VALUE = df.loc[(df["created_date_date"] == df.loc[df[BRAND_GROUP] == competitor[1], "created_date_date"].min()) & (df[BRAND_GROUP] == competitor[1]) , avg_metric].tolist()[0]
            df.loc[df[BRAND_GROUP] == competitor[1], "index_value"] = df.loc[df[BRAND_GROUP] == competitor[1], avg_metric] / COMP_2_INDEX_VALUE
            df.loc[df[BRAND_GROUP] == competitor[1], "color"] = MARKER_COLOR_LOW
            LEGEND = '<span style="color:' + MARKER_COLOR_TY + '">nomadpursuit</span> | <span style="color:' + MARKER_COLOR_EXTRA_LOW + '">' + competitor[0] + '</span> | <span style="color:' + MARKER_COLOR_LOW + '">' + competitor[1] + '</span>'
            Y_LEGEND = 1.08
            Y_TITLE = 1.16
        if len(competitor) >= 3:
            COMP_3_INDEX_VALUE = df.loc[(df["created_date_date"] == df.loc[df[BRAND_GROUP] == competitor[2], "created_date_date"].min()) & (df[BRAND_GROUP] == competitor[2]) , avg_metric].tolist()[0]
            df.loc[df[BRAND_GROUP] == competitor[2], "index_value"] = df.loc[df[BRAND_GROUP] == competitor[2], avg_metric] / COMP_3_INDEX_VALUE
            df.loc[df[BRAND_GROUP] == competitor[2], "color"] = MARKER_COLOR_MEDIUM
            LEGEND = '<span style="color:' + MARKER_COLOR_TY + '">nomadpursuit</span> | <span style="color:' + MARKER_COLOR_EXTRA_LOW + '">' + competitor[0] + '</span> | <span style="color:' + MARKER_COLOR_LOW + '">' + competitor[1] + '</span> | <br><span style="color:' + MARKER_COLOR_MEDIUM + '">' + competitor[2] + '</span>'
            Y_LEGEND = 1.16
            Y_TITLE = 1.24
        if len(competitor) == 4:
            COMP_4_INDEX_VALUE = df.loc[(df["created_date_date"] == df.loc[df[BRAND_GROUP] == competitor[3], "created_date_date"].min()) & (df[BRAND_GROUP] == competitor[3]), avg_metric].tolist()[0]
            df.loc[df[BRAND_GROUP] == competitor[3], "index_value"] = df.loc[df[BRAND_GROUP] == competitor[3], avg_metric] / COMP_4_INDEX_VALUE
            df.loc[df[BRAND_GROUP] == competitor[3], "color"] = MARKER_COLOR_HIGH
            LEGEND = '<span style="color:' + MARKER_COLOR_TY + '">nomadpursuit</span> | <span style="color:' + MARKER_COLOR_EXTRA_LOW + '">' + competitor[0] + '</span> | <span style="color:' + MARKER_COLOR_LOW + '">' + competitor[1] + '</span> | <br><span style="color:' + MARKER_COLOR_MEDIUM + '">' + competitor[2] + '</span> | <span style="color:' + MARKER_COLOR_HIGH + '">' + competitor[3] + '</span>'
            Y_LEGEND = 1.16
            Y_TITLE = 1.24

    fig = go.Figure()

    for brand_type in df[BRAND_GROUP].unique():
        df_plot = df.loc[df[BRAND_GROUP] == brand_type].copy()
        
        fig.add_trace(go.Scatter(x = df_plot["created_date_date"], y = df_plot["index_value"],
                                    mode = "lines",
                                    marker = dict(color = df_plot["color"].tolist()[0]),
                                    text = df_plot[BRAND_GROUP],
                                    hovertemplate = 
                                    "Date: %{x}<br>" +
                                    "Index Value: %{y:.2f}<br>" +
                                    "Competitor: %{text}<extra></extra>"))
        
    fig.update_layout(plot_bgcolor = PLOT_BGCOLOR, 
                        paper_bgcolor = PLOT_BGCOLOR,
                        font = dict(color = FONT_COLOR_TEXT, size = FONT_SIZE_TEXT),
                        xaxis = dict(tickformat = "%d-%b"),
                        showlegend = False,
                        margin = GRAPH_MARGINS_ROW_3,
                        height = GRAPH_HEIGHT_ROW_3
                        )

    #x-axis title
    fig.add_annotation(text = "DATE",
                        xref = "paper",
                        yref = "paper",
                        x = 0,
                        y = -0.12,
                        showarrow = False,
                        align = "left",
                        xanchor = "left")

    #y-axis title
    fig.add_annotation(text = "INDEX",
                        xref = "paper",
                        yref = "paper",
                        x = -0.12,
                        y = 0.99,
                        showarrow = False,
                        textangle = -90,
                        align = "right",
                        yanchor = "top")

    #legend
    fig.add_annotation(text = LEGEND,
                        xref = "paper",
                        yref = "paper",
                        x = -0.12,
                        y = Y_LEGEND,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_LEGEND_SUBTITLE))

    #title
    fig.add_annotation(text = TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = -0.12,
                        y = Y_TITLE,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(color = FONT_COLOR_TITLE, size = FONT_SIZE_TITLE_ROW_3))

    return fig






def competitors_heatmap(df, comp_view_type, comp_selector_value, metric, start_date, end_date):
    
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()

    #create weekday and hour variables for the x and y axis of the heatmap
    df["created_date_weekday"] = df["created_date"].dt.weekday
    df["created_date_weekday"] = df["created_date_weekday"].map({0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5:"Sat", 6: "Sun"})
    metric_column = "{}_count".format(metric)
    df["created_date_hour"] = df["created_date_hour"].map({0: "12AM", 1: "1AM", 2: "2AM", 3: "3AM", 4: "4AM", 5:"5AM", 6: "6AM",
                                                            7: "7AM", 8: "8AM", 9: "9AM", 10: "10AM", 11: "11AM", 12:"12PM", 13: "1PM",
                                                            14: "2PM", 15: "3PM", 16: "4PM", 17: "5PM", 18: "6PM", 19:"7PM", 20: "8PM",
                                                            21: "9PM", 22: "10PM", 23:"11PM"})

    #create variables specific to each competitor view type
    if comp_view_type == "competitor":
        BRAND_GROUP = "brand"

        df = df.loc[(df[BRAND_GROUP] == comp_selector_value) & (df["created_date_date"].between(start_date, end_date)), ["created_date", "created_date_weekday", "created_date_hour", BRAND_GROUP, "followers_count", "media_count", "follows_count"]].groupby([BRAND_GROUP, "created_date", "created_date_weekday", "created_date_hour"]).agg(followers_count = ("followers_count", "sum"),
                                                                                            media_count = ("media_count", "sum"),
                                                                                            follows_count = ("follows_count", "sum")).reset_index()
        
        df.sort_values(by = ["created_date"], inplace = True)

        #calculate the variance between the followers/media count and the previous one for each group
        df["metric_lag"] = df.groupby(BRAND_GROUP)[metric_column].shift()
        df["metric_variance"] = df[metric_column] - df[metric_column].shift() 
        
        df_new = df.groupby(["created_date_weekday", "created_date_hour"]).agg(metric_variance = ("metric_variance", "sum")).reset_index()
    
    elif comp_view_type == "Groups":
        BRAND_GROUP = "followers_count_group"

        df.loc[df["user_account"] == "nomadpursuit", BRAND_GROUP] = "nomadpursuit"

        df = df.loc[(df[BRAND_GROUP] == comp_selector_value) & (df["created_date_date"].between(start_date, end_date)), ["created_date", "created_date_weekday", "created_date_hour", BRAND_GROUP, "followers_count", "media_count", "follows_count"]].groupby([BRAND_GROUP, "created_date", "created_date_weekday", "created_date_hour"]).agg(followers_count = ("followers_count", "sum"),
                                                                                            media_count = ("media_count", "sum"),
                                                                                            follows_count = ("follows_count", "sum")).reset_index()

        
        df.sort_values(by = ["created_date"], inplace = True)

        #calculate the variance between the followers/media count and the previous one for each group
        df["metric_lag"] = df.groupby(BRAND_GROUP)[metric_column].shift()
        df["metric_variance"] = df[metric_column] - df[metric_column].shift() 
        
        df_new = df.groupby(["created_date_weekday", "created_date_hour"]).agg(metric_variance = ("metric_variance", "sum")).reset_index()
    
    elif comp_view_type == "Individual":
        BRAND_GROUP = "user_account"


        df = df.loc[(df[BRAND_GROUP] == comp_selector_value) & (df["created_date_date"].between(start_date, end_date)), ["created_date", "created_date_weekday", "created_date_hour", BRAND_GROUP, "followers_count", "media_count", "follows_count"]].groupby([BRAND_GROUP, "created_date", "created_date_weekday", "created_date_hour"]).agg(followers_count = ("followers_count", "sum"),
                                                                                            media_count = ("media_count", "sum"),
                                                                                            follows_count = ("follows_count", "sum")).reset_index()

        #calculate the variance between the followers/media count and the previous one for each group
        df["metric_lag"] = df.groupby(BRAND_GROUP)[metric_column].shift()
        df["metric_variance"] = df[metric_column] - df[metric_column].shift() 
        
        df_new = df.groupby(["created_date_weekday", "created_date_hour"]).agg(metric_variance = ("metric_variance", "sum")).reset_index()
    
    #now create the variables specific to each metric
    if metric == "followers":
        TITLE = "Followers Variance by Day of Week & Hour"
        LEGEND_TITLE = "FOLLOWERS VARIANCE"
        if comp_selector_value == "nomadpursuit":
            LEGEND_TITLE_X_AXIS =  1.32
        elif comp_selector_value != "nomadpursuit":
            LEGEND_TITLE_X_AXIS = 1.34
    elif metric == "media":
        TITLE = "Media Count Variance by Day of Week & Hour"
        LEGEND_TITLE = "MEDIA COUNT VARIANCE"
        if comp_selector_value == "nomadpursuit":
            LEGEND_TITLE_X_AXIS =  1.36
        elif comp_selector_value != "nomadpursuit":
            LEGEND_TITLE_X_AXIS = 1.32
    elif metric == "follows":
        TITLE = "Following Variance by Day of Week & Hour"
        LEGEND_TITLE = "FOLLOWING VARIANCE"
        if comp_selector_value == "nomadpursuit":
            LEGEND_TITLE_X_AXIS =  1.34
        elif comp_selector_value != "nomadpursuit":
            LEGEND_TITLE_X_AXIS = 1.38

    #get the color scales to be used in the heatmap
    HEATMAP_COLOR_MAX = "#129132"
    HEATMAP_COLOR_MID = "white"
    HEATMAP_COLOR_MIN = "#C82A19"

    fig = go.Figure()

    fig.add_trace(go.Heatmap(x = df_new["created_date_weekday"], y = df_new["created_date_hour"], z = df_new["metric_variance"],
                            colorscale = [[0, HEATMAP_COLOR_MIN], [0.5, HEATMAP_COLOR_MID], [1, HEATMAP_COLOR_MAX]],
                            zmid = 0,
                            hovertemplate = "Day of Week: %{y}<br>Hour: %{x}<br>Follower Variance: %{z}<extra></extra>"))

    fig.update_layout(plot_bgcolor = PLOT_BGCOLOR,
                        paper_bgcolor = PLOT_BGCOLOR,
                        xaxis = dict(linecolor = PLOT_BGCOLOR, gridcolor = PLOT_BGCOLOR,
                                    categoryarray = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
                        yaxis = dict(linecolor = PLOT_BGCOLOR, gridcolor = PLOT_BGCOLOR,
                                    categoryarray = ["12AM", "1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", 
                                                    "8AM", "9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM",
                                                    "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM", "11PM",]),
                        font = dict(color = FONT_COLOR_TEXT, size = FONT_SIZE_TEXT),
                        margin = GRAPH_MARGINS_HEATMAP,
                        height = GRAPH_HEIGHT_ROW_3_HEATMAP
                        )

    #title
    fig.add_annotation(text = TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = -0.195,
                        y = 1.11,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_TITLE_ROW_3, color = FONT_COLOR_TITLE))

    #y-axis title
    fig.add_annotation(text = "HOUR",
                        xref = "paper",
                        yref = "paper",
                        x = -0.2,
                        y = 1.02,
                        showarrow = False,
                        textangle= -90,
                        align = "right",
                        yanchor = "top",
                        font = dict(size = FONT_SIZE_TEXT, color = FONT_COLOR_TEXT))

    #legend title
    fig.add_annotation(text = LEGEND_TITLE,
                        xref = "paper",
                        yref = "paper",
                        x = LEGEND_TITLE_X_AXIS,
                        y = 0.98,
                        showarrow = False,
                        textangle= 90,
                        align = "right",
                        yanchor = "top",
                        font = dict(size = FONT_SIZE_TEXT, color = FONT_COLOR_TEXT))

    #x-axis title
    fig.add_annotation(text = "DAY OF WEEK",
                        xref = "paper",
                        yref = "paper",
                        x = 0.02,
                        y = -0.13,
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        font = dict(size = FONT_SIZE_TEXT, color = FONT_COLOR_TEXT))

    return fig


#############################
## Text Analysis Functions ##
#############################

#create a function to clean the text
def clean_text(string):
    return re.sub("[^a-zA-Z]", "", string)
