select
    ProductID       as product_id,
    ProductName     as product_name,
    Category        as category,
    KGPerPallet     as kg_per_pallet,
    SalesUnit       as sales_unit,
    KGPerSalesUnit  as kg_per_sales_unit,
    Price           as price,
    COGS            as cogs,
    ShelfLife       as shelf_life
from {{ source('raw_supply_chain', 'product_master') }}