import sys
sys.path.append('..')
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import streamlit as st
import st_aggrid
import pandas as pd
import numpy as np
from streamlit_extras.stylable_container import stylable_container
import streamlit_highcharts as hct
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen
from branca.colormap import StepColormap, LinearColormap
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder, GridUpdateMode
import math
from df_global_search import DataFrameSearch
import plotly.graph_objects as go
from streamlit_echarts import st_echarts


def format_page_element():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            [data-testid=stSidebar] {
            background-color: rgba(1, 66, 106, 0.8);
            color: #ffffff
            }
            .css-17lntkn {
            color: rgba(181, 185, 204, 0.6)
            }
            .css-pkbazv {
            color: #ffffff
            }
            css-fblp2m {
            color: #ffffff
            }
            }
        </style>
        """, 
        unsafe_allow_html=True)

k_sep_formatter = st_aggrid.JsCode("""
    function(params) {
        return (params.value == null) ? params.value : params.value.toLocaleString('en-US'); 
    }
    """)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def CreateHeaderTooltip(grid_table, list_cols):

    for i in range(len(list_cols)):

        grid_table.configure_column(list_cols[i],
                                    headerTooltip=list_cols[i])

    return grid_table

def formatCurrency(value):
    if abs(value) >= 1000000 or value <= -1000000:
        return "{:.1f} M€".format(round(value / 1000000, 1))
    elif abs(value) >= 1000 or value <= -1000:
        return "{:.1f} k€".format(round(value / 1000, 1))
    else:
        return "{:.1f} €".format(round(value, 1))
    
def formatCurrencyTooltip(value):
    if abs(value) >= 1000000:
        return "{:.0f}M".format(round(value / 1000000, 0))
    elif abs(value) >= 1000:
        return "{:.0f}k".format(round(value / 1000, 0))
    else:
        return "{:.0f}".format(round(value, 0))    

def formatNumber(x, unit, digits=0):
    value = f"{x:,.{digits}f}"
    return f"{value}{unit}"

def calculatePercWaterfall(value, totalCol, percentage = True):
    if totalCol == 0:
        return 0
    else:
        result = abs(value) * 100 / totalCol if percentage == True else abs(value)/totalCol
        return result
        
        
def process_data(data):
    total_sales_value = data.TotalSalesValue.sum()
    total_quantity_mt = data.QuantityInMT.sum()
    
    pos_color = "#005959"
    negative_color = "#cb333b"
    cost_color = "#cb333b"
    def waterfallColoring (value):
        return pos_color if value >= 0 else negative_color

    columns = [
        #Format: col_name - display - isSum parameter - color - Negative col
        ("TotalSalesValue", "<b>Revenue</b>", False, pos_color, False),
        ("TotalCOGS", "COGS", False, cost_color, True),
        ("GM", "<b>Gross Margin</b>", True, None, False), #T/F here is to assign isSum later
        ("TotalDemurrageCost", "Demurrage Cost", False, cost_color, True),
        ("TotalStorageCostPerYear", "Storage Cost", False, cost_color, True),
        ("TotalHandlingCost", "Handling Cost", False, cost_color, True),
        ("TotalTransportCost", "Transport Cost", False, cost_color, True),
        ("CBM", "<b>CBM</b>", True, None, False),
        ("IOC", "IROC", False, cost_color, True),
        ("CBMAI", "<b>CBM after IROC</b>", True, None, False),
        ("SGA", "SG&A", False, cost_color, True),
        ("EBITAI", "<b>EBIT after IROC</b>", True, None, False),
    ]   
        
    waterfall_data = []
    for col_data in columns:
        col_name, display_name, is_sum, color, is_cost = col_data
        value = data[col_name].sum() if not is_cost else -data[col_name].sum()
        color = waterfallColoring(value) if color is None else color
        
        col_dict = {
            "name": display_name,
            "y": value,
            "perc": calculatePercWaterfall(value, total_sales_value),
            "perTon": calculatePercWaterfall(value, total_quantity_mt, percentage=False),
            "color": color,
            "dataLabels": {
                "format": formatCurrencyTooltip(value)
            }
        }
        
        if is_sum:
            col_dict["isSum"] = True

        waterfall_data.append(col_dict)

    return waterfall_data

def createWaterfallChart(data):
    data_dict = process_data(data)
    
    chart = {
        "chart": {"type": "waterfall", "zoomType":"x"},
        "title": {"text": ""},
        "xAxis": {
            "type": "category"
        },
        "yAxis": {
            "title": {
                "text": "EUR"
            }
        },
        "legend": {"enabled": False},
        "tooltip": {
            "pointFormat": '<b>{point.y:,.2f} €</b><br/><b>{point.perc:.2f}%</b> of Revenue<br/><b>{point.perTon:.2f}</b> € per MT</b>',
            "followPointer": True
        },
        "series": [{
            "name": "",
            "data": data_dict,
            "dataLabels": {
                "enabled": True,
                "verticalAlign": "top",
                "y": -30,
                "style":{
                    "fontSize": "9px",
                    "fontWeight": "bold"
                },
                "color": "black"
            },
            "pointPadding": 0,
            "borderRadius": 3,
            "colorByPoint": True
        }],
        'exporting': { 
            'enabled': True
        }
    }
    
    return hct.streamlit_highcharts(chart, 530)



def process_waterfall_data(data):
    
    pos_color = "#005959"
    negative_color = "#cb333b"
    cost_color = "#cb333b"
    def waterfallColoring (value):
        return pos_color if value >= 0 else negative_color

    columns = [
        #Format: col_name - display - isSum parameter - color - Negative col
        ("TotalSalesValue", "<b>Revenue</b>", True, pos_color, False),
        ("TotalCOGS", "COGS", False, cost_color, True),
        ("GM", "<b>Gross Margin</b>", True, None, False), #T/F here is to assign isSum later
        ("TotalDemurrageCost", "Demurrage Cost", False, cost_color, True),
        ("TotalStorageCostPerYear", "Storage Cost", False, cost_color, True),
        ("TotalHandlingCost", "Handling Cost", False, cost_color, True),
        ("TotalTransportCost", "Transport Cost", False, cost_color, True),
        ("CBM", "<b>CBM</b>", True, None, False),
        ("IOC", "IROC", False, cost_color, True),
        ("CBMAI", "<b>CBM after IROC</b>", True, None, False),
        ("SGA", "SG&A", False, cost_color, True),
        ("EBITAI", "<b>EBIT after IROC</b>", True, None, False),
    ]   
        
    waterfall_data = []
    for col_data in columns:
        col_name, display_name, is_rev, color, is_cost = col_data
        value = data[col_name].sum() if not is_cost else -data[col_name].sum()
        color = waterfallColoring(value) if color is None else color
        
        col_dict = {
            "ColName": col_name,
            "X-axis": display_name,
            "is_cost":is_cost,
            "is_rev": is_rev,
            "y": value
            # "perc": calculatePercWaterfall(value, total_sales_value),
            # "perTon": calculatePercWaterfall(value, total_quantity_mt, percentage=False),
            # "color": color,
            # "dataLabels": {
            #     "format": formatCurrencyTooltip(value)
            # }
        }
        

        waterfall_data.append(col_dict)

    return waterfall_data



def CreateWaterfallInput(data):
    df = pd.DataFrame(process_waterfall_data(data))

    df.index = df.ColName.tolist()

    df_transposed = df.transpose()[1:]

    value_list = df_transposed.loc["y"].tolist()
    isrev_list = df_transposed.loc["is_rev"].tolist()
    iscost_list =  df_transposed.loc["is_cost"].tolist()

    positive_rev = []
    negative_rev = []
    for i in range(len(value_list)):
        positive_rev.append(value_list[i] if value_list[i] >=0 and isrev_list[i] else None if iscost_list[i] else 0)
        negative_rev.append(value_list[i] if value_list[i] <0 and isrev_list[i] else None if iscost_list[i] else 0)

    cost = []
    for i in range(len(value_list)):
        cost.append(value_list[i] if iscost_list[i] else None)

    # placeholder = []
    # for i in range(len(value_list)):
    #     placeholder.append(0 if isrev_list[i] else None)

    # placeholder = [value_list[i] if math.isnan(val) else val for i, val in enumerate(placeholder)]    

    # negatives = df_transposed.loc['y',df_transposed.loc["is_rev"]] < 0
    # df_transposed.loc['y',negatives[negatives].first_valid_index()]

    running_total = value_list[0]
    values_to_add = cost
    gap = []

    for value in values_to_add:
        if value is not None: 
            running_total += value
            gap.append(running_total)
        else:
            gap.append(0) 

    placeholder = gap.copy()

    if next((i for i, x in enumerate(gap) if x < 0), None) is not None:
        placeholder[next((i for i, x in enumerate(gap) if x < 0), None)] = 0
        for i in range(len(value_list)):
            if cost[i] is not None and i > next((i for i, x in enumerate(gap) if x < 0), None):
                placeholder[i] = placeholder[i] - cost[i]    


    negative_cost = []
    for i in range(len(value_list)):
        negative_cost.append(cost[i] if gap[i] < 0 else None)

    if next((i for i, x in enumerate(gap) if x < 0), None) is not None:
        negative_cost[next((i for i, x in enumerate(gap) if x < 0), None)] = gap[next((i for i, x in enumerate(gap) if x < 0), None)]

    postive_cost = []
    for i in range(len(value_list)):
        postive_cost.append(abs(cost[i]) if gap[i] > 0 else None) 


    if next((i for i, x in enumerate(gap) if x < 0), None) is not None:
        if isrev_list[(next((i for i, x in enumerate(gap) if x < 0), None)) - 1]:
            postive_cost[next((i for i, x in enumerate(gap) if x < 0), None)] = value_list[(next((i for i, x in enumerate(gap) if x < 0), None)) - 1]
        else:
            postive_cost[next((i for i, x in enumerate(gap) if x < 0), None)]  = gap[(next((i for i, x in enumerate(gap) if x < 0), None)) - 1]  


    data_waterfall = pd.DataFrame(
        {"Name": df.ColName.tolist(),
        "positive_rev": positive_rev,
        "negative_rev": negative_rev,
        "placeholder": placeholder,
        "negative_cost": negative_cost,
        "postive_cost": postive_cost
        }
    )  

    data_waterfall.replace(np.nan,0, inplace=True)
    return(data_waterfall)

def createWaterfallEChart(data_input):

    data = CreateWaterfallInput(data_input)

    options = {
        "title": False,
        # "tooltip": {
        #     "trigger": "axis",
        #     "axisPointer": {
        #         "type": "shadow"
        #     },
        #     "formatter": JsCode("function (params) { var tar = params[1]; var tar_value = Math.round(tar.data.value); var tar_perc = tar.data.perc.toFixed(2); var tar_perTon = Math.round(tar.data.perTon); return '<b>' + tar.name + '</b>' + ' : ' + tar_value.toLocaleString() + ' €' + '<br />' + tar_perc + ' % Revenue' + '<br />' + tar_perTon.toLocaleString() + ' €/MT'; }").js_code
        # },
        "grid":{
            'left':'2%',
            # 'right':'4%',
            # 'top': '4%',
            'bottom':'2%',
            'containLabel': 'false'
        },
        "xAxis": {
            "type": "category",
            "splitLine": {"show": False},
            "data": data.Name.tolist(),
            "axisLabel": {
                "rotate" : "70",
                "fontSize": "12"
            },
            "axisTick": {
                "show": False
            }  
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {
                "formatter": JsCode("function(value,index){ if (Math.abs(value) >= 1000000){ return value/1000000 + 'M' } else if (Math.abs(value) >= 1000){ return value/1000 + 'K' } else {return value} }").js_code
            }            
        },
        "series": [
            {
                "name": 'Placeholder',
                "type": 'bar',
                "stack": 'Total',
                "silent": True,
                "itemStyle": {
                    "borderColor": 'transparent',
                    "color": 'transparent'
                },
                "emphasis": {
                    "itemStyle": {
                        "borderColor": 'transparent',
                        "color": 'transparent'
                    }
                },               
                "data": data.placeholder.tolist()
            },
            {
                "name": 'Positive Revenue',
                "type": 'bar',
                "stack": 'Total',
                "data": data.positive_rev.tolist(),
                "color": "#005959",
                "label":{
                    "show": True,
                    "position": "top",
                    "fontSize" : "11",
                    "fontWeight" : "bolder"
                }
            },
            {
                "name": 'Negative Revenue',
                "type": 'bar',
                "stack": 'Total',
                "data": data.negative_rev.tolist(),
                "color": "#cb333b",
                "label":{
                    "show":True
                }
            },
            {
                "name": 'Negative Cost',
                "type": 'bar',
                "stack": 'Total',
                "data": data.negative_cost.tolist(),
                "color": "#cb333b",
                "label":{
                    "show":False
                }
            },
            {
                "name": 'Positive Cost',
                "type": 'bar',
                "stack": 'Total',
                "data": data.postive_cost.tolist(),
                "color": "#cb333b",
                "label":{
                    "show": False,
                    "position": "top",
                    "fontSize" : "11",
                    "fontWeight" : "bolder"
                }
            }                          
        ]        
    }

    return st_echarts(options=options, height="540px")

def threshold(data_raw, col_name):
    whole_data = data_raw
    whole_data = whole_data.rename(columns = {
        "TotalSalesValue":"Revenue",
        "QuantityInMT":"Sales In MT"
    })
    whole_data['ShipToCountry'] = whole_data['ShipToCountry'].replace('Czech Republic', 'Czechia')
        
    whole_data = whole_data.groupby('ShipToCountry').agg(**{col_name: (col_name, 'sum')}).reset_index()
    min_val = whole_data[col_name].min()
    max_val = whole_data[col_name].max()
    
    if min_val < 0:
        threshold_scale = [min_val] + np.linspace(0, max_val, 5).tolist()
    else:
        threshold_scale = np.linspace(min_val, max_val, 6).tolist()
    
    def custom_round(x):
        if col_name != "Sales In MT":
            if x < 0:
                return round(np.floor(x / 100000))*100
            elif x == 0:
                return 0
            else:
                return round(np.ceil(x / 1000000))*1000
        else:
            return round(np.ceil(x/1000))*1000

    rounded_scale = [custom_round(num) for num in threshold_scale]
    
    return rounded_scale



def createHeatmap(data, geo_data, col_name, bins):
    data['ShipToCountry'] = data['ShipToCountry'].replace('Czech Republic', 'Czechia')
    
    # filter and merge df into geo_json
    if col_name in ['CBM', 'CBMAI', 'EBITAI', 'GM']:
        profit_country = data.groupby('ShipToCountry').agg(
            Revenue=('Revenue', 'sum'),
            **{col_name: (col_name, 'sum')}
        ).reset_index().assign(
            value_thousand = lambda x: x[col_name]/1000,
            value_ratio = lambda x: round(x[col_name] * 100 / x.Revenue, 2)
        )
        profit_country['Revenue'] = profit_country['Revenue'].round(0)
        profit_country[col_name] = profit_country[col_name].round(0)
    else:
        profit_country = data.groupby('ShipToCountry').agg(
            **{col_name: (col_name, 'sum')}
        ).reset_index().assign(
            value_thousand = lambda x:  x[col_name]/1000 if col_name == 'Revenue' else x[col_name],
            value_ratio = lambda x: round(x[col_name] * 100 / x[col_name].sum(), 2)
        )
        profit_country[col_name] = profit_country[col_name].round(0)
        
    profit_country_dict = profit_country.set_index('ShipToCountry').to_dict('index') 

    enriched_features = []
    for feature in geo_data['features']:
        country_name = feature['properties']['name']
        if country_name in profit_country_dict:
            feature['properties'].update(profit_country_dict[country_name])
            enriched_features.append(feature)
    
    geo_data['features'] = enriched_features
    
    # create color, tooltip, legend
    style_tooltip ="""
                        background-color: #F0EFEF;
                        border: 1px solid black;
                        border-radius: 3px;
                        box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.75);
                        font-family: 'Helvetica', sans-serif;
                        font-size: 13px;
                    """
    if col_name in ['CBM', 'CBMAI', 'EBITAI', 'GM']:
        tooltip_f = folium.features.GeoJsonTooltip(
                    fields=['name', 'Revenue', col_name, 'value_ratio'], 
                    aliases=['Country:', 'Revenue (€)', f'{col_name} (€)', f'{col_name} on Revenue (%):'],
                    localize=True,
                    style=style_tooltip,
                    max_width=800
                )
        color_pallete = ["#D0474E", "#8db6b7", "#72a4a5", "#5c9696"  ,"#287474", "#005959"]
    else:
        tooltip_f = folium.features.GeoJsonTooltip(
                    fields=['name', col_name, 'value_ratio'], 
                    aliases=['Country:',  f'{col_name} (€)', f'Percentage on Total {col_name} (%):'],
                    localize=True,
                    style=style_tooltip,
                    max_width=800
                )
        color_pallete = ["#bed7d8", "#8db6b7", "#72a4a5", "#5c9696"  ,"#287474", "#005959"]
        
        
    bins = bins
    colorstep = LinearColormap(
        color_pallete,
        index = bins, vmin = min(bins), vmax = max(bins),
        caption = f"{col_name} (MT)" if col_name == "Sales In MT" else f"{col_name} (k€)"
        )
    
    m = folium.Map(location=[55.9754, 19], zoom_start=2.5, max_zoom = 1.5, tiles="cartodbpositron")
         
    style_f = lambda feature: {
        'fillColor': colorstep(feature['properties']['value_thousand']),
        "fillOpacity": 1,
        "color": "white", 
        "weight": 0.7
        } 

    folium.GeoJson(
        geo_data,
        style_function=style_f,
        highlight_function=lambda feature: {'weight': 1, 'color': '#ffffff', 'fillColor':'#005959', "fillOpacity": 0.8},
        tooltip = tooltip_f
        ).add_to(m)
    
    colorstep.add_to(m) #add legend
    Fullscreen().add_to(m)
    
    make_map_responsive = """
                        <style>
                        [title~="st.iframe"] { width: 96%} 
                        </style>
                        """ #do not delete white space before "width"
    st.markdown(make_map_responsive, unsafe_allow_html=True) 

    return folium_static(m)

########################################################################################################################################
########################################################################################################################################

def DownloadTopBleeders(data, profit_level, grouping_cols_for_download = ['Account','Segment','Material','MaterialDescription','Commodity','ProductGroup','ProductOrigin']):
    download_top_bleeders = data.groupby(grouping_cols_for_download)[['SalesInMT','Revenue', 'GM', 'S&D', 'CBM', 'CBMAI', 'EBITAI']].sum().sort_values(profit_level).reset_index()
    download_top_bleeders = download_top_bleeders.rename(columns = {'MaterialDescription':'Material Description', 'ProductGroup':'Product Group', 'ProductOrigin':'Product Origin', 'SalesInMT':'Sales In MT'})
    csv = download_top_bleeders.to_csv(index=False).encode('utf-8')
    st.download_button(
            label="Download Data",
            data=csv,
            file_name= 'top_bleeders_'+profit_level+'.csv',
            mime='text/csv',
        )
    pass

def TopBleedersTable_st(data, search_text):

    format_dict = {
        "SalesInMT": "{:,.0f}",
        "Revenue": "€ {:,.0f}",
        "GM": "€ {:,.0f}",
        "S&D": "€ {:,.0f}",
        "CBM": "€ {:,.0f}",
        "CBMAI": "€ {:,.0f}",
        "EBITAI": "€ {:,.0f}"
    }

    for col in format_dict:
        if col in data.columns:
            data[col] = data[col].map(lambda x: format_dict[col].format(x))

    with DataFrameSearch(
            dataframe=data,
            text_search=search_text,
            case_sensitive=False,
        ) as result:

        print(f"Type of result: {type(result)}")

        try:
            filtered_data = result if isinstance(result, pd.DataFrame) else result.data
        except AttributeError:
            st.error("Error processing the search results. Please check the DataFrameSearch function.")
            return
            
    pagination = st.container()

    bottom_menu = st.columns((4, 1, 1))
    with bottom_menu[2]:
        batch_size = st.selectbox("Page Size", options=[10, 25, 50], key="batch_size")

    with bottom_menu[1]:
        total_rows = len(filtered_data)
        total_pages = total_rows // batch_size
        if total_rows % batch_size > 0:
            total_pages += 1

        current_page = st.number_input(
            "Page", min_value=1, max_value=max(1, total_pages), step=1, key="current_page"
        )

    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}** ")

    start = (current_page - 1) * batch_size
    end = start + batch_size
    pagination_data = filtered_data.iloc[start:end]

    pagination.dataframe(pagination_data, use_container_width=True, hide_index=True,
                         column_config={"MaterialName": st.column_config.Column("Material"),
                                       "SalesInMT": st.column_config.Column("Sales In MT")})

    pass



########################################################################################################################################
########################################################################################################################################

def DownloadDetailedData(data, grouping_cols_for_download = ['Account','Segment','Material','MaterialDescription','Commodity','ProductGroup','ProductOrigin']):
    download_top_bleeders = data.groupby(grouping_cols_for_download)[['SalesInMT','Revenue', 'GM', 'S&D', 'CBM', 'CBMAI', 'EBITAI']].sum().sort_values('Revenue',ascending=False).reset_index()
    download_top_bleeders = download_top_bleeders.rename(columns = {'MaterialDescription':'Material Description', 'ProductGroup':'Product Group', 'ProductOrigin':'Product Origin', 'SalesInMT':'Sales In MT'})
    csv = download_top_bleeders.to_csv(index=False).encode('utf-8')
    st.download_button(
            label="Download Data",
            data=csv,
            file_name= 'detailed_data.csv',
            mime='text/csv',
            key="download_detailed"
        )
    pass

def DetailedTable_st(data, search_text):

    data = data.groupby(['Account', 'Commodity', 'MaterialName'])[['SalesInMT', 'Revenue', 'GM', 'S&D', 'CBM', 'CBMAI', 'EBITAI']].sum().sort_values('Revenue', ascending=False).reset_index()

    format_dict = {
        "SalesInMT": "{:,.0f}",
        "Revenue": "€ {:,.0f}",
        "GM": "€ {:,.0f}",
        "S&D": "€ {:,.0f}",
        "CBM": "€ {:,.0f}",
        "CBMAI": "€ {:,.0f}",
        "EBITAI": "€ {:,.0f}"
    }

    for col in format_dict:
        if col in data.columns:
            data[col] = data[col].map(lambda x: format_dict[col].format(x))

    with DataFrameSearch(
            dataframe=data,
            text_search=search_text,
            case_sensitive=False,
        ) as result:

        print(f"Type of result: {type(result)}")

        try:
            filtered_data = result if isinstance(result, pd.DataFrame) else result.data
        except AttributeError:
            st.error("Error processing the search results. Please check the DataFrameSearch function.")
            return
            
    pagination = st.container()

    bottom_menu = st.columns((4, 1, 1))
    with bottom_menu[2]:
        batch_size = st.selectbox("Page Size", options=[10, 25, 50, 100], key="batch_size_detailed")

    with bottom_menu[1]:
        total_rows = len(filtered_data)
        total_pages = total_rows // batch_size
        if total_rows % batch_size > 0:
            total_pages += 1

        current_page = st.number_input(
            "Page", min_value=1, max_value=max(1, total_pages), step=1, key="current_page_detailed"
        )

    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}** ")

    start = (current_page - 1) * batch_size
    end = start + batch_size
    pagination_data = filtered_data.iloc[start:end]

    pagination.dataframe(pagination_data, use_container_width=True, hide_index=True,
                         column_config={"MaterialName": st.column_config.Column("Material"),
                                       "SalesInMT": st.column_config.Column("Sales In MT")})

    pass    

def createValueBox(kpi,
                   total_nsv,
                   total_volume,
                   total_value,
                   color):
    
    with stylable_container(
        key='nsv_metric',
        css_styles="""
        {
            background-color: #ffffff;
            border-radius: 4px;
            text-align: center;
            padding-bottom: 15px;
            font-family: ''Helvetica Neue', sans-serif';
            box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.75);
        }
        """
        ):


        total_value_print = formatCurrency(total_value)

        perc_nsv = round(total_value*100/total_nsv, ndigits=1)
        per_unit = round(total_value/total_volume)

        string_name = "<b style='color: #302E2C; font-size: 15px; margin: 0; padding: 0; text-align: center;'>" + kpi + "</b>"
        string_total = "<b style='font-size: 30px; margin: 0; padding: 0; text-align: center; color: " + color + "'>" + total_value_print + "</b>"
        string_perc = "<text style='font-size: 13px; text-align: center; color: " + color + "'>" + str(perc_nsv) + " % Revenue | " + str(per_unit) + " €/MT</text>"

        html_content = """
            <div style = "margin: 0; padding: 0;">
                <div>%s</div>
                <div>%s</div>
                <div class="small-box-footer" style = "background-color: rgba(0, 0, 0, 0.1); 
                                                   padding: 0; 
                                                   margin: 0; 
                                                   position: relative;
                                                   display: block">
                    %s
                </div>
            </div>
        """ % (
            string_name,
            string_total,
            string_perc
        )

        st.markdown(html_content, unsafe_allow_html=True)

def createChartTimeView(data,
                        level_1,
                        level_2,
                        list_month):
    
    unit_dict = {
        "Sales In MT" : "MT", 
        "Revenue"     : "EUR", 
        "GM"          : "EUR", 
        "CBM"         : "EUR", 
        "CBMAI"       : "EUR", 
        "EBITAI"      : "EUR"
    }
    
    data.Month = data.Month.astype('category')
    data.Month = data.Month.cat.set_categories(list_month)
        
    data_chart = data.groupby(by = 'Month', as_index=False).agg('sum')
    data_chart['Average_1'] = data_chart[level_1].mean()
    title = level_1
    

    fig = make_subplots(specs=[[{"secondary_y": True}]])


    fig.add_trace(go.Scatter(x=data_chart['Month'],
                             y=data_chart[level_1],
                             mode='lines+text',
                             text=[level_1],
                             name=level_1,
                             textposition="top right",
                             marker=dict(color="#385D7F")),
                    secondary_y=False)

    avg_level_1 = 'Avg. ' + level_1

    fig.add_trace(go.Scatter(x=data_chart['Month'],
                             y=data_chart['Average_1'],
                             text=[avg_level_1],
                             name=avg_level_1,
                             mode='lines+text',
                             line={'dash':'dash'},
                             textposition="top right",
                             marker={'color': "rgba(56, 93, 127, 0.7)"}),
                    secondary_y=False,
                    )
    
    fig.update_yaxes(title_text=unit_dict[level_1], secondary_y=False)

    
    if level_2 != "":

        data_chart['Average_2'] = data_chart[level_2].mean()
    
        fig.add_trace(go.Scatter(x=data_chart['Month'],
                                y=data_chart[level_2],
                                mode='lines',
                                name=level_2,
                                text=level_2,
                                marker=dict(color="rgba(188, 188, 188, 0.9)")),
                    secondary_y=True)
        
        avg_level_2 = 'Avg. ' + level_2
        
        fig.add_trace(go.Scatter(x=data_chart['Month'],
                                y=data_chart['Average_2'],
                                name=avg_level_2,
                                text=[avg_level_2],
                                mode="lines",
                                line={'dash':'dash'},
                                marker=dict(color="rgba(188, 188, 188, 0.9)")),
                        secondary_y=True)   
        
        fig.update_yaxes(title_text=unit_dict[level_2], secondary_y=True)

        title = title + " vs. " + level_2

    title = title + " by Month"
    
    fig.update_layout(
        title={'text': title,
               'y': 0.9,
               'x': 0.5,
               'xanchor': 'center',
               'yanchor': 'top'},
        xaxis_title='Month',
        showlegend=False,
        hovermode='x unified',
        title_font=dict(size=24),
        yaxis2=dict(tickmode="sync"),
        height=800
    )

    fig.update_traces(
        mode="lines",
        hovertemplate="%{y:,.1f}"
    )



    return fig

