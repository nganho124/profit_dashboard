
import pandas as pd
import numpy as np 
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from scipy.stats import skew
import math

threshold_3d = [0.0000001,10,20]
labels_3d = ["Above "+ str(threshold_3d[2])+ "%",
          "From " + str(threshold_3d[1])+ "%" + " to " + str(threshold_3d[2]) + "%",
          "From " + "0"+ "%" + " to " + str(threshold_3d[1]) + "%",
          "Lower than 0%",
          "No Revenue"]
color_3d = ["#005959", "#5c9696", "#bed7d8", "#D0474E","#7F7F7F"]
pallet_3d_cbm = dict(zip(labels_3d,color_3d))

def AssignLabel(value,threshold,label):
    
    if value == -np.inf:
        output = label[4]
    elif value < threshold[0]:
        output = label[3]
    elif value >= threshold[0] and value < threshold[1]:
        output = label[2]
    elif value >= threshold[1] and value <= threshold[2]:
        output = label[1]
    else:
        output = label[0]

    return(output)

segment_3d = ["Key Account","Managed","Semi Managed","Smart Serve","Internal"]
color_3d = ["#D0474E", "#FFCC32", "#004570", "#5c9696", "#7F7F7F", "#F37032"]

pallet_3d = dict(zip(segment_3d,color_3d))

def DecideScale(data,colname):
    # Check object col type
    if data[colname].dtype == "object":
        return "category"

    # Remove non-positive values for log scale consideration
    positive_data = [x for x in data[colname] if x > 0]

    # Check if there's enough data to consider log scale
    if len(positive_data) < 2:
        return "linear"

    # Calculate range and skewness
    data_range = max(positive_data) / min(positive_data)
    data_skewness = skew(positive_data)

    # Decision criteria
    if data_range > 1000 and data_skewness > 1 and data[colname].min() >= 0:
        return "log"
    else:
        return "linear"

def format_number(num):
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f} M"
    elif num >= 1_000:
        return f"{num:,.0f}"
    elif num >= 1_00:
        return f"{num:,.1f}"    
    elif num == -np.inf:
        return "No Value"
    else:
        return f"{num:,.2f}"


def ProcessData3D (data):
    data_input = pd.DataFrame(data)
    
    # Create data summary by segment and account
    data_processed = data_input.rename(
        columns={'TotalSalesValue':'Revenue'}
    ).assign(
        Cost = lambda x: x.TotalCOGS + x.TotalStorageCostPerYear + x.TotalDemurrageCost + x.TotalHandlingCost + x.TotalTransportCost
    ).groupby(
        ['Segment','Account'],
        as_index= False
    ).agg(
        {'Revenue':'sum',
        'Cost':'sum',
        'QuantityInMT':'sum'}
    ).assign(
        CBM = lambda x: round(x.Revenue - x.Cost,ndigits=2),
        Revenue = lambda x: round(x.Revenue, ndigits= 2),
        CBM_Percentage = lambda x: round(x.CBM*100/x.Revenue,ndigits=2)
    )

    # Format numbers of numeric cols
    data_processed['Formatted_CBM'] = data_processed['CBM'].apply(format_number)
    data_processed['Formatted_Revenue'] = data_processed['Revenue'].apply(format_number)
    data_processed['Formatted_Volume'] = data_processed['QuantityInMT'].apply(format_number)
    data_processed['Formatted_Percentage'] = data_processed['CBM_Percentage'].apply(format_number)
    data_processed['Formatted_Percentage'] = data_processed['Formatted_Percentage'].apply(lambda x: x + " %" if x != "No Value" else x)

    # Remove error data 
    if "No Value" in data_processed['Formatted_Percentage'].tolist() and data_processed.Revenue.sum() != 0:
        data_processed.query(
            'Revenue > 0',
            inplace=True
        )

    return(data_processed)

# def update_axis_tickvals(fig, act_axis_order, data_processed):
#     # List of allowed axis names
#     allowed_axes = ['Formatted_CBM', 'Formatted_Revenue', 'Formatted_Volume', 'Formatted_Percentage']
    
#     # Check if any of the allowed axes are in act_axis_order
#     if any(axis in act_axis_order for axis in allowed_axes):
#         axis_names = ['scene_xaxis_tickvals', 'scene_yaxis_tickvals', 'scene_zaxis_tickvals']
#         # Update axis tickvals with text values
#         for index, axis in enumerate(act_axis_order):
#             if axis in allowed_axes:
#                 fig.update_layout({axis_names[index]: data_processed[axis].tolist()})

