with sales_totals as (
    select
        facility_id,
        product_id,
        sum(sales_volume_kg) as total_sales_volume_kg
    from {{ ref('int_sales_pallets') }}
    group by facility_id, product_id
),

transfer_out_totals as (
    select
        origin_facility_id as facility_id,
        product_id,
        sum(transfer_volume_kg) as total_transfer_out_volume_kg
    from {{ ref('int_transfer_costs') }}
    group by origin_facility_id, product_id
),

combined as (
    select
        coalesce(s.facility_id, t.facility_id) as facility_id,
        coalesce(s.product_id, t.product_id) as product_id,
        coalesce(s.total_sales_volume_kg, 0) as total_sales_volume_kg,
        coalesce(t.total_transfer_out_volume_kg, 0) as total_transfer_out_volume_kg
    from sales_totals s
    full outer join transfer_out_totals t
        on s.facility_id = t.facility_id
        and s.product_id = t.product_id
)

select
    c.facility_id,
    c.product_id,
    c.total_sales_volume_kg,
    c.total_sales_volume_kg + c.total_transfer_out_volume_kg as total_outbound_volume_kg,
    coalesce(a.storage_cost_fac_prod, 0) as storage_cost_fac_prod,
    coalesce(a.overhead_cost_fac_prod, 0) as overhead_cost_fac_prod,
    coalesce(a.ioc_fac_prod, 0) as ioc_fac_prod
from combined c
left join {{ ref('int_facility_inventory_alloc') }} a
    on c.facility_id = a.facility_id
    and c.product_id = a.product_id