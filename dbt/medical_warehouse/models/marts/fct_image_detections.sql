{{ config(materialized='table') }}

with detections as (

    select *
    from {{ ref('stg_yolo_image_detections') }}

),

-- Aggregate detections per image
image_flags as (

    select
        message_id,

        max(case when detected_class = 'person' then 1 else 0 end) as has_person,

        max(
            case
                when detected_class in (
                    'bottle', 'container', 'box', 'package', 'product'
                )
                then 1 else 0
            end
        ) as has_product

    from detections
    group by message_id
),

classified_images as (

    select
        message_id,

        case
            when has_person = 1 and has_product = 1 then 'promotional'
            when has_person = 0 and has_product = 1 then 'product_display'
            when has_person = 1 and has_product = 0 then 'lifestyle'
            else 'other'
        end as image_category

    from image_flags
),

messages as (

    select
        message_id,
        channel_key,
        date_key
    from {{ ref('fct_messages') }}

)

select
    d.message_id,
    m.channel_key,
    m.date_key,

    d.detected_class,
    d.confidence_score,

    c.image_category

from detections d
join classified_images c
    on d.message_id = c.message_id
join messages m
    on d.message_id = m.message_id
