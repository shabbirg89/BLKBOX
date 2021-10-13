
SELECT adaccount_id,
       campaign_name,
       target_d7_roas,
       CASE
         WHEN ( target_d7_roas :: NUMERIC ) < ((
              SUM(blk_d7_purchase_value) /
              Nullif(SUM(blk_spend), 0) :: NUMERIC )
                                              ) THEN'above'
         ELSE 'below'
       END                                                        AS goal,
       ( SUM(blk_d7_purchase_value) / Nullif(SUM(blk_spend), 0) ) AS
       blkbox_d7_roas
FROM   (SELECT campaign.campaign_id,
               campaign.adaccount_id,
               campaign_name,
               Cast(blk.metadata ->> 'spend' AS FLOAT)             AS blk_spend,
               adaccount.optimization_metric,
               Cast(adaccount.targets ->> 'd7_roas' AS FLOAT)      AS
               target_d7_roas,
               Cast(blk.metadata ->> 'd7_purchase_value' AS FLOAT) AS
                      blk_d7_purchase_value
        FROM   fb_app_campaigns campaign
               inner join fb_app_adaccounts adaccount
                       ON campaign.adaccount_id = adaccount.adaccount_id
               inner join blkbox_performance_history blk
                       ON blk.adaccount_id = campaign.adaccount_id
                          AND blk.entity_id = campaign.campaign_id
        WHERE  campaign_name LIKE '%\_AC\_%'
                OR campaign_name LIKE '%\_AC'
        ORDER  BY campaign.adaccount_id)g
GROUP  BY 1,
          2,
          3;
