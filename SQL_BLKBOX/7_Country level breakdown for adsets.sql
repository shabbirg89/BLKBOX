

 SELECT adaccount_id,
       adaccount_name,
       optimization_metric,
       region,
       optimization,
       goal,
       ( SUM(spend) / Nullif(SUM(installs), 0) )          AS cpi,
       ( SUM(spend) / Nullif(SUM(unique_purchases), 0) )  AS cpa,
       ( SUM(d7_purchase_value) / Nullif(SUM(spend), 0) ) AS d7_roas,
       SUM(spend)                                         AS spend
FROM   (SELECT fb_adaccount.adaccount_id,
               fb_adaccount.adaccount_name,
               fb_adaccount.optimization_metric,
               fb_campaigns.targeting                            AS region,
               fb_campaigns.optimization                         AS optimization
               ,
               CASE
                 WHEN ( fb_adaccount.optimization_metric = 'd7_roas' )
                      AND ( ( fb_adaccount.targets ->> 'd7_roas' ) :: NUMERIC )
                          < (
                          ( blk_per.d7_roas ) :: NUMERIC ) THEN 'above'
                 WHEN ( fb_adaccount.optimization_metric = 'cpi' )
                      AND ( ( fb_adaccount.targets ->> 'cpi' ) :: NUMERIC ) >
                          ( ( blk_per.cpi ) :: NUMERIC ) THEN 'above'
                 WHEN ( fb_adaccount.optimization_metric = 'cpa' )
                      AND ( ( fb_adaccount.targets ->> 'cpa' ) :: NUMERIC ) >
                          ( ( blk_per.cpa ) :: NUMERIC ) THEN 'above'
                 ELSE 'below'
               END                                               AS goal,
               Cast(fb_adaccount.targets AS JSONB) ->> 'cpa'     AS target_cpa,
               Cast(fb_adaccount.targets AS JSONB) ->> 'cpi'     AS target_cpi,
               Cast(fb_adaccount.targets AS JSONB) ->> 'd7_roas' AS
               target_d7_roas,
               cpa,
               cpi,
               d7_roas,
               d7_purchase_value,
               spend,
               installs,
               unique_purchases,
               blk_per.DATE
        FROM   fb_app_adsets fb_adset
               inner join fb_app_adaccounts fb_adaccount
                       ON fb_adset.adaccount_id = fb_adaccount.adaccount_id
               inner join fb_app_campaigns AS fb_campaigns
                       ON fb_adset.campaign_id = fb_campaigns.campaign_id
               inner join (SELECT adaccount_id,
                                  entity_id,
                                  DATE,
                                  Cast(metadata ->> 'cpa' AS FLOAT)
                                  AS
                                  cpa,
                                  Cast(metadata ->> 'cpi' AS FLOAT)
                                  AS
                                  cpi,
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
GROUP  BY 1,
          2,
          3,
          4,
          5,
          6; 

