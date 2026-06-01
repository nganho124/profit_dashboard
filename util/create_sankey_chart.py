import matplotlib.colors as mcolors
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st

def create_color_palette(color_vector, opacity=1):
    number_of_colors = len(color_vector)
    assert number_of_colors > 0, "The color vector should contain at least one color."
    if opacity < 1:
        final_palette = [mcolors.to_rgba(
            color, alpha=opacity) for color in color_vector]
    else:
        final_palette = color_vector
    rgba_strings = [
        f'rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {a})' for r, g, b, a in final_palette]
    return rgba_strings

def get_level(label, levels_mapping):
    for i, levels in enumerate(levels_mapping.values(), start=1):
        if label in levels:
            return i
    return None

def create_id_sequence(sequence):
    unique_numbers = sorted(set(sequence))
    number_to_id = {number: idx + 1 for idx, number in enumerate(unique_numbers)}
    return [number_to_id[number] for number in sequence]

def create_sankey_chart(data, 
                        originCol, 
                        destinationCol,
                        quantityCol, 
                        categoryCol, 
                        colorDict=None,          # Now Optional
                        levelsMapping=None,      # Now Optional
                        mode="snap",
                        return_from_final_node=False,
                        return_to_begin_node=False,
                        unit="ton", 
                        fontName="Helvetica", 
                        fontSize=10):
    
    # --- 1. EXTRACT & SORT NODES ---
    nodes = list(set(data[originCol].unique().tolist() + data[destinationCol].unique().tolist()))

    if levelsMapping is not None:
        order = levelsMapping.label.tolist()
        # Sort based on mapping, push unmapped nodes to the end
        nodes = sorted(nodes, key=lambda x: order.index(x) if x in order else len(order))
    else:
        # Auto-sort alphabetically if no mapping is provided
        nodes = sorted(nodes)
    
    nodes_df = pd.DataFrame({
      'id': np.arange(len(nodes)),
      'label': nodes,
      'color': 'rgba(203,51,59,1)' # Default red node color
    })

    # --- 2. X & Y POSITIONING (Manual vs Auto) ---
    node_x = None
    node_y = None

    if levelsMapping is not None:
        nodes_df = nodes_df.merge(levelsMapping, on='label')
        nodes_df['level'] = create_id_sequence(nodes_df['level'])
        nodes_df['steps'] = 1 / (nodes_df['level'].max() - 1)

        # Reverse logistics logic
        if return_from_final_node and return_to_begin_node:
            nodes_df['x_values'] = np.where(nodes_df['level'] == 1, 0.05, (nodes_df['level'] - 1) * nodes_df['steps'] - 0.05)
        elif (not return_to_begin_node) and return_from_final_node:
            nodes_df['x_values'] = np.where(nodes_df['level'] == 1, 0, (nodes_df['level'] - 1) * nodes_df['steps'] - 0.05)
        elif return_to_begin_node and (not return_from_final_node):
            nodes_df['x_values'] = np.where(nodes_df['level'] == 1, 0.05, (nodes_df['level'] - 1) * nodes_df['steps'])
        else:
            nodes_df['x_values'] = (nodes_df['level'] - 1) * nodes_df['steps']    

        nodes_df['y_values'] = np.where(nodes_df['level'] == nodes_df.level.max(), 0.1, 0.1 * nodes_df['level'])   

        # Freeform anti-overlap logic
        if mode == "freeform":
            last_level = None
            base_y_value = None
            increment = 0.1
            
            for i, row in nodes_df.iterrows():
                current_level = row['level']
                if current_level == last_level:
                    nodes_df.at[i, 'y_values'] = base_y_value + increment
                    increment += 0.05  
                else:
                    last_level = current_level
                    base_y_value = row['y_values']
                    increment = 0.1  

        # Save coordinates to inject into Plotly
        node_x = nodes_df['x_values'].tolist()
        node_y = nodes_df['y_values'].tolist()


    # --- 3. DYNAMIC CATEGORY COLORS ---
    flow = data[categoryCol].sort_values().unique().tolist()
    
    if colorDict is None:
        # Auto-generate a color mapping using standard distinct hex codes
        default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        colorDict = {category: default_colors[i % len(default_colors)] for i, category in enumerate(flow)}

    colorVector = [colorDict[key] for key in flow if key in colorDict]
    palette = create_color_palette(colorVector, opacity=0.6)


    # --- 4. BUILD PLOTLY DICTIONARIES ---
    node_setup = dict(
        pad=15,
        thickness=15,
        line=dict(color='black', width=0.5),
        label=nodes_df['label'].tolist(),
        color=nodes_df['color'].tolist()
    )
    
    # Only inject manual placement coordinates if a mapping was provided.
    # Otherwise, Plotly's engine will arrange them automatically and perfectly.
    if node_x is not None and node_y is not None:
        node_setup['x'] = node_x
        node_setup['y'] = node_y

    origin = pd.merge(data[originCol],
                      nodes_df[['id', 'label']],
                      left_on=originCol, 
                      right_on='label',
                      how='left').drop('label', axis=1)

    destination = pd.merge(data[[destinationCol, quantityCol, categoryCol]],
                           nodes_df[['id', 'label']],
                           left_on=destinationCol, 
                           right_on='label',
                           how='left').drop('label', axis=1)

    links = pd.DataFrame({
        'origin': origin['id'],
        'destination': destination['id'],
        'value': destination[quantityCol].astype(str).values.flatten(),
        'label': destination[categoryCol].astype(str).values.flatten()
    })
    links['label'] = links['label'].astype('category')
    links['color'] = [palette[label] for label in links['label'].cat.codes] 

    link_setup = {
        'source': links['origin'].tolist(),
        'target': links['destination'].tolist(),
        'value': links['value'].tolist(),
        'label': links['label'].tolist(),
        'color': links['color'].tolist()
    }

    # --- 5. RENDER THE CHART ---
    sankey_chart = go.Sankey(
        arrangement=mode,
        domain=dict(x=[0, 1], y=[0, 1]),
        orientation='h',
        valueformat=",.2f",
        valuesuffix=" " + unit,
        node=node_setup,
        link=link_setup
    )

    legend = []
    for key, value in colorDict.items():
        if key in flow:
            legend.append(
                go.Scatter(
                    mode="markers",
                    x=[None],
                    y=[None],
                    marker=dict(size=10, color=value, symbol="square"),
                    name=key,
                )
            )

    traces = [sankey_chart] + legend
    layout = go.Layout(
        showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=fontSize, family=fontName),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        height=500,
        modebar_add='hovercompare'
    )

    fig = go.Figure(data=traces, layout=layout)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    
    return fig, nodes_df

