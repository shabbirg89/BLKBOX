SELECT *
FROM (SELECT fb_app_adaccounts.adaccount_name,
fb_campaign.adaccount_id,
blk_ph.entity_id,
blk_ph.date,
blk_ph.metadata ->> 'cpi' AS cpi,
blk_ph.metadata ->> 'cpm' AS cpm,
blk_ph.metadata ->> 'cpa' AS cpa,
blk_ph.metadata ->> 'impressions' AS impressions,
blk_ph.metadata ->> 'installs' AS installs,
blk_ph.metadata ->> 'd7_purchase_value' AS d7_purchase_value,
blk_ph.metadata ->> 'spend' AS spend,
Row_number()
OVER(
partition BY blk_ph.entity_id
ORDER BY blk_ph.date) day_of_campaign
FROM blkbox_performance_history blk_ph
INNER JOIN fb_app_campaigns fb_campaign
ON blk_ph.entity_id = fb_campaign.campaign_id
INNER JOIN fb_app_adaccounts
ON fb_campaign.adaccount_id =
fb_app_adaccounts.adaccount_id) t
WHERE day_of_campaign <= 3;
