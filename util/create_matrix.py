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



def ProcessMatrixData(data_input, profit_level,list_label,percent_range,threshold_matrix,labels_matrix,color_matrix):

    data_grp_prt_mtl = data_input.rename(columns= {'TotalSalesValue':'NSV'})

    # Create summary data by account and material
    data_grp_prt_mtl = SummaryMatrixData(data_grp_prt_mtl,profit_level,['Account','ProductOrigin','Commodity','Material','MaterialName'])
    data_grp_prt_mtl['Label'] = data_grp_prt_mtl['Percent'].apply(lambda x: AssignLabel(x,threshold_matrix,labels_matrix))
    data_grp_prt_mtl['Color'] = data_grp_prt_mtl['Percent'].apply(lambda x: AssignColor(x,threshold_matrix,color_matrix))

    if percent_range is not None:
        if len(percent_range) > 1:
            data_grp_prt_mtl = data_grp_prt_mtl[data_grp_prt_mtl['Label'].isin(list_label[list_label.index(percent_range[0]):(list_label.index(percent_range[1])+1)])]    
        elif len(percent_range) == 1:
            data_grp_prt_mtl = data_grp_prt_mtl[data_grp_prt_mtl['Label'].isin(percent_range)]

    data_input_processed = data_grp_prt_mtl.copy(deep=True)

    # Create summary data by material
    summary_material = SummaryMatrixData(data_grp_prt_mtl,profit_level,['Material','MaterialName','Commodity','ProductOrigin']).sort_values(
        by = profit_level,
        ascending = True
    ).assign(Account = "Summary by Materials")
    summary_material['Label'] = summary_material['Percent'].apply(lambda x: AssignLabel(x,threshold_matrix,labels_matrix))
    summary_material['Color'] = summary_material['Percent'].apply(lambda x: AssignColor(x,threshold_matrix,color_matrix))

    # Create summary data by account
    summary_customer = SummaryMatrixData(data_grp_prt_mtl,profit_level,['Account']).assign(
        Material = "Summary by Customer",
        MaterialName = "Summary by Customers",
        Commodity = "Summary",
        ProductOrigin = "Summary"
    ).sort_values(
        by = profit_level,
        ascending = False
    )

    summary_customer.Account = pd.Categorical(summary_customer.Account, categories= summary_customer.Account)
    summary_customer['Label'] = summary_customer['Percent'].apply(lambda x: AssignLabel(x,threshold_matrix,labels_matrix))
    summary_customer['Color'] = summary_customer['Percent'].apply(lambda x: AssignColor(x,threshold_matrix,color_matrix))

    # Combine data
    data_input_chart = data_input_processed.assign(
        Account = lambda x: pd.Categorical(x.Account, categories=summary_customer.Account),
        MaterialName = lambda x: pd.Categorical(x.MaterialName, categories=summary_material.MaterialName)
    )

    data_input_chart = pd.concat([summary_customer,data_input_chart],ignore_index= True)
    data_input_chart = pd.concat([summary_material,data_input_chart], ignore_index= True)
    data_input_chart['Percent_Formatted'] = data_input_chart.Percent.astype(str).apply(lambda x: "No Revenue" if x == '-inf' else x + "%")

    

    return(data_input_chart)

def CreateInputMatrixSlider(filtered_df,Profit_level):

    # Prepare data 
    data_input = filtered_df.rename(columns= {'TotalSalesValue':'NSV'})
    data_label = SummaryMatrixData(data_input,Profit_level,['Account','ProductOrigin','Commodity','Material','MaterialName'])
    
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
    labels_matrix = create_palette_matrix(threshold_matrix = threshold_matrix)[0]

    # Assign and extract a label list from a data
    data_label['Label'] = data_label['Percent'].apply(lambda x: AssignLabel(x,threshold_matrix,labels_matrix))    
    label_list = data_label.Label.unique().tolist()

    # Sort a label list 
    ordered_labels_matrix =  labels_matrix.copy()
    sorted_label_list = sorted(label_list, key = lambda x:ordered_labels_matrix.index(x))

    return(sorted_label_list,threshold_matrix)