def update_axis_ticks(fig, act_axis_order, data_processed, axis_values):
    axis_dict = {'0': 'scene.xaxis', '1': 'scene.yaxis', '2': 'scene.zaxis'}
    
    # Update axis tickvals with numeric values when axis's scale is log scale
    for axis_name, axis_value in axis_values.items():
        if axis_name in act_axis_order:
            scale_type = DecideScale(data_processed, axis_name)
            if scale_type == "log":
                axis_index = act_axis_order.index(axis_name)
                fig.update_layout({
                    axis_dict[str(axis_index)] + '.tickvals': axis_value
                })

def Create3DChart (data,axis_order):

    # Create input data
    data_processed = ProcessData3D(data)
    
    # Replace the axis name so that it matches with the col name of data input
    act_axis_order = [item.replace("CBM Percentage", "CBM_Percentage") for item in axis_order]
    act_axis_order = [item.replace("Sales In MT", "QuantityInMT") for item in act_axis_order]

    # Replace the axis name with the col name having str type, When the chart displays 1 value or has only NA values.
    if len(data_processed) == 1:
        act_axis_order = [item.replace("CBM", "Formatted_CBM") if item == "CBM" else item for item in act_axis_order]
        act_axis_order = [item.replace("Revenue", "Formatted_Revenue") if item == "Revenue" else item for item in act_axis_order]
        act_axis_order = [item.replace("QuantityInMT", "Formatted_Volume") if item == "QuantityInMT" else item for item in act_axis_order]
        act_axis_order = [item.replace("CBM_Percentage", "Formatted_Percentage") if item == "CBM_Percentage" else item for item in act_axis_order]
    elif data_processed.Formatted_Percentage.unique().tolist()[0] == "No Value":
        act_axis_order = [item.replace("Revenue", "Formatted_Revenue") if item == "Revenue" else item for item in act_axis_order]
        act_axis_order = [item.replace("CBM_Percentage", "Formatted_Percentage") if item == "CBM_Percentage" else item for item in act_axis_order]    

    # Create values displaying on axes based on log scale
    min_rev_tickvals = pow(10,len(str(math.ceil(data_processed.Revenue.min())))-1)
    max_rev_tickvals = pow(10,len(str(math.ceil(data_processed.Revenue.max())))-1)
    revenue_tickvals = []

    for i in range(int(math.log10(max_rev_tickvals) - math.log10(min_rev_tickvals))):
        revenue_tickvals.append(min_rev_tickvals*pow(10,(i+1)))


    min_cbm_tickvals = pow(10,len(str(math.ceil(data_processed.CBM.min())))-1)
    max_cbm_tickvals = pow(10,len(str(math.ceil(data_processed.CBM.max())))-1)
    cbm_tickvals = []

    for i in range(int(math.log10(max_cbm_tickvals) - math.log10(min_cbm_tickvals))):
        cbm_tickvals.append(min_cbm_tickvals*pow(10,(i+1)))

    min_volume_tickvals = pow(10,len(str(math.ceil(data_processed.QuantityInMT.min())))-1)
    max_volume_tickvals = pow(10,len(str(math.ceil(data_processed.QuantityInMT.max())))-1)
    volume_tickvals = []

    for i in range(int(math.log10(max_volume_tickvals) - math.log10(min_volume_tickvals))):
        volume_tickvals.append(min_volume_tickvals*pow(10,(i+1)))

    # Create a dict of colors and segments
    filtered_segment = data_processed.Segment.unique()
    filtered_pallete_3d =  {key: pallet_3d[key] for key in filtered_segment if key in pallet_3d}

    sorted_pallete_3d_keys = sorted(filtered_pallete_3d, key = lambda x:segment_3d.index(x))
    sorted_pallete_3d = {key: filtered_pallete_3d[key] for key in sorted_pallete_3d_keys}

    # Create a dict of colors and labels 
    data_processed["Label"] = data_processed["CBM_Percentage"].apply(lambda x: AssignLabel(x,threshold_3d,labels_3d))

    filtered_label = data_processed.Label.unique()
    filtered_pallete_3d_cbm =  {key: pallet_3d_cbm[key] for key in filtered_label if key in pallet_3d_cbm}

    sorted_pallete_3d_cbm_keys = sorted(filtered_pallete_3d_cbm, key = lambda x:labels_3d.index(x))
    sorted_pallete_3d_cbm = {key: filtered_pallete_3d_cbm[key] for key in sorted_pallete_3d_cbm_keys}

    # Choose the displayed legened based on axis order 
    if "Segment" in act_axis_order:
        legend = "Label"
        legend_title = "CBM Percentage"
    else:
        legend = "Segment"
        legend_title = "Segment"

    sorted_pallete = dict(
        Segment = sorted_pallete_3d,
        Label = sorted_pallete_3d_cbm
    )

    # Draw a chart
    fig = px.scatter_3d(
        data_processed,
        x= act_axis_order[0],
        y= act_axis_order[1],
        z= act_axis_order[2],
        color = legend,
        color_discrete_sequence= list(sorted_pallete[legend].values()),
        category_orders = {"Label": list(sorted_pallete_3d_cbm.keys()),
                           "Segment": list(sorted_pallete_3d.keys())},
        custom_data= ['Segment','Account','Formatted_Revenue','Formatted_CBM','Formatted_Percentage','QuantityInMT']
    )

    # Create tooltip
    fig.update_traces(
                    hovertemplate = "<b>Segment </b>:%{customdata[0]} <br><b>Account Name</b>: %{customdata[1]} <br><b>Revenue </b>: € %{customdata[2]} <br><b>Sales In MT </b>:  %{customdata[5]:,.2f} <br><b>CBM </b>: € %{customdata[3]} <br><b>CBM Percentage </b>:  %{customdata[4]} <extra></extra>",
                    marker = dict(size = 5)
    )

    # Update the scale of three axes and legend
    fig.update_layout(
        autosize = False,
        width = 750,
        height = 750,
        template= "plotly",
        scene = dict(
            xaxis = dict(
                title = axis_order[0],
                title_font_color = "black",
                type = DecideScale(data_processed,act_axis_order[0])
            ),
            yaxis = dict(
                title = axis_order[1],
                title_font_color = "black",
                type = DecideScale(data_processed,act_axis_order[1])
            ),
            zaxis = dict(
                title= axis_order[2],
                title_font_color = "black",
                type = DecideScale(data_processed,act_axis_order[2])
            )
        ),
        legend_orientation = 'h',
        legend_title  = '<b>'+legend_title+'</b>',
        legend = dict(
            title_font = dict(
                size =15,
                color = "black"
            ),
            yanchor = "top",
            y = 1,
            xanchor = "center",
            x = 0.5
        )
    )

    axis_values = {
        'Revenue': revenue_tickvals,
        'CBM': cbm_tickvals,
        'QuantityInMT': volume_tickvals
    }
    # Function to update axis label when using log scale
    update_axis_ticks(fig, act_axis_order, data_processed, axis_values)

    # Function to update axis label when there is only 1 data point        
    # update_axis_tickvals(fig, act_axis_order, data_processed)         

    return(fig)








