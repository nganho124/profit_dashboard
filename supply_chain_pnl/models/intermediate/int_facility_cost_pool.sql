with direct_costs as (
    select * from {{ ref('int_facility_inventory_alloc') }}
),

inbound_costs as (
    select * from {{ ref('int_inbound_inherited_costs') }}
),

outbound_sales_costs as (
    select
        facility_id,
        product_id,
        sum(outbound_transport_cost) as total_outbound_transport_cost,
        sum(total_handling_cost) as total_outbound_handling_cost,
        sum(sales_volume_kg) as total_sales_volume_kg
    from {{ ref('int_sales_pallets') }}
    group by facility_id, product_id
)

select
    coalesce(d.facility_id, i.facility_id, o.facility_id) as facility_id,
    coalesce(d.product_id, i.product_id, o.product_id) as product_id,

    coalesce(o.total_sales_volume_kg, 0) as total_sales_volume_kg,

    -- Storage + Overhead combined (matches original notebook's TotalStorageCost grouping)
    coalesce(d.storage_cost_fac_prod, 0) + coalesce(d.overhead_cost_fac_prod, 0)
        + coalesce(i.inbound_storage_cost, 0) + coalesce(i.inbound_overhead_cost, 0) as total_storage_pool,

    coalesce(d.ioc_fac_prod, 0) + coalesce(i.inbound_ioc, 0) as total_ioc_pool,

    coalesce(o.total_outbound_transport_cost, 0) + coalesce(i.inbound_transport_cost, 0) as total_transport_pool,

    coalesce(o.total_outbound_handling_cost, 0) + coalesce(i.inbound_handling_cost, 0) as total_handling_pool

from direct_costs d
full outer join inbound_costs i
    on d.facility_id = i.facility_id and d.product_id = i.product_id
full outer join outbound_sales_costs o
    on coalesce(d.facility_id, i.facility_id) = o.facility_id
    and coalesce(d.product_id, i.product_id) = o.product_id