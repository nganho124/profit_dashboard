import pandas as pd
import streamlit as st
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder, GridUpdateMode, ColumnsAutoSizeMode
from df_global_search import DataFrameSearch

# def ProfitTable(data, 
#                 grouping_columns=None, 
#                 value_columns=['SalesInMT','Revenue', 'GM', 'S&D', 'CBM', 'CBMAI', 'EBITAI'], 
#                 lowest_level=False,
#                 download_data=True,
#                 profit_level=None):
#     if grouping_columns is None:
#         grouping_columns = ['Account', 'Commodity', 'ABCClass', 'MaterialName']  # Default grouping columns
#     all_columns = grouping_columns + value_columns

#     data_filtered = data.groupby(grouping_columns)[value_columns].sum().reset_index().sort_values('Revenue', ascending = False)


#     gb = GridOptionsBuilder.from_dataframe(data_filtered)
#     gridOptions = gb.build()

#     # Configure grid options
#     gb.configure_grid_options(suppressAggFuncInHeader=True,
#                               groupDisplayType='multipleColumns',
#                             #   rowGroupPanelShow='always',
#                               suppressDragLeaveHidesColumns=True,
#                               pagination=True,
#                               paginationPageSize=10,
#                               autoSizeStrategy ='fitCellContents',
#                               filter = True)

#     currencyFormatter_euro = JsCode("""
#     function(params) {
#         if (params.value != null) {
#             return '\u20AC ' + params.value.toLocaleString('en-US', {
#                 minimumFractionDigits: 1,
#                 maximumFractionDigits: 1
#             });
#         } else {
#             return '';
#         }
#     };
#     """).js_code

#     currencyFormatter = JsCode("""
#     function(params) {
#         if (params.value != null) {
#             return params.value.toLocaleString('en-US', {
#                 minimumFractionDigits: 1,
#                 maximumFractionDigits: 1
#             });
#         } else {
#             return '';
#         }
#     };
#     """).js_code


#     # Dynamically set the grouping columns
#     columnDefs = []
#     if lowest_level == False:
#         for col in all_columns:
#             colDef = {"field": col}
#             if col in grouping_columns[:-1]:
#                 colDef.update({'rowGroup': True, 'enableRowGroup': True, 'hide': True, 'filter': 'agTextColumnFilter'})
#             elif col in value_columns:
#                 if col == "SalesInMT":
#                     colDef.update({'aggFunc': 'sum', "valueFormatter": currencyFormatter})
#                 else:
#                     colDef.update({'aggFunc': 'sum', "valueFormatter": currencyFormatter_euro})
#                 if col == 'Revenue' and profit_level is None:
#                     colDef.update({'sort': 'desc'}) 
#                 elif col == profit_level and profit_level is not None:
#                     colDef.update({'sort': 'asc'}) 
#             columnDefs.append(colDef)
#     else:
#         for col in all_columns:
#             colDef = {"field": col,'filter': 'agTextColumnFilter'}
#             if col in value_columns:
#                 if col == "SalesInMT":
#                     colDef.update({'aggFunc': 'sum', "valueFormatter": currencyFormatter})
#                 else:
#                     colDef.update({'aggFunc': 'sum', "valueFormatter": currencyFormatter_euro})
#                 if col == profit_level:
#                     colDef.update({'sort': 'asc'}) 
#             columnDefs.append(colDef)

#     gridOptions["columnDefs"] = columnDefs
#     gridOptions["defaultColDef"] = {"flex": 1, 
#                                     'minWidth': 100, 
#                                     'sortable': True,
#                                     'filter': True,
#                                     }
    
#     gridOptions["autoGroupColumnDef"] = {
#         "minWidth": 150,
#         "cellRendererParams": {"suppressCount": True},
#         'resizable': True
#     }

#     ##### Autosize columns to fit content
#     autoSizeColumns = JsCode("""
#     function(params) {
#         setTimeout(function() {
#             var allColumnIds = [];
#             params.columnApi.getAllColumns().forEach(function(column) {
#                 allColumnIds.push(column.colId);
#             });
#             params.columnApi.autoSizeColumns(allColumnIds, false);
#         }, 1000); // Increased timeout
#     }
#     """).js_code

#     gridOptions["onGridReady"] = autoSizeColumns
#     gridOptions["onFirstDataRendered"] = autoSizeColumns
#     gridOptions["onModelUpdated"] = autoSizeColumns  # Trigger on data update
#     # gridOptions["onGridSizeChanged"] = autoSizeColumns  # Trigger on grid resize
#     #####

#     AgGrid(
#         data_filtered,
#         gridOptions=gridOptions,
#         fit_columns_on_grid_load=False,
#         allow_unsafe_jscode=True,
#         theme="alpine",
#         enable_enterprise_modules=True,
#         update_mode='SELECTION_CHANGED'
#     )

