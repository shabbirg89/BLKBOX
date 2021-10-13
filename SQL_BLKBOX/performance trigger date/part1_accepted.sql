
with cte1 as(
SELECT entity_id,
operation,
trigger_date,
blk_date,
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
INNER JOIN blkbox_performance_history blk
ON log.adaccount_id = blk.adaccount_id
AND log.entity_id = blk.entity_id
AND log.entity_type = 'ADSET'
AND ( blk.date = log.date - 1 ))t
GROUP BY 1,
2,
3,
4
ORDER BY entity_id
),
cte2 as(
	
SELECT entity_id,
operation,
trigger_date,
blk_date,
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
INNER JOIN blkbox_performance_history blk
ON log.adaccount_id = blk.adaccount_id
AND log.entity_id = blk.entity_id
AND log.entity_type = 'ADSET'
AND ( blk.date = log.date))t
GROUP BY 1,
2,
3,
4
ORDER BY entity_id
),
cte3 as(
SELECT entity_id,
operation,
trigger_date,
blk_date,
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
INNER JOIN blkbox_performance_history blk
ON log.adaccount_id = blk.adaccount_id
AND log.entity_id = blk.entity_id
AND log.entity_type = 'ADSET'
AND ( blk.date = log.date + 1 ) )t
GROUP BY 1,
2,
3,
4
ORDER BY entity_id
)
select cte1.entity_id,cte1.operation,cte1.trigger_date,cte1.blk_date,cte2.blk_date,cte3.blk_date,cte1.d7_roas as previous,cte2.d7_roas as same,cte3.d7_roas as next
from cte1 inner join cte2 on cte1.entity_id=cte2.entity_id and cte1.trigger_date=cte2.trigger_date inner join cte3 on cte1.entity_id=cte3.entity_id  and cte1.trigger_date=cte3.trigger_date order by cte1.entity_id;

