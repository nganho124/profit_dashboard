import pandas as pd
import numpy as np 
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import math




def create_palette_matrix(threshold_matrix):

    # Sort the threshold matrix to handle unordered inputs
    sorted_thresholds = sorted(threshold_matrix)

    # Label and color for NA values
    labels_matrix = ["No Revenue"]
    color_matrix = ["#BABABA"]

    # Label and color for values below the first threshold
    labels_matrix.append("Lower than " + str(math.floor(sorted_thresholds[0])) + "%")
    color_matrix.append("#CB333B")

    # Labels and colors for values in between thresholds
    mid_range_color = ["#abf7b1","#05E177"]
    for i in range(1, len(sorted_thresholds)):
        label = "From " + str(math.floor(sorted_thresholds[i-1])) + "%" + " to " + str(math.floor(sorted_thresholds[i])) + "%"
        labels_matrix.append(label)
        color_matrix.append(mid_range_color[i-1])

    # Label and color for values above the last threshold
    labels_matrix.append("Above " + str(math.floor(sorted_thresholds[-1])) + "%")
    color_matrix.append("#11772D")


    return labels_matrix,color_matrix

def AssignLabel(value, threshold, label):
    # Handle the special case of -np.inf
    if value == -np.inf:
        return label[0]  # Assuming the first label is for 'No Revenue' or equivalent

    # Iterate over the thresholds to determine the label
    for i in range(len(threshold)):
        if value < threshold[i]:
            return label[i+1]
    
    # If value is not less than any of the thresholds, it falls into the last category
    return label[-1]  # Assuming the last label is for values above the highest threshold

def AssignColor(value,threshold,color):
    # Handle the special case of -np.inf
    if value == -np.inf:
        return color[0]  # Assuming the first label is for 'No Revenue' or equivalent

    # Iterate over the thresholds to determine the label
    for i in range(len(threshold)):
        if value < threshold[i]:
            return color[i+1]
    
    # If value is not less than any of the thresholds, it falls into the last category
    return color[-1]  # Assuming the last label is for values above the highest threshold    


def SummaryMatrixData (data_input, profit_level, group_cols):
    output = data_input.groupby(
        group_cols,
        as_index = False
    ).agg(
        {'NSV':'sum',
         profit_level:'sum'}
    ).assign(
        Percent = lambda x: round(x[profit_level]*100/x.NSV, ndigits= 2)
    )
    return(output)



import pandas as pd