#     if download_data == True:

#         def convert_df_to_csv(df):
#             return df.to_csv(index=False).encode('utf-8')
        
#         csv = convert_df_to_csv(data_filtered)

#         st.download_button(
#             label="Download Data",
#             data=csv,
#             file_name='data.csv',
#             mime='text/csv',
#         )



##########################################################################################################################################
##########################################################################################################################################
        

def TopBleedersTable(data, 
                     grouping_columns=['Account','MaterialName'], 
                     value_columns=['SalesInMT','Revenue', 'GM', 'S&D', 'CBM', 'CBMAI', 'EBITAI'], 
                     profit_level=""):
    
    all_columns = grouping_columns + value_columns

    data_filtered = data.groupby(grouping_columns)[value_columns].sum().reset_index().sort_values('Revenue', ascending = False)

    gb = GridOptionsBuilder.from_dataframe(data_filtered)
    
    gb.configure_default_column(flex=1,
                                min_column_width=100,
                                sortable=True,
                                filterable=True,
                                floatingFilter=True
                                )

    gb.configure_grid_options(suppressAggFuncInHeader=True,
                              groupDisplayType='multipleColumns',
                              suppressDragLeaveHidesColumns=True,
                              pagination=True,
                              paginationPageSize=10,
                              autoSizeStrategy ='fitCellContents')

    currencyFormatter_euro = JsCode("""
    function(params) {
        if (params.value != null) {
            return '\u20AC ' + params.value.toLocaleString('en-US', {
                minimumFractionDigits: 1,
                maximumFractionDigits: 1
            });
        } else {
            return '';
        }
    };
    """).js_code

    currencyFormatter = JsCode("""
    function(params) {
        if (params.value != null) {
            return params.value.toLocaleString('en-US', {
                minimumFractionDigits: 1,
                maximumFractionDigits: 1
            });
        } else {
            return '';
        }
    };
    """).js_code


    # Dynamically set the grouping columns
    columnDefs = []
    for col in all_columns:
        colDef = {"field": col}
        if col == grouping_columns[-1]:
            colDef.update({'filter': 'agMultiColumnFilter'})
        elif col in grouping_columns[:-1]:
            colDef.update({'rowGroup': True, 'enableRowGroup': True, 'hide': True, 'filter': 'agMultiColumnFilter'})
        elif col in value_columns:
            if col == "SalesInMT":
                colDef.update({'aggFunc': 'sum', "valueFormatter": currencyFormatter, 'filter':False})
            else:
                colDef.update({'aggFunc': 'sum', "valueFormatter": currencyFormatter_euro, 'filter':False})
            if col == 'Revenue' and profit_level is None:
                colDef.update({'sort': 'desc'}) 
            elif col == profit_level and profit_level is not None:
                colDef.update({'sort': 'asc'}) 
        columnDefs.append(colDef)
    

    gridOptions = gb.build()

    gridOptions["columnDefs"] = columnDefs
       
    gridOptions["autoGroupColumnDef"] = {
        "minWidth": 150,
        "cellRendererParams": {"suppressCount": True},
        'resizable': True,
        'filter': 'agGroupColumnFilter'
    }

    ##### Autosize columns to fit content
    autoSizeColumns = JsCode("""
    function(params) {
        setTimeout(function() {
            var allColumnIds = [];
            params.columnApi.getAllColumns().forEach(function(column) {
                allColumnIds.push(column.colId);
            });
            params.columnApi.autoSizeColumns(allColumnIds, false);
        }, 1000); // Increased timeout
    }
    """).js_code

    gridOptions["onGridReady"] = autoSizeColumns
    gridOptions["onFirstDataRendered"] = autoSizeColumns
    gridOptions["onModelUpdated"] = autoSizeColumns  # Trigger on data update
    # gridOptions["onGridSizeChanged"] = autoSizeColumns  # Trigger on grid resize
    #####
        

    AgGrid(
        data_filtered,
        gridOptions=gridOptions,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        theme="alpine",
        enable_enterprise_modules=True,
        update_mode='SELECTION_CHANGED'
    )


###########################################################################################
###########################################################################################        

