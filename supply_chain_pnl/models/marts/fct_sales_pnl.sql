{{ config(materialized='table') }}

with sales as (
    select * from {{ ref('int_sales_pallets') }}
),

cost_pool as (
    select * from {{ ref('int_facility_cost_pool') }}
),

joined as (
    select
        s.*,
        coalesce(cp.total_sales_volume_kg, 0) as total_sales_volume_kg,
        coalesce(cp.total_storage_pool, 0) as total_storage_pool,
        coalesce(cp.total_ioc_pool, 0) as total_ioc_pool,
        coalesce(cp.total_transport_pool, 0) as total_transport_pool,
        coalesce(cp.total_handling_pool, 0) as total_handling_pool
    from sales s
    left join cost_pool cp
        on s.facility_id = cp.facility_id
        and s.product_id = cp.product_id
),

ratios as (
    select
        *,
        coalesce(safe_divide(sales_volume_kg, total_sales_volume_kg), 0) as alloc_ratio
    from joined
),

allocated as (
    select
        *,
        total_storage_pool * alloc_ratio as allocated_storage_cost,
        total_ioc_pool * alloc_ratio as allocated_ioc,
        total_transport_pool * alloc_ratio as allocated_transport_cost,
        total_handling_pool * alloc_ratio as allocated_handling_cost
    from ratios
),

waterfall as (
    select
        *,
        allocated_transport_cost + allocated_handling_cost + allocated_storage_cost as total_s_and_d,
        total_sales_value - total_cogs as gross_margin,
        0.035 * total_sales_value as sga
    from allocated
)

select
    order_id,
    order_date,
    extract(year from order_date) as fiscal_year,
    format_date('%m-%Y', order_date) as fiscal_month,
    facility_id, facility_name, facility_type, facility_city, facility_country,
    ship_to_id, ship_to_party, account, channel, customer_city, ship_to_country,
    product_id, product_name, category,
    sales_volume,
    sales_volume_kg,
    total_sales_volume_kg,
    sales_volume_kg / 1000 as quantity_mt,
    pallets_shipped,
    total_sales_value,
    total_cogs,
    allocated_storage_cost as total_storage_cost,
    allocated_handling_cost as total_handling_cost,
    allocated_transport_cost as total_transport_cost,
    allocated_ioc as ioc,
    total_s_and_d,
    gross_margin as gm,
    gross_margin - total_s_and_d as cbm,
    gross_margin - total_s_and_d - allocated_ioc as cbmai,
    sga,
    (gross_margin - total_s_and_d - allocated_ioc) - sga as ebitai
from waterfall