import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import datetime as dt
from dash.dependencies import Input, Output

from app import app
from apps.data import df_user_info
from apps.functions import get_navbar, MAX_DATETIME_DATE, MAX_DATETIME_HOUR, competitors_over_time_index, \
    competitors_heatmap


#define the competitor groups by the amount of followers
df_user_info["followers_count_group"] = "Under 1k"
df_user_info.loc[df_user_info["followers_count"].between(1000,4999), "followers_count_group"] = "1k-5k"
df_user_info.loc[df_user_info["followers_count"].between(5000,9999), "followers_count_group"] = "5k-10k"
df_user_info.loc[df_user_info["followers_count"] >= 10000, "followers_count_group"] = "Over 10k"

#define who is a competitor
df_user_info["brand"] = "competitor"
df_user_info.loc[df_user_info["user_account"] == "nomadpursuit", "brand"] = "nomadpursuit"

#remove columns that are not needed when passing df to callback
df_user_info = df_user_info[["created_date","created_date_date", "created_date_hour", "brand", "user_account","followers_count_group", "followers_count", "media_count", "follows_count"]].copy()

#get a list of the most recent competitors along with which account size group they are in
competitors_selection_dropdown = df_user_info.loc[~(df_user_info["user_account"] == "nomadpursuit") & (df_user_info["created_date"] == max(df_user_info["created_date"])), ["user_account", "followers_count_group"]].copy()
competitors_selection_dropdown["dropdown_selection"] = [ "{} ({})".format(i, j) for i, j in zip(competitors_selection_dropdown["user_account"], competitors_selection_dropdown["followers_count_group"])]

competitors_selection_dropdown["dropdown_selection_order"] = competitors_selection_dropdown["followers_count_group"].map({"Under 1k": 1, "1k-5k": 2, "5k-10k": 3, "Over 10k": 4})
competitors_selection_dropdown.sort_values(by = ["dropdown_selection_order", "user_account"], ascending = [True, True], inplace = True)




layout = dbc.Container([
    get_navbar("competitors"),
    dbc.Container([
        dbc.Row([
            dbc.Col([html.P("Select Date Range:", className = "p-metric-title"),
                    dcc.DatePickerRange(id = "competitor-date-range",
                                        start_date = (df_user_info["created_date_date"].max() - dt.timedelta(13)).strftime("%Y-%m-%d"),
                                        end_date = df_user_info["created_date_date"].max().strftime("%Y-%m-%d"),
                                        display_format = "DD-MM-YYYY",
                                        min_date_allowed = "2021-07-28",
                                        max_date_allowed = df_user_info["created_date_date"].max(),
                                        initial_visible_month = (df_user_info["created_date_date"].max() - dt.timedelta(13)).strftime("%Y-%m-%d")
                                        )]),
            dbc.Col([html.P("Select Competitor View:", className = "p-metric-title"),
                    dbc.RadioItems(id = "competitor-view-radio",
                                    options = [{"label": "Overall", "value": "competitor"},
                                                {"label": "Groups", "value": "Groups"},
                                                {"label": "Individual", "value": "Individual"}],
                                    value = "Groups",
                                    inline = True,
                                    labelClassName = "radio-button-label",
                                    labelCheckedClassName = "radio-button-checked")]),
            dbc.Col([html.P("Select Competitor (Max 4):", 
                            id = "competitor-selector-text",
                            className = "p-metric-title",
                            style = None),
                    dcc.Dropdown(id = "competitor-selector-dropdown",
                                options = [{"label": label, "value": value} for label, value in zip(competitors_selection_dropdown["dropdown_selection"], competitors_selection_dropdown["user_account"])],
                                value = competitors_selection_dropdown["user_account"].tolist()[0],
                                multi = True,
                                style = None)])
            
        ]),
    ], className = "container-box"),
    dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Graph(id = "competitor-followers-over-time-graph",
                                config = {"displayModeBar": False}), className = "col-4"),
            dbc.Col(dcc.Graph(id = "competitor-media-count-over-time-graph",
                                config = {"displayModeBar": False}), className = "col-4"),
            dbc.Col(dcc.Graph(id = "competitor-follows-over-time-graph",
                                config = {"displayModeBar": False}), className = "col-4")
        ]),
    ], className = "container-box"),
    dbc.Container([
        dbc.Row([
            dbc.Col([html.P(className = "p-metric-title", id = "competitor-dropdown-heading"),
                    dcc.Dropdown(id = "heatmap-competitor-selector-dropdown", className = "competitor-dropdown")], 
                    className = "col-12")
        ]),
    ], className = "container-box", style = {"width": "33%", "margin-left": "0px"}),
    dbc.Container([
        html.P("Brand: nomadpursuit", className = "p-title"),
        dbc.Row([
            dbc.Col(dcc.Graph(id = "np-followers-heatmap",
                            config = {"displayModeBar": False}), className = "col-4"),
            dbc.Col(dcc.Graph(id = "np-media-count-heatmap",
                            config = {"displayModeBar": False}), className = "col-4"),
            dbc.Col(dcc.Graph(id = "np-follows-heatmap",
                            config = {"displayModeBar": False}), className = "col-4")
        ]),
    ], className = "container-box"),
    dbc.Container([
        html.P(id = "competitor-heading", className = "p-title"),
        dbc.Row([
            dbc.Col(dcc.Graph(id = "competitor-followers-heatmap",
                            config = {"displayModeBar": False}), className = "col-4"),
            dbc.Col(dcc.Graph(id = "competitor-media-count-heatmap",
                            config = {"displayModeBar": False}), className = "col-4"),
            dbc.Col(dcc.Graph(id = "competitor-follows-heatmap",
                            config = {"displayModeBar": False}), className = "col-4")
        ]),
    ], className = "container-box")
])

