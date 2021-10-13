
SELECT
operation,
(CAST(trigger_date AS date) - CAST(created_at AS date)) as days_since_creation,
( Sum(d7_purchase_value) / NULLIF(Sum(spend), 0) ) AS d7_roas,
( Sum(spend) / NULLIF(Sum(installs), 0) ) AS cpi,
( Sum(spend) / NULLIF(Sum(unique_purchases), 0) ) AS cpa,
Sum(spend) AS spend
FROM (SELECT log.adaccount_id,
log.entity_id,
log.entity_type,
log.operation,
log.date AS
trigger_date,
adset.created_at,
blk.date AS blk_date,
Cast(blk.metadata ->> 'd7_purchase_value' AS FLOAT) AS
d7_purchase_value
,
Cast(blk.metadata ->> 'installs' AS FLOAT) AS
installs,
Cast(blk.metadata ->> 'spend' AS FLOAT) AS spend,
Cast(blk.metadata ->> 'unique_purchases' AS FLOAT) AS
unique_purchases
FROM blkbox_fb_changelog log
inner join fb_app_adsets adset on adset.adaccount_id=log.adaccount_id and
adset.adset_id=log.entity_id
INNER JOIN blkbox_performance_history blk
ON log.adaccount_id = blk.adaccount_id
AND log.entity_id = blk.entity_id
AND log.entity_type = 'ADSET'
AND ( ( blk.date = log.date - 1 )
OR ( blk.date = log.date )
OR ( blk.date = log.date + 1 ) ))t
GROUP BY 1,
2