def ProcessMatrixData(data_input, profit_level, list_label, percent_range, 
                      threshold_matrix, labels_matrix, color_matrix,
                      base_group_cols=None, 
                      material_group_cols=None, 
                      account_group_cols=None,
                      main_y_col='Account', 
                      main_x_col='MaterialName'):

    # 1. Set defaults if no custom groups are provided (Backward Compatibility)
    if base_group_cols is None:
        base_group_cols = ['Account', 'ProductOrigin', 'Commodity', 'Material', 'MaterialName']
    if material_group_cols is None:
        material_group_cols = ['Material', 'MaterialName', 'Commodity', 'ProductOrigin']
    if account_group_cols is None:
        account_group_cols = ['Account']

    data_grp_prt_mtl = data_input.rename(columns={'TotalSalesValue': 'NSV'})

    # 2. Create summary data by base dimensions
    data_grp_prt_mtl = SummaryMatrixData(data_grp_prt_mtl, profit_level, base_group_cols)
    data_grp_prt_mtl['Label'] = data_grp_prt_mtl['Percent'].apply(lambda x: AssignLabel(x, threshold_matrix, labels_matrix))
    data_grp_prt_mtl['Color'] = data_grp_prt_mtl['Percent'].apply(lambda x: AssignColor(x, threshold_matrix, color_matrix))

    # Filter by percentage range
    if percent_range is not None:
        if len(percent_range) > 1:
            idx_start = list_label.index(percent_range[0])
            idx_end = list_label.index(percent_range[1]) + 1
            valid_labels = list_label[idx_start:idx_end]
            data_grp_prt_mtl = data_grp_prt_mtl[data_grp_prt_mtl['Label'].isin(valid_labels)]    
        elif len(percent_range) == 1:
            data_grp_prt_mtl = data_grp_prt_mtl[data_grp_prt_mtl['Label'].isin(percent_range)]

    data_input_processed = data_grp_prt_mtl.copy(deep=True)

    # 3. Create summary data by X-Axis (Material)
    summary_material = SummaryMatrixData(data_grp_prt_mtl, profit_level, material_group_cols).sort_values(
        by=profit_level, ascending=True
    )
    # Dynamically assign the Y-axis label to the Material summary
    summary_material[main_y_col] = "Summary by Materials"
    
    summary_material['Label'] = summary_material['Percent'].apply(lambda x: AssignLabel(x, threshold_matrix, labels_matrix))
    summary_material['Color'] = summary_material['Percent'].apply(lambda x: AssignLabel(x, threshold_matrix, color_matrix)) # Assuming AssignColor was intended here based on previous logic

    # 4. Create summary data by Y-Axis (Account/Customer)
    summary_customer = SummaryMatrixData(data_grp_prt_mtl, profit_level, account_group_cols).sort_values(
        by=profit_level, ascending=False
    )
    
    # Dynamically fill the missing X-Axis columns for the Customer summary
    for col in material_group_cols:
        if col == main_x_col:
            summary_customer[col] = "Summary by Customers"
        elif col not in summary_customer.columns:
            summary_customer[col] = "Summary"

    # Set Categorical Order
    summary_customer[main_y_col] = pd.Categorical(summary_customer[main_y_col], categories=summary_customer[main_y_col].unique())
    summary_customer['Label'] = summary_customer['Percent'].apply(lambda x: AssignLabel(x, threshold_matrix, labels_matrix))
    summary_customer['Color'] = summary_customer['Percent'].apply(lambda x: AssignColor(x, threshold_matrix, color_matrix))

    # 5. Combine all data
    data_input_chart = data_input_processed.copy()
    
    # Dynamically apply categories to the main dataset so the chart plots in the correct sorted order
    data_input_chart[main_y_col] = pd.Categorical(data_input_chart[main_y_col], categories=summary_customer[main_y_col].unique())
    data_input_chart[main_x_col] = pd.Categorical(data_input_chart[main_x_col], categories=summary_material[main_x_col].unique())

    # Concat
    data_input_chart = pd.concat([summary_customer, data_input_chart], ignore_index=True)
    data_input_chart = pd.concat([summary_material, data_input_chart], ignore_index=True)
    
    # Format the percentage string safely
    data_input_chart['Percent_Formatted'] = data_input_chart['Percent'].astype(str).apply(
        lambda x: "No Revenue" if x in ['-inf', 'inf', 'nan'] else x + "%"
    )

    return data_input_chart

def CreateInputMatrixSlider(filtered_df, Profit_level, group_cols=None):

    # Set default grouping if none is provided (ensures backward compatibility)
    if group_cols is None:
        group_cols = ['Account', 'ProductOrigin', 'Commodity', 'Material', 'MaterialName']

    # Prepare data 
    data_input = filtered_df.rename(columns= {'TotalSalesValue':'NSV'})
    
    # Pass the dynamic group_cols argument into SummaryMatrixData
    data_label = SummaryMatrixData(data_input, Profit_level, group_cols)
    
    # Calculate the percentage of profitability level on revenue
    profit_level_percent = round((data_label[Profit_level].sum()/data_label.NSV.sum())*100) if data_label.NSV.sum() != 0 else None

    # Create a threshold for a matrix based on the calculated percentage
    threshold_matrix = [0]

    if profit_level_percent is not None:
        threshold_matrix.append(profit_level_percent)

    threshold_matrix.sort()

    if 0 in threshold_matrix:
        threshold_matrix[threshold_matrix.index(0)] = 0.0000001

    # Create labels for a matrix based on threshold
    labels_matrix = create_palette_matrix(threshold_matrix=threshold_matrix)[0]

    # Assign and extract a label list from a data
    data_label['Label'] = data_label['Percent'].apply(lambda x: AssignLabel(x, threshold_matrix, labels_matrix))    
    label_list = data_label.Label.unique().tolist()

    # Sort a label list 
    ordered_labels_matrix = labels_matrix.copy()
    sorted_label_list = sorted(label_list, key=lambda x: ordered_labels_matrix.index(x))

    return (sorted_label_list, threshold_matrix)





