select
    OriginID             as origin_id,
    OriginCity           as origin_city,
    OriginCountry        as origin_country,
    DestinationID        as destination_id,
    DestinationCity      as destination_city,
    DestinationCountry   as destination_country,
    DistanceKM           as distance_km,
    CostPerPallet        as cost_per_pallet,
    RouteType            as route_type
from {{ source('raw_supply_chain', 'transport_ratecard') }}