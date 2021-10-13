
WITH cte_1
     AS (SELECT asset.asset_id,
                asset.adaccount_id,
                asset.asset_name,
                asset.asset_type,
                adaccount.optimization_metric,
                Cast(adaccount.targets AS JSONB) ->> 'd7_roas' AS target_d7roas,
                Cast(adaccount.targets AS JSONB) ->> 'cpi'     AS target_cpi,
                Cast(adaccount.targets AS JSONB) ->> 'cpm'     AS target_cpa
         FROM   fb_app_assets asset
                left join fb_app_adaccounts adaccount
                       ON asset.adaccount_id = adaccount.adaccount_id
         WHERE  asset.adaccount_id = 'act_318549416033487'
                AND asset_name NOT IN(SELECT asset_name
                                      FROM   fb_app_assets
                                      WHERE
                    adaccount_id = 'act_439286853957566')),
     cte_2
     AS (SELECT adaccount_id,
                entity_id,
                ( SUM(blk_d7_purchase_value) / Nullif(SUM(blk_spend), 0) ) AS
                d7_roas
                ,
                ( SUM(blk_spend) / Nullif(SUM(blk_installs), 0) )
                AS cpi,
                ( SUM(blk_spend) / Nullif(SUM(blk_unique_purchases), 0) )  AS
                cpa
         FROM  (SELECT blk.adaccount_id,
                       blk.entity_id,
                       Cast(blk.metadata ->> 'd7_purchase_value' AS FLOAT) AS
                              blk_d7_purchase_value,
                       Cast(blk.metadata ->> 'spend' AS FLOAT)             AS
                       blk_spend,
                       Cast(metadata ->> 'installs' AS FLOAT)              AS
                       blk_installs,
                       Cast(metadata ->> 'unique_purchases' AS FLOAT)      AS
                              blk_unique_purchases
                FROM   blkbox_performance_history AS blk
                WHERE  blk.adaccount_id = 'act_318549416033487') t
         GROUP  BY 1,
                   2)
SELECT *
FROM  (SELECT c1.asset_id,
              c1.asset_name,
              c1.asset_type,
              c1.target_d7roas,
              c2.d7_roas,
              CASE
                WHEN ( c1.optimization_metric = 'd7_roas' )
                     AND ( c1.target_d7roas :: NUMERIC ) < (
                         c2.d7_roas :: NUMERIC )
                    THEN
                'above'
                WHEN ( c1.optimization_metric = 'cpi' )
                     AND ( c1.target_cpi :: NUMERIC ) > ( c2.cpi :: NUMERIC )
              THEN
                'above'
                WHEN ( c1.optimization_metric = 'cpa' )
                     AND ( c1.target_cpa :: NUMERIC ) > ( c2.cpa :: NUMERIC )
              THEN
                'above'
                ELSE 'below'
              END AS goal
       FROM   cte_1 c1
              inner join cte_2 c2
                      ON c1.adaccount_id = c2.adaccount_id
                         AND c1.asset_id = c2.entity_id)p
WHERE  goal = 'above';
