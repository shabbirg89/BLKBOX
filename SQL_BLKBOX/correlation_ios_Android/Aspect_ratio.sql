
SELECT app_id,
       adaccount_id,
       asset_id,
       platform,
       asset_type,
       aspect_ratio,
       ( Sum(spend) / NULLIF(Sum(installs), 0) )           AS cpi,
       ( Sum(spend) / NULLIF(Sum(unique_purchases), 0) )   AS cpa,
       ( Sum(d0_purchase_value) / NULLIF(Sum(spend), 0) )  AS d0_roas,
       ( Sum(d7_purchase_value) / NULLIF(Sum(spend), 0) )  AS d7_roas,
       ( 1000 * Sum(spend) / NULLIF(Sum(impressions), 0) ) AS cpm,
       Sum(spend)                                          AS spend,
       Sum(impressions)                                    AS impressions
FROM   (SELECT asset.app_id,
               asset.adaccount_id,
               asset.asset_name,
               asset.asset_id,
			   asset.asset_type,
               asset.platform,
               asset.aspect_ratio,
               cpa,
               cpi,
               d7_roas,
               d7_purchase_value,
               spend,
               installs,
               unique_purchases,
               blk_per.date AS datee,
               impressions,
               d0_purchase_value
        FROM   fb_app_assets asset
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
                       ON blk_per.adaccount_id = asset.adaccount_id
                          AND blk_per.entity_id = asset.asset_id) t
GROUP  BY 1,
          2,
          3,
          4,
          5,6;
