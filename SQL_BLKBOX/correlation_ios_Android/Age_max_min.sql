	
SELECT 
		date_trunc('month',datee) as datee,
		app_id,
       adaccount_id,
       adaccount_name,
       platform,

	   age_max,
	   age_min,
	  
       ( Sum(spend) / NULLIF(Sum(installs), 0) )          AS cpi,
       ( Sum(spend) / NULLIF(Sum(unique_purchases), 0) )  AS cpa,
       ( Sum(d0_purchase_value) / NULLIF(Sum(spend), 0) ) AS d0_roas,
       ( Sum(d7_purchase_value) / NULLIF(Sum(spend), 0) ) AS d7_roas,
       ( 1000 * Sum(spend) / nullif(Sum(impressions),0 ))           AS cpm,
       Sum(spend)                                         AS spend,
       Sum(impressions)                                   AS impressions,
	   sum(d0_purchase_value)                                   AS d0_purchase,
	   sum(d7_purchase_value)                                   AS d7_purchase,
	   sum(unique_purchases)                                    AS unique_purchases
FROM   (SELECT fb_adaccount.app_id,
               fb_adaccount.adaccount_id,
               fb_adaccount.adaccount_name,
               fb_adaccount.platform,
               fb_campaigns.targeting                                      AS
               region,
               fb_campaigns.optimization                                   AS
                      optimization,
               Cast(fb_adset.targeting AS JSONB) ->> 'publisher_platforms' AS
                      publish_platforms,
               Cast(fb_adset.targeting AS JSONB) ->> 'genders'             AS
               genders,
               Cast(fb_adset.targeting AS JSONB) ->> 'age_max'             AS
               age_max,
               Cast(fb_adset.targeting AS JSONB) ->> 'age_min'             AS
               age_min,
               cpa,
               cpi,
               d7_roas,
               d7_purchase_value,
               spend,
               installs,
               unique_purchases,
               blk_per.date                                                AS
               datee,
               impressions,
               d0_purchase_value
        FROM   fb_app_adsets fb_adset
               INNER JOIN fb_app_adaccounts fb_adaccount
                       ON fb_adset.adaccount_id = fb_adaccount.adaccount_id
               INNER JOIN fb_app_campaigns AS fb_campaigns
                       ON fb_adset.campaign_id = fb_campaigns.campaign_id
               INNER JOIN (SELECT adaccount_id,
                                  entity_id,
                                  date,
                                  Cast(metadata ->> 'cpa' AS FLOAT)
                                  AS
                                  cpa,
                                  Cast(metadata ->> 'impressions' AS FLOAT)
                                  AS
               impressions,
                                  Cast(metadata ->> 'cpi' AS FLOAT)
                                  AS
                                  cpi,
                                  Cast(metadata ->> 'd0_purchase_value' AS FLOAT
                                  ) AS
               d0_purchase_value,
                                  Cast(metadata ->> 'd7_roas' AS FLOAT)
                                  AS
                                  d7_roas,
                                  Cast(metadata ->> 'd7_purchase_value' AS FLOAT
                                  ) AS
               d7_purchase_value,
                                  Cast(metadata ->> 'spend' AS FLOAT)
                                  AS
                                  spend,
                                  Cast(metadata ->> 'installs' AS FLOAT)
                                  AS
                                  installs,
                                  Cast(metadata ->> 'unique_purchases' AS FLOAT)
                                  AS
               unique_purchases
                           FROM   blkbox_performance_history) AS blk_per
                       ON blk_per.adaccount_id = fb_adset.adaccount_id
                          AND blk_per.entity_id = fb_adset.adset_id) AS info
GROUP by date_trunc('month',datee),
		  1,
          2,
          3,
          4,
          5,6,7 order by app_id;