def DetailedData(data, 
                grouping_columns=['Account', 'Commodity', 'ABCClass', 'MaterialName'], 
                value_columns=['SalesInMT','Revenue', 'GM', 'S&D', 'CBM', 'CBMAI', 'EBITAI'],
                download_data=True):
    
        
    all_columns = grouping_columns + value_columns

    data_filtered = data.groupby(grouping_columns)[value_columns].sum().reset_index().sort_values('Revenue', ascending = False)

    if download_data == True:

        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        
        csv = convert_df_to_csv(data_filtered)

        st.download_button(
            label="Download Data",
            data=csv,
            file_name='data.csv',
            mime='text/csv',
        )

    gb = GridOptionsBuilder.from_dataframe(data_filtered)
    
    gb.configure_default_column(flex=1,
                                min_column_width=100,
                                sortable=True,
                                filterable=True,
                                floatingFilter=True
                                )

    gb.configure_grid_options(suppressAggFuncInHeader=True,
                              groupDisplayType='multipleColumns',
                              suppressDragLeaveHidesColumns=True,
                              pagination=True,
                              paginationPageSize=10,
                              autoSizeStrategy ='fitCellContents')

    currencyFormatter_euro = JsCode("""
    function(params) {
        if (params.value != null) {
            return '\u20AC ' + params.value.toLocaleString('en-US', {
                minimumFractionDigits: 1,
                maximumFractionDigits: 1
            });
        } else {
            return '';
        }
    };
    """).js_code

    currencyFormatter = JsCode("""
    function(params) {
        if (params.value != null) {
            return params.value.toLocaleString('en-US', {
                minimumFractionDigits: 1,
                maximumFractionDigits: 1
            });
        } else {
            return '';
        }
    };
    """).js_code


    # Dynamically set the grouping columns
    columnDefs = []
    for col in all_columns:
        colDef = {"field": col}
        if col == grouping_columns[-1]:
            colDef.update({'filter': 'agMultiColumnFilter', 'headerName':'Material'})
        elif col in grouping_columns[:-1]:
            colDef.update({'rowGroup': True, 'enableRowGroup': True, 'hide': True, 'filter': 'agMultiColumnFilter'})
        elif col in value_columns:
            if col == "SalesInMT":
                colDef.update({'aggFunc': 'sum', "valueFormatter": currencyFormatter, 'filter':False})
            else:
                colDef.update({'aggFunc': 'sum', "valueFormatter": currencyFormatter_euro, 'filter':False})
            if col == 'Revenue':
                colDef.update({'sort': 'desc'}) 
        columnDefs.append(colDef)
    

    gridOptions = gb.build()

    gridOptions["columnDefs"] = columnDefs
       
    gridOptions["autoGroupColumnDef"] = {
        "minWidth": 150,
        "cellRendererParams": {"suppressCount": True},
        'resizable': True,
        'filter': 'agGroupColumnFilter'
    }

    ##### Autosize columns to fit content
    autoSizeColumns = JsCode("""
    function(params) {
        setTimeout(function() {
            var allColumnIds = [];
            params.columnApi.getAllColumns().forEach(function(column) {
                allColumnIds.push(column.colId);
            });
            params.columnApi.autoSizeColumns(allColumnIds, false);
        }, 1000); // Increased timeout
    }
    """).js_code

    gridOptions["onGridReady"] = autoSizeColumns
    gridOptions["onFirstDataRendered"] = autoSizeColumns
    gridOptions["onModelUpdated"] = autoSizeColumns  # Trigger on data update
    # gridOptions["onGridSizeChanged"] = autoSizeColumns  # Trigger on grid resize

    return data_filtered, gridOptions

########################################################################################################################################
########################################################################################################################################


        

# def draw_agrid(data, key):
#     data_filtered, gridOptions = DetailedData(data, 
#                                               grouping_columns=['Account', 'Commodity', 'ABCClass', 'MaterialName'], 
#                                               value_columns=['SalesInMT','Revenue', 'GM', 'S&D', 'CBM', 'CBMAI', 'EBITAI'],
#                                               download_data=True)

#     return AgGrid(data_filtered, gridOptions=gridOptions, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
#                   fit_columns_on_grid_load=False, allow_unsafe_jscode=True, theme="alpine",
#                   enable_enterprise_modules=True,
#                   update_mode='SELECTION_CHANGED', key = key
#                   )



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
        "SalesInMT": "{:,.1f}",
        "Revenue": "€ {:,.1f}",
        "GM": "€ {:,.1f}",
        "S&D": "€ {:,.1f}",
        "CBM": "€ {:,.1f}",
        "CBMAI": "€ {:,.1f}",
        "EBITAI": "€ {:,.1f}"
    }

    for col in format_dict:
        if col in data.columns:
            data[col] = data[col].map(lambda x: format_dict[col].format(x))

    with DataFrameSearch(
            dataframe=data,
            text_search=search_text,
            case_sensitive=True,
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
        "SalesInMT": "{:,.1f}",
        "Revenue": "€ {:,.1f}",
        "GM": "€ {:,.1f}",
        "S&D": "€ {:,.1f}",
        "CBM": "€ {:,.1f}",
        "CBMAI": "€ {:,.1f}",
        "EBITAI": "€ {:,.1f}"
    }

    for col in format_dict:
        if col in data.columns:
            data[col] = data[col].map(lambda x: format_dict[col].format(x))

    with DataFrameSearch(
            dataframe=data,
            text_search=search_text,
            case_sensitive=True,
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





    

    