select
    FacilityID              as facility_id,
    FacilityName            as facility_name,
    FacilityType            as facility_type,
    OriginCity               as origin_city,
    Country                  as country,
    Latitude                 as latitude,
    Longitude                as longitude,
    CapacityInPallet         as capacity_in_pallet,
    AnnualStorageCost        as annual_storage_cost,
    HandlingCostPerPallet    as handling_cost_per_pallet,
    TotalOverheadCost        as total_overhead_cost
from {{ source('raw_supply_chain', 'facility_master') }}