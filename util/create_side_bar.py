import streamlit as st
import numpy as np
import pandas as pd

def create_side_bar(input_data):

    # list_year = input_data.FY.unique()
    with st.expander("Time"):

    #     st.markdown("""
    #                 <div>
    #                 <p>Fiscal Year:</p>
    #                 </div>   
    #                 """
    #                 , unsafe_allow_html=True)
        
    #     year = st.selectbox(
    #         label='Choose fiscal year you want to review',
    #         options=list_year,
    #         # format_func= lambda x: 'Selected all supply flows' if x == '' else x,
    #         index = 0,
    #         label_visibility='collapsed'            
    #     )
    
        # filtered_df = input_data[input_data.FY == year]
        list_month_full = input_data.Month.unique().tolist()
        sorted_months = sorted(list_month_full, key=lambda x: pd.to_datetime(x, format='%m-%Y'))
        # list_month = filtered_df.Month.unique()
        # print(sorted_months)

        st.markdown("""
                    <div>
                    <p>Month:</p>
                    </div>   
                    """
                    , unsafe_allow_html=True)
        
        month = st.select_slider(
            label= 'Choose which month you want to look at',
            options=sorted_months,
            label_visibility='collapsed',
            value=('01-2024', '12-2025')
        )

        list_month_selected = sorted_months[sorted_months.index(month[0]):(sorted_months.index(month[1])+1)]
        
        filtered_df = input_data[input_data.Month.isin(list_month_selected)]
    
        # list_supply_flow = filtered_df.SupplyChainFlow.unique()
        # list_supply_flow_choose = np.concatenate(([""], list_supply_flow), axis=0)


    with st.expander("Network"):

        # st.markdown("""
        #             <div>
        #             <p>Supply Chain Flow:</p>
        #             </div>   
        #             """
        #             , unsafe_allow_html=True)
        # supply_flow = st.selectbox(
        #     label='Choose supply chain flow',
        #     options=list_supply_flow_choose,
        #     format_func= lambda x: 'Selected all' if x == '' else x,
        #     index = 0,
        #     label_visibility='collapsed'            
        # )

        # if supply_flow != "":

        #     filtered_df = filtered_df[filtered_df.SupplyChainFlow == supply_flow]

        # else:

        #     filtered_df = filtered_df[filtered_df.SupplyChainFlow.isin(list_supply_flow)]  

        list_facility_type = filtered_df.FacilityType.unique()   
        list_facility_type_choose = np.concatenate(([""], list_facility_type), axis=0)

        st.markdown("""
                    <div>
                    <p>Facility Type:</p>
                    </div>   
                    """
                    , unsafe_allow_html=True)
        
        facility_type = st.multiselect(
            label='Choose facility type',
            options=list_facility_type,
            # default=list_facility,
            placeholder="Selected all",
            label_visibility='collapsed',
            key=12        
        )

        if len(facility_type) > 0:

            filtered_df = filtered_df[filtered_df.FacilityType.isin(facility_type)]
        
        else:

            filtered_df = filtered_df[filtered_df.FacilityType.isin(list_facility_type)]

        list_facility = filtered_df.FacilityName.unique()   
        list_facility_choose = np.concatenate(([""], list_facility), axis=0)

        st.markdown("""
                    <div>
                    <p>Facility Name:</p>
                    </div>   
                    """
                    , unsafe_allow_html=True)
        
        facility = st.multiselect(
            label='Choose facility',
            options=list_facility,
            # default=list_facility,
            placeholder="Selected all",
            label_visibility='collapsed',
            key=19            
        )

        if len(facility) > 0:

            filtered_df = filtered_df[filtered_df.FacilityType.isin(facility)]
        
        else:

            filtered_df = filtered_df[filtered_df.FacilityType.isin(list_facility)]        



    with st.expander('Customer'):

        # st.markdown("""
        #             <div>
        #             <p>Segment:</p>
        #             </div>   
        #             """
        #             , unsafe_allow_html=True)
        # segmentation = st.selectbox(
        #     label='Choose Segmentation',
        #     options=list_segment_choose,
        #     format_func= lambda x: "Selected all" if x == '' else x,
        #     index = 0,
        #     label_visibility='collapsed'            
        # )

        # if segmentation == "":

        #     filtered_df = filtered_df[filtered_df.Segment.isin(list_segment)]
        
        # else:

        #     filtered_df = filtered_df[filtered_df.Segment == segmentation]

        list_parent_name = filtered_df.Account.unique()
        list_parent_name_choose = np.concatenate(([""], list_parent_name), axis=0)

        st.markdown("""
                    <div>
                    <p>Account:</p>
                    </div>   
                    """
                    , unsafe_allow_html=True)
        
        parent = st.selectbox(
            label='Choose account',
            options=list_parent_name_choose,
            format_func= lambda x: 'Selected all' if x == '' else x,
            index = 0,
            label_visibility='collapsed',
            key=1
        )

        if parent != "":

            selected_parent = parent
            filtered_df = filtered_df.loc[filtered_df.Account == selected_parent]

        else:

            selected_parent = list_parent_name
            filtered_df = filtered_df.loc[filtered_df.Account.isin(selected_parent)]

        list_country = filtered_df.ShipToCountry.unique()
        list_country_choose = np.concatenate(([""], list_country), axis=0)

        st.markdown("""
                    <div>
                    <p>Country:</p>
                    </div>   
                    """
                    , unsafe_allow_html=True)
        
        country = st.selectbox(
            label='Choose country',
            options=list_country_choose,
            format_func= lambda x: 'Selected all' if x == '' else x,
            index = 0,            
            label_visibility='collapsed',
            key=23            
        )

        if country != "":

            filtered_df = filtered_df.loc[filtered_df.ShipToCountry == country]

        else:

            filtered_df = filtered_df.loc[filtered_df.ShipToCountry.isin(list_country)]   

        list_category = filtered_df.Category.unique()
        list_category_choose = np.concatenate(([""], list_category), axis=0)


    
    with st.expander('Material'):

        st.markdown("""
                    <div>
                    <p>Category:</p>
                    </div>   
                    """
                    , unsafe_allow_html=True)
        
        category = st.selectbox(
            label='Choose material',
            options=list_category_choose,
            format_func= lambda x: 'Selected all' if x == '' else x,
            index = 0,
            # default=list_commodity,
            label_visibility='collapsed',
            key=40            
        )     

        if category != "":

            filtered_df = filtered_df.loc[filtered_df.Category == category]

        else:

            filtered_df = filtered_df.loc[filtered_df.Category.isin(list_category)]

        # list_product_group = filtered_df.ProductGroup.unique() 
        # list_product_group_choose = np.concatenate(([""], list_product_group), axis=0)

        # st.markdown("""
        #             <div style="font-size: 5px; font-family: 'HelveticaNeue-Light', Helvetica, Arial, sans-serif; text-align: left; color: #ffffff;">
        #             <p>Product Group:</p>
        #             </div>   
        #             """
        #             , unsafe_allow_html=True)
        # prod_group = st.selectbox(
        #     label='Choose material',
        #     options=list_product_group_choose,
        #     format_func= lambda x: 'Selected all' if x == '' else x,
        #     index = 0,
        #     label_visibility='collapsed',
        #     key=3            
        # )

        # if prod_group != "":

        #     filtered_df = filtered_df.loc[filtered_df.ProductGroup == prod_group]

        # else:

        #     filtered_df = filtered_df.loc[filtered_df.ProductGroup.isin(list_product_group)]        
        
        list_origin = filtered_df.Country_Facility.unique() 
        list_origin_choose = np.concatenate(([""], list_origin), axis=0)

        st.markdown("""
                    <div>
                    <p>Product Origin:</p>
                    </div>   
                    """
                    , unsafe_allow_html=True)
        
        prod_origin = st.selectbox(
            label='Choose material',
            options=list_origin_choose,
            format_func= lambda x: 'Selected all' if x == '' else x,
            index = 0,
            label_visibility='collapsed',
            key=4           
        )       

        if prod_origin != "":

            filtered_df = filtered_df.loc[filtered_df.Country_Facility == prod_origin]

        else:

            filtered_df = filtered_df.loc[filtered_df.Country_Facility.isin(list_origin)]        
        
        list_material = filtered_df.MaterialName.unique()  
        list_material_choose = np.concatenate(([""], list_material), axis=0)

        st.markdown("""
                    <div>
                    <p>Material:</p>
                    </div>   
                    """
                    , unsafe_allow_html=True)
        material = st.selectbox(
            label='Choose material',
            options=list_material_choose,
            format_func= lambda x: 'Selected all' if x == '' else x,
            index = 0,
            label_visibility='collapsed'            
        )    

        if material != "":

            filtered_df = filtered_df.loc[filtered_df.MaterialName == material]

        else:

            filtered_df = filtered_df.loc[filtered_df.MaterialName.isin(list_material)]

    return filtered_df, list_month_selected