@app.callback([Output("competitor-followers-over-time-graph", "figure"),
            Output("competitor-media-count-over-time-graph", "figure"),
            Output("competitor-follows-over-time-graph", "figure"),
            Output("heatmap-competitor-selector-dropdown", "options"),
            Output("heatmap-competitor-selector-dropdown", "value"),
            
            Output("np-followers-heatmap", "figure"),
            Output("np-media-count-heatmap", "figure"),
            Output("np-follows-heatmap", "figure"),
            Output("competitor-selector-dropdown", "style"),
            Output("competitor-selector-text", "style")

            ],
            [Input("competitor-date-range", "start_date"),
            Input("competitor-date-range", "end_date"),
            Input("competitor-view-radio", "value"),
            Input("competitor-selector-dropdown", "value")])

def create_competitor_page_content(startdate, enddate, comp_view, comp):

    #create the first three graphs
    fig_comp_followers_over_time = competitors_over_time_index(df_user_info, comp_view, "followers", startdate, enddate, comp)
    fig_comp_media_over_time = competitors_over_time_index(df_user_info, comp_view, "media_count", startdate, enddate, comp)
    fig_comp_follows_over_time = competitors_over_time_index(df_user_info, comp_view, "following", startdate, enddate, comp)

    #if comp is not a list (i.e. only contains 1 competitor) then turn it into a list
    if isinstance(comp, str):
        comp = [comp]
    #get the selection for the second dropdown based on what comp view type was selected and competitors 
    if comp_view == "competitor":
        heatmap_dropdown_options = [{"label": "Overall", "value": "competitor"}]
        heatmap_dropdown_value = "competitor"
        style_dropdown = {"display": "none"}
    elif comp_view == "Groups":
        COMP_GROUPS = ["Under 1k", "1k-5k", "5k-10k", "Over 10k"]
        heatmap_dropdown_options = [{"label": i, "value": i} for i in COMP_GROUPS]
        heatmap_dropdown_value = COMP_GROUPS[0]
        style_dropdown = {"display": "none"}

    elif comp_view == "Individual":
        heatmap_dropdown_options = [{"label": i, "value": j} for i, j in zip(competitors_selection_dropdown["dropdown_selection"], competitors_selection_dropdown["user_account"]) if j in comp]
        heatmap_dropdown_value = comp[0]
        style_dropdown = None


    #pass in a dataframe to the heatmap function that only has nomadpursuit in
    fig_np_heatmp_followers = competitors_heatmap(df_user_info.loc[df_user_info["user_account"] == "nomadpursuit"].copy(), comp_view, "nomadpursuit", "followers", startdate, enddate)
    fig_np_heatmp_media = competitors_heatmap(df_user_info.loc[df_user_info["user_account"] == "nomadpursuit"].copy(), comp_view, "nomadpursuit", "media", startdate, enddate)
    fig_np_heatmp_follows = competitors_heatmap(df_user_info.loc[df_user_info["user_account"] == "nomadpursuit"].copy(), comp_view, "nomadpursuit", "follows", startdate, enddate)

    

    return fig_comp_followers_over_time, fig_comp_media_over_time, fig_comp_follows_over_time, \
        heatmap_dropdown_options, heatmap_dropdown_value, fig_np_heatmp_followers, fig_np_heatmp_media, \
            fig_np_heatmp_follows, style_dropdown, style_dropdown



