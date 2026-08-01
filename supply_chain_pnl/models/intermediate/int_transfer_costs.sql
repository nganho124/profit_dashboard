with transfers as (
    select * from {{ ref('stg_internal_transfer') }}
),
product as (
    select * from {{ ref('stg_product_master') }}
),
routes as (
    select * from {{ ref('stg_transport_ratecard') }}
    where route_type = 'Internal STO'
),
facility as (
    select * from {{ ref('stg_facility_master') }}
)

select
    t.transfer_id,
    t.transfer_date,
    t.origin_facility_id,
    t.destination_facility_id,
    t.product_id,
    t.transfer_pallets,
    t.transfer_pallets * p.kg_per_pallet as transfer_volume_kg,
    r.cost_per_pallet as transfer_cost_per_pallet,
    t.transfer_pallets * r.cost_per_pallet as transfer_transport_cost,
    -- handling incurred at the origin facility when the transfer is picked/loaded
    f.handling_cost_per_pallet as origin_handling_cost_per_pallet,
    t.transfer_pallets * f.handling_cost_per_pallet as transfer_handling_cost
from transfers t
left join product p on t.product_id = p.product_id
left join routes r
    on t.origin_facility_id = r.origin_id
    and t.destination_facility_id = r.destination_id
left join facility f on t.origin_facility_id = f.facility_id