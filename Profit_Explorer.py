import streamlit as st
import pandas as pd
import util.helper_visualization_func as viz
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import numpy as np
import streamlit_highcharts as hct
from streamlit_extras.stylable_container import stylable_container
from util.create_sankey_chart import *
from util.create_3d_chart import *
from util.create_matrix import *
import json
import streamlit.components.v1 as components
import util.helper_profit_table_func as profit
from streamlit_option_menu import option_menu
import util.create_side_bar as sibr
import base64



# Set up page and data =============================================================

st.set_page_config(page_title = "Profit Explorer", 
                   layout="wide", 
                #    page_icon="data/CEL_icon_square_light_crop.png",
                   initial_sidebar_state="collapsed")

viz.local_css("styles_v1.2.css")
viz.format_page_element()
draw_sankey_supply_chain_flow = pd.read_excel("data/data_sankey_supply_chain_flow.xlsx")

@st.cache_data
def loadGeo():
    with open('data/WorldCountry.json', 'r') as f:
        geo_json = json.load(f)
    return geo_json


@st.cache_data
def loadInput():
    demo = True
    if demo:
        input = pd.read_csv('demo_sc_data_eu/final_profit_and_loss_transactions.csv')
        
    else:
        input = pd.read_csv('data/profit_by_month.csv')
    
    level = pd.read_csv('data/Facility_Level.csv')
    transfer_df = pd.read_csv('demo_sc_data_eu/InternalTransfer.csv')

    return input, level, transfer_df

# with open("data/Profit_Explorer_2.png", "rb") as img_file:
#     contents = img_file.read()
# data_url = base64.b64encode(contents).decode("utf-8")


# st.markdown(f"""
#     <img src="data:image/jpeg;base64,{data_url}" alt="local image" 
#          style="display: block; margin-left: 0; margin-right: auto; align: left;"
#          width="220px">
#     """, 
#     unsafe_allow_html=True)

input_df, level_df, transfer_df = loadInput()



legend_input = loadInput()
geo_json = loadGeo()
input_df['MaterialName'] = input_df.ProductID.astype(str) + " - " + input_df.ProductName
input_df['ShipToDescription'] = input_df.ShipToID.astype(str) + " - " + input_df.ShipToParty
input_df = input_df.assign(
    TotalSnD = lambda x: x.TotalStorageCost + x.TotalHandlingCost + x.TotalTransportCost
)
list_profitability_level = ['GM', 'CBM', 'CBMAI', 'EBITAI']
list_profit_include_volume = ["Sales In MT", "Revenue", "GM", "CBM", "CBMAI", "EBITAI"]

color_for_flow_dict = {
    'EU to EU Direct'   : "#C63D2F",
    'EU to EU Switch'   : "#FF9B50",
    'NZ Indirect'       : "#053B50",
    'NZ Direct EU'      : "#62B6B7", #     
    'NZ Direct Export'  : "#CBEDD5",
    'EU to Export'      : "#FFF2CC"
}

html_content = """
<p><strong>Terminologies:</strong>
    <ul>
        <li><strong>CBM:</strong> Contribution Before Marketing</li>
        <li><strong>IOC:</strong> Inventory on Capital</li>
        <li><strong>SG&A:</strong> Selling, General and Administrative Expenses</li>
        <li><strong>CBMAI:</strong> Contribution Before Marketing after IOC</li>
        <li><strong>EBIT:</strong> Earnings Before Interest and Taxes (CBM after SG&A)</li>
        <li><strong>EBITAI:</strong> Earnings Before Interest and Taxes (CBM after IOC and SG&A)</li>
    </ul></p>
    </div>
"""


# Sidebar ========================================================================================

with st.sidebar:

    # st.sidebar.image("data/CEL_Logo.png")
    # with open("data/CEL_Logo.png", "rb") as f:
    #     side_img = base64.b64encode(f.read()).decode("utf-8")

    # st.sidebar.markdown(f"""
    # <img src="data:image/png;base64,{side_img}" alt="local image" 
    #      style="display: block; margin-left: auto; margin-right: auto; align: left; margin-top:-35px;"
    #      width="180px">
    # """, 
    # unsafe_allow_html=True)    

    filtered_df, list_month_selected = sibr.create_side_bar(input_data=input_df)
    
