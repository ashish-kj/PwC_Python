mapbox_access_token = "pk.eyJ1IjoiYXNoaXNoamhhMjEiLCJhIjoiY2t2YmJvdTdtMjdqdDMzb2t4NmNvdHE4NiJ9.ZqBYpLao0YBfuaLa7fuWew"
import datetime
from datetime import date
import pandas as pd
import numpy as np
import dash                    
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.offline as py    
import plotly.graph_objs as go
from predicthq import Client

icon_dict = {"academic": "college",
    "airport-delays": "airport",
    "community": "town-hall",
    "concerts": "music",
    "conferences": "marker",
    "daylight-savings": "marker",
    "disasters": "volcano",
    "expos": "star",
    "festivals": "marker",
    "health-warnings": "hospital",
    "observances": "town-hall",
    "performing-arts": "theatre",
    "politics": "town-hall",
    "public-holidays": "marker",
    "school-holidays": "marker",
    "severe-weather": "volcano",
    "sports": "stadium",
    "terror": "fire-station"}

rank_dict = {
    "0 - 20":1,
    "20 - 40":2,
    "40 - 60":3,
    "60 - 80":4,
    "80 - 100":5
}

eventStatus_dict = {
    "active": 1,
    "cancelled" : 2,
    "postponed" : 3
    
}

phq = Client(access_token="MivqobgiCDmkdYOczGBWv8vtnPa-zoYiNmPOzpIc")

df = pd.read_excel("api_output.xlsx")
app = dash.Dash(__name__)

blackbold={'color':'black', 'font-weight': 'bold'}


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label(children=['Event Status'], style=blackbold),
            dcc.Checklist(id='event_type',
                    options=[{'label':str(b),'value':b} for b in eventStatus_dict],
                    value=[b for b in eventStatus_dict],
        ),
        html.Br(),
        html.Br(),
            html.Label(children=['Date Range for Event'], style=blackbold),
            dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=date(2021, 1, 1),
            max_date_allowed=date(2023, 1, 1),
            initial_visible_month=date(2021, 10, 30),
            start_date=date(2021, 10, 30),
            end_date=date(2022, 1, 1),
        ),
        html.Br(),
        html.Br(),
            html.Label(children=['Search by querry'], style=blackbold),
            dcc.Input(
            id='my_txt_input',
            type='text',
            debounce=True,           # changes to input are sent to Dash server only on enter or losing focus
            #pattern=r"^[A-Za-z].*",  # Regex: string must start with letters only
            spellCheck=True,
            inputMode='latin',       # provides a hint to browser on type of data that might be entered by the user.
            name='text',             # the name of the control, which is submitted with the form data
            #list='browser',          # identifies a list of pre-defined options to suggest to the user
            #n_submit=0,              # number of times the Enter key was pressed while the input had focus
            #n_submit_timestamp=-1,   # last time that Enter was pressed
            autoFocus=True,          # the element should be automatically focused after the page loaded
            #n_blur=0,                # number of times the input lost focus
            #n_blur_timestamp=-1,     # last time the input lost focus.
            # selectionDirection='', # the direction in which selection occurred
            # selectionStart='',     # the offset into the element's text content of the first selected character
            # selectionEnd='',       # the offset into the element's text content of the last selected character
        ),
        html.Br(),
        html.Br(),
            html.Label(children=['Categories: '], style=blackbold),
            dcc.Checklist(id='category_name',
                    options=[{'label':str(b),'value':b} for b in icon_dict],
                    value=[b for b in icon_dict],
            ),
            html.Label(children=['Rank selection: '], style=blackbold),
            dcc.Checklist(id='rank_name',
                    options=[{'label':str(b),'value':b} for b in rank_dict],
                    value=[b for b in rank_dict],
            ),
            html.Br()
        ], className='three columns'
        ),

        # Map
        html.Div([
            dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                style={'background':'#FFFFFF','padding-bottom':'2px','padding-left':'2px','height':'100vh'}
            ),
            html.Label(['Location Description:'],style=blackbold),
            html.Pre(id='location_desc', children=[],
            style={'white-space': 'pre-wrap','word-break': 'break-all',
                 'border': '3px solid black','text-align': 'center',
                 'padding': '12px 12px 12px 12px', 'color':'blue',
                 'margin-top': '3px'}
            ),
        ], className='nine columns'
        ),

    ], className='row'
    ),

], className='ten columns offset-by-one'
)

