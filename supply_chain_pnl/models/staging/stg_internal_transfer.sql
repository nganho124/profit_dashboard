select
    TransferID              as transfer_id,
    Date                     as transfer_date,
    OriginFacilityID         as origin_facility_id,
    DestinationFacilityID    as destination_facility_id,
    ProductID                as product_id,
    TransferPallets          as transfer_pallets,
from {{ source('raw_supply_chain', 'internal_transfer') }}