@app.callback([Output("competitor-followers-heatmap", "figure"),
            Output("competitor-media-count-heatmap", "figure"),
            Output("competitor-follows-heatmap", "figure"),
            Output("competitor-heading", "children"),
            Output("competitor-dropdown-heading", "children"),
            Output("competitor-selector-dropdown", "options")],
            [Input("competitor-date-range", "start_date"),
            Input("competitor-date-range", "end_date"),
            Input("competitor-view-radio", "value"),
            Input("heatmap-competitor-selector-dropdown", "value"),
            Input("competitor-selector-dropdown", "value")])
def create_competitor_heatmaps(startdate, enddate, comp_view, comp, dropdown_value_input):

    #pass in a dataframe to the heatmap function that doesn't have nomadpursuit in
    fig_comp_heatmp_followers = competitors_heatmap(df_user_info.loc[~(df_user_info["user_account"] == "nomadpursuit")].copy(), comp_view, comp, "followers", startdate, enddate)
    fig_comp_heatmp_media = competitors_heatmap(df_user_info.loc[~(df_user_info["user_account"] == "nomadpursuit")].copy(), comp_view, comp, "media", startdate, enddate)
    fig_comp_heatmp_follows = competitors_heatmap(df_user_info.loc[~(df_user_info["user_account"] == "nomadpursuit")].copy(), comp_view, comp, "follows", startdate, enddate)

    #get the title of the dropdown header depending on what type of competitor view has been selected
    if comp_view == "Individual":
        header_title = "Brand: {}".format(comp)
        dropdown_header_title = "Select Competitor:"
    elif comp_view == "Groups": 
        header_title = "Brand Group: {}".format(comp)
        dropdown_header_title = "Select Competitor Group:"
    elif comp_view == "competitor":
        header_title = "Overall"
        dropdown_header_title = "Select Competitor Group:"

    #restrict the options in the dropdown if 4 values have been selected
    if isinstance(dropdown_value_input, str):
        dropdown_value_input = [dropdown_value_input]

    if comp_view == "Individual" and len(dropdown_value_input) >= 4:
        options_dropdown = [{"label": label, "value": value} for label, value in zip(competitors_selection_dropdown["dropdown_selection"], competitors_selection_dropdown["user_account"]) if value in dropdown_value_input]
    else:
        options_dropdown = [{"label": label, "value": value} for label, value in zip(competitors_selection_dropdown["dropdown_selection"], competitors_selection_dropdown["user_account"])]
    
    
    return fig_comp_heatmp_followers, fig_comp_heatmp_media, fig_comp_heatmp_follows, header_title, \
        dropdown_header_title, options_dropdown



