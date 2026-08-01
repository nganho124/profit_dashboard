with inventory as (
    select * from {{ ref('stg_inventory') }}
),
facility as (
    select * from {{ ref('stg_facility_master') }}
),
product as (
    select * from {{ ref('stg_product_master') }}
),

rounded_inventory as (
    select
        facility_id,
        product_id,
        inventory_date,
        -- enforce whole-pallet occupancy: a partial pallet can't be shared across products
        ceil(volume_in_pallet) as volume_in_pallet_rounded
    from inventory
),

avg_inv as (
    select
        facility_id,
        product_id,
        avg(volume_in_pallet_rounded) as avg_inventory_pallets
    from rounded_inventory
    group by facility_id, product_id
),

with_ratio as (
    select
        *,
        sum(avg_inventory_pallets) over (partition by facility_id) as facility_total_avg_inventory,
        coalesce(safe_divide(
            avg_inventory_pallets,
            sum(avg_inventory_pallets) over (partition by facility_id)
        ), 0) as inv_alloc_ratio
    from avg_inv
)

select
    w.facility_id,
    w.product_id,
    w.avg_inventory_pallets,
    w.inv_alloc_ratio,
    f.annual_storage_cost * 2 * w.inv_alloc_ratio as storage_cost_fac_prod,
    f.total_overhead_cost * 2 * w.inv_alloc_ratio as overhead_cost_fac_prod,
    0.10 * w.avg_inventory_pallets * (p.cogs * (p.kg_per_pallet / p.kg_per_sales_unit)) as ioc_fac_prod
from with_ratio w
left join facility f on w.facility_id = f.facility_id
left join product p on w.product_id = p.product_id