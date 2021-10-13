
WITH cte_1
AS (SELECT adaccount_id,
entity_id,
order_date,
operation,
min_roas
FROM (SELECT adaccount_id,
entity_id,
operation,
Cast(fb_log.metadata AS JSONB) ->> 'Min ROAS'
AS
Min_Roas,
Generate_series(Min(fb_log.DATE), Max(fb_log.DATE), '1d') :: DATE AS
order_date
FROM blkbox_fb_changelog fb_log
GROUP BY entity_id,
adaccount_id,
operation,
Cast(fb_log.metadata AS JSONB) ->> 'Min ROAS')t
WHERE operation = 'UPDATE_MIN_ROAS'),
cte_2
AS (SELECT blk_ph.entity_id AS blk_entity_id,
blk_ph.DATE AS blk_date,
Cast(blk_ph.metadata AS JSONB) ->> 'cpa' AS cpa,
Cast(blk_ph.metadata AS JSONB) ->> 'cpm' AS cpm,
Cast(blk_ph.metadata AS JSONB) ->> 'cpi' AS cpi
FROM blkbox_performance_history blk_ph)
SELECT *
FROM cte_1 c1
inner join cte_2 c2
ON c1.entity_id = c2.blk_entity_id
AND c1.order_date = c2.blk_date;