def CreateMatrix(data_input, 
                 profit_level, 
                 list_label, 
                 threshold_matrix, 
                 percent_range=None,
                 base_group_cols=None,
                 material_group_cols=None,
                 account_group_cols=None,
                 main_y_col='Account', 
                 main_x_col='MaterialName',
                 main_x_id_col='Material'):
   
    # 1. Create a dict of palette including labels and colors based on threshold
    labels_matrix, color_matrix = create_palette_matrix(threshold_matrix=threshold_matrix)   
    pallet_matrix = dict(zip(labels_matrix, color_matrix))
    
    # 2. Create data input (passing the dynamic groups through to ProcessMatrixData)
    data_input_chart = ProcessMatrixData(
        data_input, profit_level, list_label, percent_range, threshold_matrix, labels_matrix, color_matrix,
        base_group_cols=base_group_cols, 
        material_group_cols=material_group_cols, 
        account_group_cols=account_group_cols,
        main_y_col=main_y_col, 
        main_x_col=main_x_col
    )            
    
    # 3. Create a dict of palette including labels and colors based on data input
    filter_list = data_input_chart.Label.unique().tolist()
    filtered_pallete = {key: pallet_matrix[key] for key in filter_list if key in pallet_matrix}

    sorted_pallete_keys = sorted(filtered_pallete, key=lambda x: labels_matrix.index(x))
    sorted_pallete = {key: filtered_pallete[key] for key in sorted_pallete_keys}

    # Extract list of labels and colors 
    list_ordered_label = list(sorted_pallete.keys())
    list_ordered_color = list(sorted_pallete.values())

    # 4. Create list of X-Axis (Materials/Categories) 
    mtl_list = data_input_chart.loc[data_input_chart[main_y_col] == "Summary by Materials", :].sort_values(
        by=profit_level,
        ascending=True
    )

    mtl_list_sorted = mtl_list[main_x_col].tolist()
    mtl_list_sorted.append("Summary by Customers")

    # Handle the tick ID column safely (if no ID column exists in the new grouping, just use the name)
    if main_x_id_col in data_input_chart.columns:
        mtlid_list_sorted = mtl_list[main_x_id_col].tolist()
    else:
        mtlid_list_sorted = mtl_list[main_x_col].tolist()
        
    mtlid_list_sorted.append("Summary by Customers")
    mtlid_list_sorted = [str(item) for item in mtlid_list_sorted]

    # 5. Create list of Y-Axis (Accounts/Countries)
    account_list = data_input_chart.loc[data_input_chart[main_x_col] == "Summary by Customers", :].sort_values(
        by=profit_level,
        ascending=True
    )

    account_list_sorted = account_list[main_y_col].tolist()
    account_list_sorted.append("Summary by Materials")

    # 6. Calculate the font size of x and y axes based on size of data input
    fontsize_account = math.ceil(data_input_chart[main_y_col].nunique() * (-0.0869) + 15)
    fontsize_material = math.ceil(data_input_chart[main_x_col].nunique() * (-0.0625) + 15)
    
    # 7. Draw the matrix
    fig = px.scatter(
        data_input_chart,
        x=main_x_col,
        y=main_y_col,
        color='Label',
        category_orders={
            main_x_col: mtl_list_sorted,
            main_y_col: account_list_sorted,
            "Label": list_ordered_label
        },
        color_discrete_sequence=list_ordered_color,
        custom_data=[main_y_col, main_x_col, "NSV", profit_level, "Percent_Formatted"]
    )

    # Dynamically inject the axis names into the hover template
    fig.update_traces(
        hovertemplate=f"<b>{main_y_col} </b>: %{{customdata[0]}} <br>" +
                      f"<b>{main_x_col}</b>: %{{customdata[1]}} <br>" +
                      "<b>Revenue </b>: € %{customdata[2]:,.0f} <br>" +
                      f"<b>{profit_level}</b>: € %{{customdata[3]:,.0f}} <br>" +
                      f"<b>{profit_level} Percentage </b>:  %{{customdata[4]}} <extra></extra>"
    )

    # 8. Dynamic Layout sizing based on the new Y-axis
    num_y_items = len(data_input_chart[main_y_col].unique())
    
    fig.update_layout(
        autosize=False,
        width=1200,
        height=300 if num_y_items <= 5 else 600 if num_y_items <= 26 else 1200,
        xaxis=dict(
            title_text=f"<b>{main_x_col}</b>",
            title_font_color="black",
            tickfont_size=fontsize_material,
            tickvals=mtl_list_sorted,
            ticktext=['Summary by<br>Customers<br>' if tick == 'Summary by Customers' else tick for tick in mtlid_list_sorted] if num_y_items <= 26 else ['Summary by<br>Customers<br><br>' if tick == 'Summary by Customers' else tick for tick in mtlid_list_sorted],
            showgrid=True,
            tickangle=70,
            side="bottom"          
        ),
        yaxis=dict(
            title_text=f"<b>{main_y_col}</b>",
            title_font_color="black",
            tickmode="linear",
            showgrid=True,
            tickfont_size=fontsize_account
        ),
        legend=dict(
            orientation="h",
            title_text=f"<b>{profit_level} Percentage </b>",
            title_font=dict(
                size=15,
                color="black"
            ),
            yanchor="top",
            y=2 if num_y_items <= 5 else 1.15 if num_y_items <= 26 else 1.05,
            xanchor="center",
            x=0.4
        )
    )

    return fig