def scope_project():

    html_content = """
    <div style="font-size: 4px; font-family: 'HelveticaNeue-Light', Helvetica, Arial, sans-serif;">
    <p>Time window: <strong>FY23 - From 01/08/2022 to 15/07/2023</strong></p>
    <p>Order Status: <strong>Invoiced</strong></p>
    <p><strong>Only considering ROC of EU</strong></p>      
    <p><strong>Only considering 5 Supply Chain Flows:</strong>
    <ul>
        <li><span style="display:inline-block; width:10px; height:10px; background-color:#C63D2F; margin-right:5px;"></span>EU to EU Direct</li>
        <li><span style="display:inline-block; width:10px; height:10px; background-color:#FF9B50; margin-right:5px;"></span>EU to EU Switch</li>
        <li><span style="display:inline-block; width:10px; height:10px; background-color:#053B50; margin-right:5px;"></span>NZ Indirect</li>
        <li><span style="display:inline-block; width:10px; height:10px; background-color:#62B6B7; margin-right:5px;"></span>NZ Direct EU</li>
        <li><span style="display:inline-block; width:10px; height:10px; background-color:#CBEDD5; margin-right:5px;"></span>NZ Direct Export</li>
    </ul></p>
    <p><strong>Out of scope Supply Chain Flow:</strong>
    <ul>
        <li><span style="display:inline-block; width:10px; height:10px; background-color:#FFF2CC; margin-right:5px;"></span>EU to Export</li>
    </ul></p>
    <p><strong>Excluded:</strong>
    <ul>
        <li>Sales Record of Material from Gregory (SAPUTO)</li>
        <li>Sales Record classifed as Downgraded materials</li>
        <li>Sales Record for SAMPLE Heerenveen</li>
    </ul></p>
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

    st.markdown(html_content, unsafe_allow_html=True)    