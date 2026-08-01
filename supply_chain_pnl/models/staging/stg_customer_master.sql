select
    ShipToID        as ship_to_id,
    ShipToParty     as ship_to_party,
    Account         as account,
    Channel         as channel,
    Address         as address,
    City            as city,
    ShipToCountry   as ship_to_country,
    Continent       as continent,
    Latitude        as latitude,
    Longitude       as longitude
from {{ source('raw_supply_chain', 'customer_master') }}