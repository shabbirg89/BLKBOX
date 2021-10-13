
select adaccount_id,campaign_name,sum(spend) from (
select campaign.campaign_id,campaign.adaccount_id,campaign_name,cast(blk.metadata ->>'spend' as FLOAT) as spend,
adaccount.optimization_metric,cast(adaccount.targets as jsonb)->>'d7_roas' as target_d7_roas
from fb_app_campaigns campaign inner join fb_app_adaccounts adaccount on 
campaign.adaccount_id=adaccount.adaccount_id inner join  blkbox_performance_history blk on 
blk.adaccount_id=campaign.adaccount_id and blk.entity_id=campaign.campaign_id  where campaign_name like '%\_AC\_%' or campaign_name like '%\_AC'
)t  group by 1,2;