# def Create3DCBMChart (data, segment_order = segment_3d):
#     segment_order.reverse()
#     data_processed_3d_cbm = ProcessData3D(data)

#     data_processed_3d_cbm["Label"] = data_processed_3d_cbm["CBM_Percentage"].apply(lambda x: AssignLabel(x,threshold_3d,labels_3d))

#     filtered_label = data_processed_3d_cbm.Label.unique()
#     filtered_pallete_3d_cbm =  {key: pallet_3d_cbm[key] for key in filtered_label if key in pallet_3d_cbm}

#     sorted_pallete_3d_cbm_keys = sorted(filtered_pallete_3d_cbm, key = lambda x:labels_3d.index(x))
#     sorted_pallete_3d_cbm = {key: filtered_pallete_3d_cbm[key] for key in sorted_pallete_3d_cbm_keys}

#     filtered_segment_cbm = data_processed_3d_cbm.Segment.unique()
#     sorted_segment_cbm = sorted(filtered_segment_cbm, key = lambda x:segment_order.index(x))



#     fig = px.scatter_3d(
#         data_processed_3d_cbm,
#         x='Segment',
#         y='Revenue',
#         z='CBM',
#         color = 'Label',
#         color_discrete_sequence= list(sorted_pallete_3d_cbm.values()),
#         category_orders = {"Label": list(sorted_pallete_3d_cbm.keys()),
#                            "Segment": sorted_segment_cbm},
#         custom_data= ['Segment','Account','Formatted_Revenue','Formatted_CBM','CBM_Percentage']
#     )

#     fig.update_traces(
#                     hovertemplate = "<b>Segment </b>:%{customdata[0]} <br><b>Account Name</b>: %{customdata[1]} <br><b>Revenue </b>: € %{customdata[2]} <br><b>CBM </b>: € %{customdata[3]} <br><b>CBM Percentage </b>:  %{customdata[4]:,.2f} %<extra></extra>",
#                     marker = dict(size = 6)
#     )


#     fig.update_layout(
#         autosize = False,
#         width = 750,
#         height = 750,
#         template= "plotly",
#         scene = dict(
#             xaxis_title = '',
#             xaxis_title_font_color = "black",
#             yaxis = dict(
#                 title = 'Revenue',
#                 type = 'log'
#             ),
#             zaxis_title= 'CBM',
#             zaxis_title_font_color = "black",
#             yaxis_title_font_color = "black",
#         ),
#         legend_orientation = 'h',
#         legend_title  = '<b>CBM Percentage</b>',
#         legend = dict(
#             title_font = dict(
#                 size =15,
#                 color = "black"
#             ),
#             yanchor = "bottom",
#             y = -0.1,
#             xanchor = "center",
#             x = 0.5
#         )
#     )
#     return(fig)