def CreateMatrix(data_input,profit_level,list_label,threshold_matrix,percent_range = None):
   
    # Create a dict of palette including labels and colors based on threshold
    labels_matrix,color_matrix = create_palette_matrix(threshold_matrix = threshold_matrix)   
    pallet_matrix = dict(zip(labels_matrix,color_matrix))
    
    # Create data input
    data_input_chart = ProcessMatrixData(data_input,profit_level,list_label,percent_range,threshold_matrix,labels_matrix,color_matrix)             
    
    # Create a dict of palette including labels and colors based on data input
    filter_list = data_input_chart.Label.unique().tolist()
    filtered_pallete =  {key: pallet_matrix[key] for key in filter_list if key in pallet_matrix}

    sorted_pallete_keys = sorted(filtered_pallete, key = lambda x:labels_matrix.index(x))
    sorted_pallete = {key: filtered_pallete[key] for key in sorted_pallete_keys}

    # Extract list of labels and colors 
    list_ordered_label = list(sorted_pallete.keys())
    list_ordered_color = list(sorted_pallete.values())


    # Create list of material and material ID 
    mtl_list = data_input_chart.loc[data_input_chart.Account == "Summary by Materials",:].sort_values(
        by = profit_level,
        ascending= True
    )

    mtl_list_sorted = mtl_list.MaterialName.tolist()
    mtl_list_sorted.append("Summary by Customers")

    mtlid_list_sorted = mtl_list.Material.tolist()
    mtlid_list_sorted.append("Summary by Customers")
    mtlid_list_sorted = [str(item) for item in mtlid_list_sorted]

    # Create list of account
    account_list = data_input_chart.loc[data_input_chart.MaterialName == "Summary by Customers",:].sort_values(
        by = profit_level,
        ascending= True
    )

    account_list_sorted = account_list.Account.tolist()
    account_list_sorted.append("Summary by Materials")

    # Calculate the font size of x and y axes based on size of data input
    fontsize_account = math.ceil(data_input_chart.Account.nunique()*(-0.0869)+15)
    fontsize_material = math.ceil(data_input_chart.MaterialName.nunique()*(-0.0625)+15)
    
    # Draw  a matrix
    fig = px.scatter(
        data_input_chart,
        x= "MaterialName",
        y = "Account",
        # size = "NSV" ,
        color = 'Label',
        category_orders = {
            "MaterialName": mtl_list_sorted,
            "Account": account_list_sorted,
            "Label": list_ordered_label
        },
        color_discrete_sequence = list_ordered_color,
        custom_data = ["Account", "MaterialName", "NSV", profit_level, "Percent_Formatted"]
    )

    fig.update_traces(
        hovertemplate = "<b>Account Name </b>: %{customdata[0]} <br>"+
        "<b>Material</b>: %{customdata[1]} <br>"+
        "<b>Revenue </b>: € %{customdata[2]:,.0f} <br>"+
        "<b>"+ profit_level + "</b>: € %{customdata[3]:,.0f} <br>"+
        "<b>" + profit_level +" Percentage </b>:  %{customdata[4]} <extra></extra>"
    )

    fig.update_layout(
        autosize = False,
        width = 1200,
        height = 300 if len(data_input_chart.Account.unique()) <= 5 else 600 if len(data_input_chart.Account.unique()) <= 26 else 1200,
        xaxis = dict(
            title_text = "<b>Material</b>",
            title_font_color = "black",
            # tickmode = "linear",
            tickfont_size = fontsize_material,
            tickvals = mtl_list_sorted,
            ticktext =  ['Summary by<br>Customers<br>' if tick == 'Summary by Customers' else tick for tick in mtlid_list_sorted] if len(data_input_chart.Account.unique()) <= 26 else ['Summary by<br>Customers<br><br>' if tick == 'Summary by Customers' else tick for tick in mtlid_list_sorted],
            showgrid= True,
            tickangle = 70,
            side = "bottom"          
        ),
        yaxis = dict(
            title_text = "<b>Account Name</b>",
            title_font_color = "black",
            tickmode = "linear",
            showgrid= True,
            tickfont_size = fontsize_account
        ),
        legend = dict(
            orientation = "h",
            title_text = "<b>" + profit_level +" Percentage </b>",
            title_font = dict(
                size = 15,
                color = "black"
            ),
            yanchor = "top",
            y = 2 if len(data_input_chart.Account.unique()) <= 5 else 1.15 if len(data_input_chart.Account.unique()) <= 26 else 1.05,
            xanchor = "center",
            x = 0.4
        )
    )

    return(fig)    




