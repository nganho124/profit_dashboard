with sales as (
    select * from {{ ref('stg_sales_orders') }}
),
product as (
    select * from {{ ref('stg_product_master') }}
),
facility as (
    select * from {{ ref('stg_facility_master') }}
),
customer as (
    select * from {{ ref('stg_customer_master') }}
),
routes as (
    select * from {{ ref('stg_transport_ratecard') }}
    where route_type = 'Outbound to Customer'
),

joined as (
    select
        s.order_id,
        s.order_date,
        s.facility_id,
        s.ship_to_id,
        s.product_id,
        s.sales_volume,
        s.actual_price,
        f.facility_name,
        f.facility_type,
        f.origin_city as facility_city,
        f.country as facility_country,
        f.handling_cost_per_pallet,
        c.ship_to_party,
        c.account,
        c.channel,
        c.city as customer_city,
        c.ship_to_country,
        p.product_name,
        p.category,
        p.kg_per_pallet,
        p.kg_per_sales_unit,
        p.price,
        p.cogs,
        r.cost_per_pallet as transport_cost_per_pallet,
        s.sales_volume * p.kg_per_sales_unit as sales_volume_kg,
        (s.sales_volume * p.kg_per_sales_unit) / p.kg_per_pallet as raw_pallets
    from sales s
    left join facility f on s.facility_id = f.facility_id
    left join customer c on s.ship_to_id = c.ship_to_id
    left join product p on s.product_id = p.product_id
    left join routes r
        on f.origin_city = r.origin_city
        and c.city = r.destination_city
),

final as (
    select
        *,
        ceil(raw_pallets * 2) / 2 as pallets_shipped
    from joined
)

select
    *,
    pallets_shipped * transport_cost_per_pallet as outbound_transport_cost,
    pallets_shipped * handling_cost_per_pallet as total_handling_cost,
    sales_volume * price as total_sales_value,
    sales_volume * cogs as total_cogs
from final