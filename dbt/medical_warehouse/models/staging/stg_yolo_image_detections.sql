{{ config(materialized='view') }}

select
    cast(message_id as bigint) as message_id,
    lower(detected_class) as detected_class,
    cast(confidence_score as numeric(5,4)) as confidence_score
from {{ source('raw', 'yolo_image_detections') }}