# Nav Bar ===========================================================================================
            
nav_bar = option_menu(
    menu_title = None,
    options = ['Overview','Network', 'Map','Portfolio'],
    orientation = 'horizontal',
    default_index = 0,
    styles = {
        "container": {"background-color": "#ffffff"},
        "icon": {"font-size": "0px"},
        "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"}
    }
)      


with stylable_container(
    key='tabs',
    css_styles="""
    {
        top: 50px;
        padding-top: 10px;
    }
    """
    ):

    # Introduction tab (Scope & KPI) ===========================================================================================

    if nav_bar == 'Overview':
        cols_box_1 = st.columns(3)
        with cols_box_1[0]:

            viz.createValueBox(kpi="Revenue",
                        total_nsv=filtered_df.TotalSalesValue.sum(),
                        total_volume=filtered_df.QuantityInMT.sum(),
                        total_value=filtered_df.TotalSalesValue.sum(),
                        color="#005959")

        with cols_box_1[1]:

            viz.createValueBox(kpi="Gross Margin",
                        total_nsv=filtered_df.TotalSalesValue.sum(),
                        total_volume=filtered_df.QuantityInMT.sum(),
                        total_value=filtered_df.GM.sum(),
                        color="#005959")

        with cols_box_1[2]:

            viz.createValueBox(kpi="Storage & Distribution",
                        total_nsv=filtered_df.TotalSalesValue.sum(),
                        total_volume=filtered_df.QuantityInMT.sum(),
                        total_value=filtered_df.TotalSnD.sum(),
                        color="#005959") 

        cols_box_2 = st.columns(3)

        with cols_box_2[0]:

            viz.createValueBox(kpi="Contribution Before Marketing",
                        total_nsv=filtered_df.TotalSalesValue.sum(),
                        total_volume=filtered_df.QuantityInMT.sum(),
                        total_value=filtered_df.CBM.sum(),
                        color="#005959")

        with cols_box_2[1]:

            viz.createValueBox(kpi="CBM after IOC",
                        total_nsv=filtered_df.TotalSalesValue.sum(),
                        total_volume=filtered_df.QuantityInMT.sum(),
                        total_value=filtered_df.CBMAI.sum(),
                        color="#005959")
            
        with cols_box_2[2]:

            viz.createValueBox(kpi="EBIT after IOC",
                        total_nsv=filtered_df.TotalSalesValue.sum(),
                        total_volume=filtered_df.QuantityInMT.sum(),
                        total_value=filtered_df.EBITAI.sum(),
                        color="#005959")
            
        

        # with st.expander('Scope'):
        #     text_column, sankey_column = st.columns([0.35,0.65], gap="medium")
        #     with text_column:
        #         scope_project()

        #     with sankey_column:

        #         sankey_chart_SCF = create_sankey_chart(data=draw_sankey_supply_chain_flow, 
        #                                                 originCol="From", 
        #                                                 destinationCol="To",
        #                                                 quantityCol="Quantity", 
        #                                                 categoryCol="SupplyChainFlow", 
        #                                                 colorDict=color_for_flow_dict,
        #                                                 levelsMapping=level_df, 
        #                                                 unit="ton",
        #                                                 fontName="Helvetica", 
        #                                                 fontSize=10)
                
        #         st.plotly_chart(sankey_chart_SCF, use_container_width=True)        

        col_select_level = st.columns([0.2,0.3,0.3,0.2], gap="medium")
        
        with col_select_level[1]:

            st.markdown("<h5 style='font-size: 20px; margin-top: 5px; text-align: left;'>Primary KPI</h5>"
                        , unsafe_allow_html=True)        
            
            selected_level_1 = st.selectbox(
                label="Which level you want to see",
                options=list_profit_include_volume,
                label_visibility='collapsed'
            )

        with col_select_level[2]:

            st.markdown("<h5 style='font-size: 20px; margin-top: 5px; text-align: left;'>Secondary KPI</h5>"
                        , unsafe_allow_html=True)   
            
            list_profit_include_volume_after_selection = [i for i in list_profit_include_volume if i != selected_level_1]     
            list_profit_include_volume_after_selection = np.concatenate(([""], list_profit_include_volume_after_selection), axis=0)

            selected_level_2 = st.selectbox(
                label="Which level you want to see",
                options=list_profit_include_volume_after_selection,
                index=1,
                label_visibility='collapsed'
            )

        timeview_input_data = filtered_df.rename(columns = {
            "TotalSalesValue":"Revenue",
            "QuantityInMT":"Sales In MT"
        })

        col_chart_timeview = st.columns([0.1,0.9,0.1], gap="medium")

        with col_chart_timeview[1]:

            fig_time_view = viz.createChartTimeView(data=timeview_input_data,
                                                    level_1=selected_level_1,
                                                    level_2=selected_level_2,
                                                    list_month=list_month_selected)

            st.plotly_chart(fig_time_view, use_container_width=True)  
        
        with st.columns([0.4,0.7])[1]:
            st.markdown(html_content, unsafe_allow_html=True)
 

    # Network Sankey filterable Tab ========================================================================================

    if nav_bar == 'Network':

        level_df_adjusted = level_df.copy()
        level_df_adjusted.loc[level_df_adjusted['label'] == 'Schiphol Airport - NL', 'level'] = 3
        categories = level_df_adjusted['label']

        grouped_df = filtered_df[['FacilityName', 'Category', 'ShipToCountry', 'QuantityInMT']].groupby(['FacilityName', 'Category', 'ShipToCountry'], as_index=False).sum()
        # grouped_df['FacilityType'] = pd.Categorical(grouped_df['FacilityType'], categories=categories, ordered=True)
        # grouped_df['ShipToCountry'] = pd.Categorical(grouped_df['ShipToCountry'], categories=categories, ordered=True)


        grouped_df = grouped_df.sort_values(by=['FacilityName', 'Category', 'ShipToCountry', 'QuantityInMT'])
        

        sankey_chart_filter, nodes = create_sankey_chart(grouped_df, 
                                        originCol="FacilityName", 
                                        destinationCol="ShipToCountry",
                                        quantityCol="QuantityInMT", 
                                        categoryCol="Category")
        
        st.plotly_chart(sankey_chart_filter, use_container_width=True)

    # P&L Tab ====================================================================================
            
    # if nav_bar == 'P&L':
    #     # st.markdown("""
    #     #             <div style="font-size: 40px; font-family: 'HelveticaNeue-Light', Helvetica, Arial, sans-serif; text-align: center; margin-top: 5px; ">
    #     #             <p><strong>Profit & Loss Waterfall</strong></p>
    #     #             </div>     
    #     #             """
    #     #             , unsafe_allow_html=True)
        
    #     viz.createWaterfallChart(filtered_df)
    #     # viz.createWaterfallEChart(filtered_df)    

    #     with st.columns([0.4,0.7])[1]:
    #             st.markdown(html_content, unsafe_allow_html=True)

    # Map Tab ====================================================================================
    if nav_bar == 'Map':
        # st.markdown("""
        #                 <div style="font-size: 40px; font-family: 'HelveticaNeue-Light', Helvetica, Arial, sans-serif; text-align: center; margin-top: 5px; ">
        #                 <p><strong>Performance by Country</strong></p>
        #                 </div>   
        #                 """
        #                 , unsafe_allow_html=True)
        with stylable_container(
            key='select_map',
            css_styles="""
                {
                    background-color: #ffffff;
                    padding-bottom: 0px;
                    font-family: 'Helvetica', sans-serif;
                }
                .stRadio > div {
                    margin-top: -15px;
                    margin-bottom: -30px;
                    padding-bottom: 0px;
                    text-align: center;
                }
                .stRadio [role=radiogroup]{
                    align-items: center;
                    justify-content: center;
                }
                """
            ):
        
            map_level = st.radio(
                key="map_level",
                label='map',
                options=["Sales In MT", "Revenue", "GM", "CBM", "CBMAI", "EBITAI"],
                horizontal = True,
                index=3,
                label_visibility = "collapsed"
            )  

            map_input_data = filtered_df.rename(columns = {
                "TotalSalesValue":"Revenue",
                "QuantityInMT":"Sales In MT"
            })
            @st.cache_data
            def getBinsMap(data_raw,col_name):
                bins = viz.threshold(data_raw, col_name)
                return bins
            
            bins = getBinsMap(input_df, map_level)
            viz.createHeatmap(data = map_input_data, geo_data=geo_json, col_name = map_level, bins = bins)
            
            with st.columns([0.4,0.7])[1]:
                st.markdown(html_content, unsafe_allow_html=True)
    
    
    # Profit Matrix Tab ========================================================================================

    if nav_bar == 'Portfolio':
        col_profit = st.columns([0.2,0.2,0.4,0.2],gap="medium")
        with col_profit[1]:
            st.markdown("<h5 style='font-size: 18px; margin-top: 5px; text-align: left;'>" + "Profitability Level" + "</h5>", unsafe_allow_html=True)
            Profit_level = st.selectbox(
            label='Choose Profitability Level',
            options=list_profitability_level,
            index = 0,
            label_visibility='collapsed')    

        sorted_label_list,threshold_matrix = CreateInputMatrixSlider(
                                                                    filtered_df = filtered_df,
                                                                    Profit_level = Profit_level,
                                                                    group_cols=["Account", "Category", "MaterialName"])
        with col_profit[2]:
            if len(sorted_label_list) > 1:
                st.markdown("<h5 style='font-size: 18px; margin-top: 5px; text-align: left;'>"+ Profit_level + " Percentage" + "</h5>", unsafe_allow_html=True)
                selected_legend = st.select_slider(
                    'Select a range',
                    options=sorted_label_list,
                    value=(sorted_label_list[0], sorted_label_list[len(sorted_label_list)-1]),
                    label_visibility='collapsed')
            else:
                # st.write(sorted_label_list) 
                selected_legend = sorted_label_list



        # st.write(type(neg_table))
                
        col_summary_table = st.columns([0.3,0.6,0.3],gap="medium")

        with col_summary_table[1]:

            neg_table = create_summary_table_for_matrix(data_input=filtered_df,
                                                        profit_level=Profit_level,
                                                        threshold_matrix = threshold_matrix,
                                                        list_label= sorted_label_list,
                                                        percent_range = selected_legend,
                                                        base_group_cols=["Account", "Category", "MaterialName"], 
                                                        material_group_cols=["Category", "MaterialName"], 
                                                        account_group_cols=["Account"],
                                                        main_y_col='Account', 
                                                        main_x_col='MaterialName')

            st.dataframe(neg_table, hide_index=True, use_container_width=True)


        matrix = CreateMatrix(data_input = filtered_df,
                            profit_level= Profit_level,
                            list_label= sorted_label_list,
                            threshold_matrix = threshold_matrix,
                            percent_range = selected_legend,
                            base_group_cols=["Account", "Category", "MaterialName"], 
                            material_group_cols=["Category", "MaterialName"], 
                            account_group_cols=["Account"],
                            main_y_col='Account', 
                            main_x_col='MaterialName')
        
        st.plotly_chart(matrix,use_container_width=True)


        with st.columns([0.4,0.7])[1]:

            st.markdown(html_content, unsafe_allow_html=True)       

    # 3d Matrix Tab ========================================================================================
        
    # if nav_bar == 'Customers':
    #     if "initial_submit" not in st.session_state:
    #         st.session_state['initial_submit'] = True

    #     with st.form("form_3d"):
    #         form_col = st.columns([0.42,0.45,0.13],gap = 'small')
    #         with form_col[1]:
    #             st.markdown("<h5 style='font-size: 20px; margin-top: 5px; text-align: left;'>" + "Axis (X,Y,Z)" + "</h5>", unsafe_allow_html=True)
    #             axis_order = st.multiselect(
    #                 label = "Choose axis order",
    #                 options = ['CBM','CBM Percentage',"Sales In MT",'Revenue','Segment'],
    #                 default = ['CBM Percentage','Revenue','CBM'],
    #                 max_selections = 3,
    #                 key = "axis_order",
    #                 label_visibility = "collapsed"
    #             )
    #             submit_button = st.form_submit_button("Update")
    #         with form_col[0]:
    #             st.write("<h5 style='font-size: 15px; margin-top: 46px; text-align: left;'>" + "Please choose the three axes in the box based on the order X, Y, Z." + "</h5>", unsafe_allow_html=True)
    #             st.write("<h5 style='font-size: 15px; margin-top: -15px; text-align: left;'>" + "Click update to draw the new chart." + "</h5>", unsafe_allow_html=True)

    #     if st.session_state.initial_submit:
    #         submitted = st.session_state.initial_submit
    #     else:
    #         submitted = submit_button

    #     blank_column_3,chart3d_column_1, blank_column_4= st.columns([0.2,0.6,0.2], gap="medium")
    #     if submitted:
    #         # st.session_state.initial_submit = False
    #         if len(axis_order) == 3:
    #             st.session_state.axis_order_state = axis_order
    #             with chart3d_column_1:
    #                 chart_3d = Create3DChart(data= filtered_df,axis_order= st.session_state.axis_order_state)
    #                 st.plotly_chart(chart_3d, use_container_width=True)        
    #         else:
    #             st.warning('You have to choose exactly 3 axes', icon="⚠️")    

    #     with st.columns([0.4,0.7])[1]:

    #         st.markdown(html_content, unsafe_allow_html=True)     


    # Table Tab ========================================================================================

    # if nav_bar == 'Details':
    #     # table_tabs = ['List of Bleeders', 'Detailed Data']
    #     # table_tab= st.tabs([s.center(whitespace,"\u2001") for s in table_tabs])
    #     with st.expander('List of Bleeders'):
    #         if 'profit_level' not in st.session_state:
    #             st.session_state['profit_level'] = 'CBM'

    #         col_tab_3 = st.columns([0.3,0.7],gap="large")

    #         with col_tab_3[0]:
    #             st.markdown("<h5 style='font-size: 20px; margin-top: 5px; text-align: left;'>" + "Profitability Level" + "</h5>", unsafe_allow_html=True)
    #             profit_level = st.selectbox(
    #             label='Choose Profitability Level',
    #             options=list_profitability_level,
    #             index = 0,
    #             label_visibility='collapsed',
    #             key = 'profit_level_2')

    #         with col_tab_3[1]:
    #             st.markdown("<h5 style='font-size: 20px; margin-top: 5px; text-align: left;'>" + "Search" + "</h5>", unsafe_allow_html=True)
    #             search_text = st.text_input("Search", label_visibility="collapsed", placeholder="Insert")

    #         filtered_df.rename(columns={'TotalSnD': 'S&D', 'QuantityInMT': 'SalesInMT', 'TotalSalesValue': 'Revenue'}, inplace=True)

    #         select_profit_df = filtered_df.copy()

    #         if st.session_state.profit_level != profit_level:
    #             st.session_state.profit_level = profit_level

    #         select_profit_df = select_profit_df.loc[select_profit_df[profit_level] <= 0]

    #         top_bleeders_table = select_profit_df.groupby(['Account', 'MaterialName'])[['SalesInMT', 'Revenue', 'GM', 'S&D', 'CBM', 'CBMAI', 'EBITAI']].sum().sort_values(profit_level).reset_index()

    #         viz.DownloadTopBleeders(data=select_profit_df, profit_level=profit_level)
    #         viz.TopBleedersTable_st(top_bleeders_table, search_text=search_text)

    #         with st.columns([0.2,0.8])[1]:

    #             st.markdown(html_content, unsafe_allow_html=True)     

    #         st.subheader("")


    #     with st.expander('Detailed Data'):

    #         col_tab_4 = st.columns([0.2,0.8],gap="medium")

    #         with col_tab_4[0]:
    #             st.subheader(" ")
    #             st.subheader(" ")
    #             viz.DownloadDetailedData(filtered_df)

    #         with col_tab_4[1]:
    #             st.markdown("<h5 style='font-size: 20px; margin-top: 5px; text-align: left;'>" + "Search" + "</h5>", unsafe_allow_html=True)
    #             search_text = st.text_input("Search", label_visibility="collapsed", placeholder="Insert", key="search_detailed")

    #         viz.DetailedTable_st(filtered_df, search_text)    