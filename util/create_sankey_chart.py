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

def create_sankey_chart(data, 
                        originCol, 
                        destinationCol,
                        quantityCol, 
                        categoryCol, 
                        colorDict,
                        levelsMapping,
                        unit="ton", 
                        fontName="Helvetica", 
                        fontSize=10):
    
    order = levelsMapping.label.tolist()

    nodes = list(set(data[originCol].unique().tolist() + data[destinationCol].unique().tolist()))

    nodes = sorted(nodes, key=lambda x: order.index(x))
    
    nodes_df = pd.DataFrame({
      'id': np.arange(len(nodes)),
      'label': nodes,
      'color': 'rgba(203,51,59,1)'
    })

    nodes_df = nodes_df.merge(levelsMapping, on='label')

    # nodes_df['level'] = nodes_df['label'].apply(
    #     lambda x: get_level(x, levelsMapping))
    nodes_df['steps'] = 1 / (nodes_df['level'].max() - 1)
    nodes_df['x_values'] = (nodes_df['level'] - 1) * nodes_df['steps']
    nodes_df['y_values'] = np.where(nodes_df['level'] == 5, 0.05, 0.05 * nodes_df['level'])

    colorVector = [colorDict[key] for key in data[categoryCol].sort_values().unique() if key in colorDict]

    node = dict(
        label=nodes_df['label'].tolist(),
        x=nodes_df['x_values'].tolist(),
        y=nodes_df['y_values'].tolist(),
        color=nodes_df['color'].tolist(),
        pad=15,
        thickness=15,
        line=dict(
            color='black',
            width=0.5
        )
    )

    origin = pd.merge(data[originCol],
                    nodes_df[['id', 'label']],
                    left_on=originCol, right_on='label',
                    how='left').drop('label',
                                    axis=1)

    destination = pd.merge(data[[destinationCol, quantityCol, categoryCol]],
                        nodes_df[['id', 'label']],
                        left_on=destinationCol, right_on='label',
                        how='left').drop('label',
                                            axis=1)

    palette = create_color_palette(colorVector, opacity = 0.6)

    links = pd.DataFrame({
        'origin': origin['id'],
        'destination': destination['id'],
        'value': destination[quantityCol].astype(str).values.flatten(),
        'label': destination[categoryCol].astype(str).values.flatten()
    })
    links['label'] = links['label'].astype('category')
    links['color'] = [palette[label] for label in links['label'].cat.codes] 

    link = {
        'source': links['origin'].tolist(),
        'target': links['destination'].tolist(),
        'value': links['value'].tolist(),
        'label': links['label'].tolist(),
        'color': links['color'].tolist()
    }

    sankey_chart = go.Sankey(
        arrangement='snap',
        domain=dict(x=[0, 1], y=[0, 1]),
        orientation='h',
        valueformat=", .2f",
        valuesuffix=" " + unit,
        node=dict(
            pad=15,
            thickness=15,
            line=dict(color='black', width=0.5),
            label=node['label'],
            x=node['x'],
            y=node['y'],
            color=node['color']
        ),
        link=dict(
            source=link['source'],
            target=link['target'],
            value=link['value'],
            label=link['label'],
            color=link['color']
        )
    )

    legend = []
    flow = data[categoryCol].sort_values().unique().tolist()

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
        height=500
    )

    fig = go.Figure(data=traces, layout=layout)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    # fig.show()
    
    return fig

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