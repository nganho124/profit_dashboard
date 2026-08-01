select
    OrderID          as order_id,
    FacilityID       as facility_id,
    ShipToID         as ship_to_id,
    Date             as order_date,
    SalesVolume      as sales_volume,
    ProductID        as product_id,
    ShipToCountry    as ship_to_country,
    ActualPrice      as actual_price
from {{ source('raw_supply_chain', 'sales_orders') }}