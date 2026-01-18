select
    message_id,
    message_date
from {{ ref('stg_telegram_messages') }}
where message_date > now()
