select
    Date             as inventory_date,
    FacilityID       as facility_id,
    ProductID        as product_id,
    VolumeInPallet   as volume_in_pallet
from {{ source('raw_supply_chain', 'inventory') }}