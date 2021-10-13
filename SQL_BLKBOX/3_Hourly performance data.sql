
SELECT id,
adaccount_id,
entity_id,
hourly_breakdown,
KEY AS hour,
Cast(value AS JSONB)->>'spend' AS spend,
Cast(value AS JSONB)->>'installs' AS installs,
Sum(NULLIF(value->>'spend', ''):: numeric) OVER (partition BY KEY) AS spend_sum,
Sum(NULLIF(value->>'installs', '')::numeric) OVER (partition BY KEY) AS install_sum,
Round(COALESCE(Sum(NULLIF(value->>'spend', '')::numeric) OVER (partition BY KEY) / NULLIF(Sum(NULLIF(value->>'installs', '')::numeric) OVER (partition BY KEY),0), 0),3) AS cpi,
Cast(value AS JSONB)->>'d1_purchase_value' AS d1_purchase_val,
Cast(value AS JSONB)->>'d7_purchase_value' AS d7_purchase_val,
Sum(NULLIF(value->>'d1_purchase_value', '')::numeric) OVER (partition BY KEY) AS d1_purchase_val_sum,
Sum(NULLIF(value->>'d7_purchase_value', '')::numeric) OVER (partition BY KEY) AS d7_purchase_val_sum,
Round(COALESCE(Sum(NULLIF(value->>'d1_purchase_value', '')::numeric) OVER (partition BY KEY) / NULLIF(Sum(NULLIF(value->>'spend', '')::numeric) OVER (partition BY KEY),0), 0),3) AS d1_roas,
Round(COALESCE(Sum(NULLIF(value->>'d7_purchase_value', '')::numeric) OVER (partition BY KEY) / NULLIF(Sum(NULLIF(value->>'spend', '')::numeric) OVER (partition BY KEY),0), 0),3) AS d7_roas,
Cast(value AS JSONB)->>'unique_purchases' AS unique_purchases,
Sum(NULLIF(value->>'unique_purchases', '')::numeric) OVER (partition BY KEY) AS unique_purchases_sum,
Round(COALESCE(Sum(NULLIF(value->>'unique_purchases', '')::numeric) OVER (partition BY KEY) / NULLIF(Sum(NULLIF(value->>'spend', '')::numeric) OVER (partition BY KEY),0), 0),3) AS cpa,
Row_number() OVER ( partition BY entity_id ORDER BY entity_id,KEY )
FROM (
SELECT id,
adaccount_id,
entity_id,
hourly_breakdown,
date,
(Jsonb_each(hourly_breakdown)).* AS hour_info
FROM blkbox_performance_breakdowns) t
WHERE adaccount_id='act_1007332209799361';