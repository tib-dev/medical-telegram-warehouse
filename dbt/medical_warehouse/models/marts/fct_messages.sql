select
    m.message_id,
    c.channel_key,
    d.date_key,
    m.message_text,
    m.message_length,
    m.view_count,
    m.forward_count,
    m.has_image
from {{ ref('stg_telegram_messages') }} m
join {{ ref('dim_channels') }} c
    on m.channel_name = c.channel_name
join {{ ref('dim_dates') }} d
    on m.message_date::date = d.full_date