def create_summary_table_for_matrix(datainput,
                                    profit_level,
                                    threshold_matrix,
                                    list_label,
                                    percent_range):
    
    # Create a dict of palette including labels and colors based on threshold
    labels_matrix,color_matrix = create_palette_matrix(threshold_matrix = threshold_matrix)   
    pallet_matrix = dict(zip(labels_matrix,color_matrix))
    
    # Create data input
    data_smr = ProcessMatrixData(datainput,profit_level,list_label,percent_range,threshold_matrix,labels_matrix,color_matrix) 

    # data = data_smr[(data_smr['Material'] == "Summary by Customers" | (data_smr['Account'] == 'Summary by Materials'))]
    data = data_smr[(data_smr['MaterialName'] != "Summary by Customers") & (data_smr['Account'] != 'Summary by Materials')]  

    neg_value = data[data[profit_level] < 0].agg({
        'NSV': 'sum',
        profit_level: 'sum'}
    )

    neg_material = data.groupby('MaterialName', as_index=False).agg({
        profit_level: 'sum'})

    neg_material = neg_material[neg_material[profit_level] < 0].agg(
        {'MaterialName': 'nunique'}
    )

    neg_customer = data.groupby('Account', as_index=False).agg({
        profit_level: 'sum'})

    neg_customer = neg_customer[neg_customer[profit_level] < 0].agg(
        {'Account': 'nunique'}
    )

    neg_table = pd.concat([neg_value, neg_material, neg_customer])
    neg_table = neg_table.reset_index()
    neg_table.columns = ['Type', 'Negative']

    pos_value = data[data[profit_level] > 0].agg({
        'NSV': 'sum',
        profit_level: 'sum'}
    )

    pos_material = data.groupby('MaterialName', as_index=False).agg({
        profit_level: 'sum'})

    pos_material = pos_material[pos_material[profit_level] > 0].agg(
        {'MaterialName': 'nunique'}
    )

    pos_customer = data.groupby('Account', as_index=False).agg({
        profit_level: 'sum'})

    pos_customer = pos_customer[pos_customer[profit_level] > 0].agg(
        {'Account': 'nunique'}
    )

    pos_table = pd.concat([pos_value, pos_material, pos_customer])
    pos_table = pos_table.reset_index()
    pos_table.columns = ['Type', "Positive"]

    summary_table = neg_table.merge(pos_table, on='Type').assign(
        Negative_on_Possitive = lambda x: np.where(x.Type != profit_level, x.Negative*100/(x.Positive + x.Negative), np.nan)
    )

    summary_table = summary_table.round(0)
    summary_table.columns = ['Type', 'Negative ' + profit_level, 'Positive ' + profit_level, '% Negative ' +  profit_level + ' on Total']

    mapping = {'NSV': 'Revenue', 'MaterialName': 'Number of Materials', 'Account': 'Number of Accounts'}

    # Replace values in the 'Type' column
    summary_table['Type'] = summary_table['Type'].replace(mapping)
    # summary_table['% Negative ' +  profit_level + ' on Total'] = summary_table['% Negative ' +  profit_level + ' on Total'].replace({0: })

    return summary_table