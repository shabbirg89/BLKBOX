
SELECT adaccount_id,
mon,
yyyy,
( SUM(spend) / Nullif(SUM(installs), 0) ) AS cpi,
( SUM(spend) / Nullif(SUM(unique_purchases), 0) ) AS cpa,
( SUM(d0_purchase_value) / Nullif(SUM(spend), 0) ) AS d0_roas,
( SUM(d7_purchase_value) / Nullif(SUM(spend), 0) ) AS d7_roas,
( 1000 * SUM(spend) / Nullif(SUM(impressions), 0) ) AS cpm,
SUM(spend) AS spend
FROM (SELECT adset.adaccount_id,
adset.adset_id,
adset.adset_name,
blk.DATE,
To_char(blk.DATE, 'Mon') AS mon,
Extract(year FROM blk.DATE) AS yyyy,
Cast(blk.metadata ->> 'spend' AS FLOAT) AS spend,
Cast(blk.metadata ->> 'installs' AS FLOAT) AS installs,
Cast(blk.metadata ->> 'd7_purchase_value' AS FLOAT) AS
d7_purchase_value
,
Cast(blk.metadata ->> 'd0_purchase_value' AS FLOAT) AS
d0_purchase_value,
Cast(blk.metadata ->> 'unique_purchases' AS FLOAT) AS
unique_purchases,
Cast(blk.metadata ->> 'impressions' AS FLOAT) AS impressions
FROM fb_app_adsets adset
inner join blkbox_performance_history blk
ON adset.adaccount_id = blk.adaccount_id
AND adset.adset_id = blk.entity_id
WHERE adset.adset_name ~~ '%ADSET%'
ORDER BY adaccount_id)t
GROUP BY 1,
2,
3;
