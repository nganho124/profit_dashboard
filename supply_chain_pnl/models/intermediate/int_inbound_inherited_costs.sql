with transfers as (
    select * from {{ ref('int_transfer_costs') }}
),
outbound as (
    select * from {{ ref('int_outbound_totals') }}
),

with_alloc_ratio as (
    select
        t.*,
        o.storage_cost_fac_prod,
        o.overhead_cost_fac_prod,
        o.ioc_fac_prod,
        coalesce(safe_divide(t.transfer_volume_kg, o.total_outbound_volume_kg), 0) as sto_alloc_ratio
    from transfers t
    left join outbound o
        on t.origin_facility_id = o.facility_id
        and t.product_id = o.product_id
),

allocated as (
    select
        *,
        storage_cost_fac_prod * sto_alloc_ratio as sto_storage_cost,
        overhead_cost_fac_prod * sto_alloc_ratio as sto_overhead_cost,
        ioc_fac_prod * sto_alloc_ratio as sto_ioc
    from with_alloc_ratio
)

select
    destination_facility_id as facility_id,
    product_id,
    sum(transfer_transport_cost) as inbound_transport_cost,
    sum(transfer_handling_cost) as inbound_handling_cost,
    sum(sto_storage_cost) as inbound_storage_cost,
    sum(sto_overhead_cost) as inbound_overhead_cost,
    sum(sto_ioc) as inbound_ioc
from allocated
group by destination_facility_id, product_id