def create_summary_table_for_matrix(data_input, 
                                    profit_level, 
                                    threshold_matrix, 
                                    list_label, 
                                    percent_range,
                                    base_group_cols=None,
                                    material_group_cols=None,
                                    account_group_cols=None,
                                    main_y_col='Account', 
                                    main_x_col='MaterialName'):
    
    # 1. Create a dict of palette including labels and colors based on threshold
    labels_matrix, color_matrix = create_palette_matrix(threshold_matrix=threshold_matrix)   
    pallet_matrix = dict(zip(labels_matrix, color_matrix))
    
    # 2. Create data input using the dynamic parameters
    data_smr = ProcessMatrixData(
        data_input=data_input, 
        profit_level=profit_level, 
        list_label=list_label, 
        percent_range=percent_range, 
        threshold_matrix=threshold_matrix, 
        labels_matrix=labels_matrix, 
        color_matrix=color_matrix,
        base_group_cols=base_group_cols,
        material_group_cols=material_group_cols,
        account_group_cols=account_group_cols,
        main_y_col=main_y_col,
        main_x_col=main_x_col
    ) 

    # 3. Filter out the summary lines dynamically using the provided axis columns
    data = data_smr[(data_smr[main_x_col] != "Summary by Customers") & (data_smr[main_y_col] != 'Summary by Materials')]  

    # --- 4. Negative Aggregations ---
    neg_value = data[data[profit_level] < 0].agg({
        'NSV': 'sum',
        profit_level: 'sum'
    })

    neg_x = data.groupby(main_x_col, as_index=False).agg({profit_level: 'sum'})
    neg_x = neg_x[neg_x[profit_level] < 0].agg({main_x_col: 'nunique'})

    neg_y = data.groupby(main_y_col, as_index=False).agg({profit_level: 'sum'})
    neg_y = neg_y[neg_y[profit_level] < 0].agg({main_y_col: 'nunique'})

    neg_table = pd.concat([neg_value, neg_x, neg_y])
    neg_table = neg_table.reset_index()
    neg_table.columns = ['Type', 'Negative']

    # --- 5. Positive Aggregations ---
    pos_value = data[data[profit_level] > 0].agg({
        'NSV': 'sum',
        profit_level: 'sum'
    })

    pos_x = data.groupby(main_x_col, as_index=False).agg({profit_level: 'sum'})
    pos_x = pos_x[pos_x[profit_level] > 0].agg({main_x_col: 'nunique'})

    pos_y = data.groupby(main_y_col, as_index=False).agg({profit_level: 'sum'})
    pos_y = pos_y[pos_y[profit_level] > 0].agg({main_y_col: 'nunique'})

    pos_table = pd.concat([pos_value, pos_x, pos_y])
    pos_table = pos_table.reset_index()
    pos_table.columns = ['Type', "Positive"]

    # --- 6. Combine and Format ---
    summary_table = neg_table.merge(pos_table, on='Type').assign(
        Negative_on_Possitive = lambda x: np.where(x.Type != profit_level, x.Negative*100/(x.Positive + x.Negative), np.nan)
    )

    summary_table = summary_table.round(0)
    summary_table.columns = ['Type', f'Negative {profit_level}', f'Positive {profit_level}', f'% Negative {profit_level} on Total']

    # 7. Dynamic Mapping for final text output
    mapping = {
        'NSV': 'Revenue', 
        main_x_col: f'Number of {main_x_col}s', 
        main_y_col: f'Number of {main_y_col}s'
    }
    
    # Fallbacks to ensure exact string matching with your original code if defaults are used
    if main_x_col == 'MaterialName': mapping[main_x_col] = 'Number of Materials'
    if main_y_col == 'Account': mapping[main_y_col] = 'Number of Accounts'

    # Replace values in the 'Type' column
    summary_table['Type'] = summary_table['Type'].replace(mapping)

    return summary_table