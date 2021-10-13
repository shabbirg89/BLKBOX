
select adaccount_id,campaign_name,(SUM(blk_d7_purchase_value) / Nullif(SUM(blk_spend), 0) ) AS blkbox_d7_roas from (
select campaign.campaign_id,campaign.adaccount_id,campaign_name,cast(blk.metadata ->>'spend' as FLOAT) as blk_spend,
adaccount.optimization_metric,cast(adaccount.targets->>'d7_roas' as FLOAT) as target_d7_roas,cast(blk.metadata->>'d7_purchase_value' as FLOAT) as blk_d7_purchase_value
from fb_app_campaigns campaign inner join fb_app_adaccounts adaccount on 
campaign.adaccount_id=adaccount.adaccount_id inner join  blkbox_performance_history blk on 
blk.adaccount_id=campaign.adaccount_id and blk.entity_id=campaign.campaign_id  where campaign_name like '%\_AC\_%' or campaign_name like '%\_AC' order by campaign.adaccount_id
)g group by 1,2;
