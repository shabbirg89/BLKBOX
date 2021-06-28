1. Train a single ad_account : 
  url : /api/v1/similar_imgs/train
  data : {"acc": "act_439286853957566" }
  
2.  Test a single image for ad_account:
     url : /api/v1/similar_imgs/test/
     data : {"img": "/home/jignesh/blkbox/project_image/test/act_439286853957566-8a9610b7fcbd11fc40f4553d9b02fbe8_28.png"}
     
3. Train specific ad_accounts :
    url :  /api/v1/specific/train_selective
    data : {"acc": ["act_187910286561764",
                    "act_216584173102613",
                    "act_300588617701811"]}
                    
4. Train all ad_accounts : 
    url : /api/v1/specific/train_all_accounts
   > hit the url all the accounts will start training

5. Train All Ad_accounts images : 
    url : /api/v1/all/all_images
   > hit the url all images will start training and saved as unique file, csv

6. Test Image from all_images
    url : /api/v1/all/test_all_images
    data : {"img": "/home/jignesh/blkbox/project_image/test/act_439286853957566-8a9610b7fcbd11fc40f4553d9b02fbe8_28.png"}