#---------------------------------------------------------------
# Output of Graph
@app.callback(Output('graph', 'figure'),
              [Input('category_name', 'value'),
               Input('rank_name', 'value'),
               Input('my_txt_input', 'value'),
               Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),
               Input('event_type', 'value')])


def update_figure(chosen_category, chosen_rank, txt_inserted, start_date, end_date, activation):
    date_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    date_end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    #print(date_start)
    #print(type(date_start))
    rank_list = []
    search_query = str(txt_inserted)
    if('0 - 20' in chosen_rank):rank_list.append(1)
    if('20 - 40' in chosen_rank):rank_list.append(2)
    if('40 - 60' in chosen_rank):rank_list.append(3)
    if('60 - 80' in chosen_rank):rank_list.append(4)
    if('80 - 100' in chosen_rank):rank_list.append(5)
    df_sub = pd.DataFrame()
    df_subs = pd.DataFrame()
    
    for event in phq.events.search(q = search_query, country = 'AE', rank_level = rank_list, limit = 200):  #state = 'active', rank_level = [1,2,3,4,5],
        
        dic = {}
        dic['ID'] = event.id 
        dic['Rank'] = event.rank
        if event.rank in range(0, 21):
            dic['Rank Level'] = 1
        elif event.rank in range(21, 41):
            dic['Rank Level'] = 2
        elif event.rank in range(41, 61):
            dic['Rank Level'] = 3
        elif event.rank in range(61, 81):
            dic['Rank Level'] = 4
        else:
            dic['Rank Level'] = 5
        dic['Attendance'] = event.phq_attendance
        dic['Local Rank'] = event.local_rank
        dic['Longitude'] = event.location[0]
        dic['Latitude'] = event.location[1]
        dic['Description'] = event.description 
        dic['Category'] = event.category 
        dic['Title'] = event.title 
        dic['state'] = event.state
        dic['Start Time'] = event.start.strftime('%Y-%m-%d') #'%Y-%m-%d, %H:%M:%S'
        dic['End Time'] = event.end.strftime('%Y-%m-%d')
        dic['start'] = datetime.datetime.strptime(event.start.strftime('%Y-%m-%d'), "%Y-%m-%d")
        dic['end'] = datetime.datetime.strptime(event.end.strftime('%Y-%m-%d'), "%Y-%m-%d")
        dic['hov_txt'] = str("Category: "+str(event.category)+"<br>Rank: " + str(event.rank) + "<br>Title: "+str(event.title) + "<br>Status: " + str(event.state) + "<br>Evert start: " + str(event.start.strftime('%Y-%m-%d')) + "<br>Event end: " + str(event.end.strftime('%Y-%m-%d')) + "<br>Attendance: " + str(event.phq_attendance))
        dic['symbol'] = icon_dict[event.category]
        dic['color'] = "#ff00ff"
        df_sub = df_sub.append(dic, ignore_index = True)
        
        #df_sub.to_excel("api_output.xlsx")

    
    
    df_subs = df_sub[(df_sub['Category'].isin(chosen_category)) & (df_sub['state'].isin(activation))]
    mask = ((df_subs['start'] >= date_start) & (df_subs['start'] <= date_end))  | ((df_subs['end'] >= date_start) & (df_subs['end'] <= date_end))
    df_subs = df_subs.loc[mask]
    
    # Create figure
    locations=[go.Scattermapbox(
                    lon = df_subs['Longitude'],
                    lat = df_subs['Latitude'],
                    mode='markers',
                    marker={'size':13, 'symbol': df_subs['symbol']},
                    unselected={'marker' : {'opacity':1}},
                    selected={'marker' : {'opacity':0.5, 'size':25}},
                    hoverinfo='text',
                    hovertext=df_subs['hov_txt'],
                    customdata=df_subs['Description']
    )]

    # Return figure
    return {
        'data': locations,
        'layout': go.Layout(
            uirevision= 'foo', #preserves state of figure/map after callback activated
            clickmode= 'event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="UAE Events &#127878;",font=dict(size=50, color='#1a0808')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                style='dark',
                center=dict(
                    lat=24.466667,
                    lon=54.366669
                ),
                pitch=40,
                zoom=7
            ),
        )
    }
#---------------------------------------------------------------
@app.callback(
    Output('location_desc', 'children'),
    [Input('graph', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return 'Click on any icon'
    else:
        # print (clickData)
        the_desc=clickData['points'][0]['customdata']
        if str(the_desc) =='':
            return 'No Description Available'
        else:
            return the_desc
# #--------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)