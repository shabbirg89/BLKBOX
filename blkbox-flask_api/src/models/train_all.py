
from flask import Blueprint, request
from tensorflow.keras.applications import vgg16,vgg19,DenseNet201
from tensorflow.keras.models import Model
import os
import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing.image import load_img,img_to_array
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.applications import vgg16,vgg19,DenseNet201
import pickle,json
from sklearn.metrics.pairwise import cosine_similarity

all_ad_accounts = ['act_935194900267864',
 'act_2372326503071179',
 'act_941836912949189',
 'act_1358560517596540',
 'act_2910534345682289',
 'act_547511135952669',
 'act_1318123415187226',
 'act_125428025564921',
 'act_439286853957566',
 'act_2760812104166973',
 'act_530803134133407',
 'act_1252889871474229',
 'act_263840598323834',
 'act_2991319124266485',
 'act_4504208456312407',
 'act_3341820239242446',
 'act_2763692333854176',
 'act_328569521024018',
 'act_313474253188474',
 'act_1195641163801544',
 'act_300588617701811',
 'act_748215912282143',
 'act_260482525612406',
 'act_577533042923514',
 'act_393145255464655',
 'act_279325857166314',
 'act_187910286561764',
 'act_902918343836274',
 'act_1929386790698216',
 'act_251797882519603']



AllTrain = Blueprint(name='train_all', import_name=__name__)

@AllTrain.route('/train_all_accounts')#,methods=['POST'])
def all_train():
	# all_ad_accounts
	for ad_acc in all_ad_accounts:

		imgs_path = '/home/jignesh/blkbox/blkbox-ml-master/Single_ad_acc_images/{a}/'.format(a=ad_acc)
		target_path = "/home/jignesh/blkbox/blkbox-ml-master/test_images/"

		imgs_model_width, imgs_model_height = 224, 224
		nb_closest_images = 5 # number of most similar images to retrieve


		# Model
		
		dense_model = DenseNet201(weights='imagenet')
		# remove the last layers in order to get features instead of predictions
		feat_extractor = Model(inputs=dense_model.input, outputs=dense_model.get_layer("avg_pool").output)

		train_files = [imgs_path + x for x in os.listdir(imgs_path) if ".png" in x]
		
		test_files = [target_path + x for x in os.listdir(target_path) if "png" in x]
		
		def feat_extract(files):
			
			out_files = []
			counter = 0
			importedImages = []
			for f in files:
				
				try:
					
					original = load_img(f, target_size =(imgs_model_width,imgs_model_height))
					out_files.append(f)
					numpy_image = img_to_array(original)
					image_batch = np.expand_dims(numpy_image, axis=0)
					importedImages.append(image_batch)
					counter +=1
					pass
				except:
					continue
		
			images = np.vstack(importedImages)
			
			processed_imgs = preprocess_input(images.copy())


			imgs_features = feat_extractor.predict(processed_imgs)
			
			return imgs_features, out_files

		imgs_features_train, files_train = feat_extract(train_files)
		imgs_features_test, files_test = feat_extract(test_files)

		

		# Save files
		path = "/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}".format(a=ad_acc)
		if not os.path.isdir(path):
			os.mkdir(path)
				
	

		np.save("/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}/{a}".format(a = ad_acc), imgs_features_train)

		with open("/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}/{a}.txt".format(a = ad_acc),"wb") as fp:
		    pickle.dump(files_train, fp)

		arr = np.concatenate((imgs_features_train, imgs_features_test), axis=0)

		files_all = files_train + files_test

		cosSimilarities = cosine_similarity(arr)

		cos_similarities_df = pd.DataFrame(cosSimilarities, columns=files_all, index=files_all)
		#cos_similarities_df.to_csv('{}.csv'.format(ad_acc))
		cos_similarities_df.to_csv('/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}/{a}.csv'.format(a=ad_acc))




	return {"val":"Success"}



@AllTrain.route('/train_selective',methods=['POST'])
def train():
	data = request.get_json()
	
	li = data['acc']
	
	for ad_acc in li:
		

		imgs_path = '/home/jignesh/blkbox/blkbox-ml-master/Single_ad_acc_images/{a}/'.format(a=ad_acc)
		target_path = "/home/jignesh/blkbox/blkbox-ml-master/test_images/"

		imgs_model_width, imgs_model_height = 224, 224
		nb_closest_images = 5 # number of most similar images to retrieve


		# Model
		
		dense_model = DenseNet201(weights='imagenet')
		# remove the last layers in order to get features instead of predictions
		feat_extractor = Model(inputs=dense_model.input, outputs=dense_model.get_layer("avg_pool").output)

		train_files = [imgs_path + x for x in os.listdir(imgs_path) if ".png" in x]
		
		test_files = [target_path + x for x in os.listdir(target_path) if "png" in x]
		
		def feat_extract(files):
			
			out_files = []
			counter = 0
			importedImages = []
			for f in files:
				
				try:
					
					original = load_img(f, target_size =(imgs_model_width,imgs_model_height))
					out_files.append(f)
					numpy_image = img_to_array(original)
					image_batch = np.expand_dims(numpy_image, axis=0)
					importedImages.append(image_batch)
					counter +=1
					pass
				except:
					continue
		
			images = np.vstack(importedImages)
			
			processed_imgs = preprocess_input(images.copy())


			imgs_features = feat_extractor.predict(processed_imgs)
			
			return imgs_features, out_files

		imgs_features_train, files_train = feat_extract(train_files)
		imgs_features_test, files_test = feat_extract(test_files)

		

		# Save files
		path = "/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}".format(a=ad_acc)
		if not os.path.isdir(path):
			os.mkdir(path)
				
	

		np.save("/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}/{a}".format(a = ad_acc), imgs_features_train)

		with open("/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}/{a}.txt".format(a = ad_acc),"wb") as fp:
		    pickle.dump(files_train, fp)

		arr = np.concatenate((imgs_features_train, imgs_features_test), axis=0)

		files_all = files_train + files_test

		cosSimilarities = cosine_similarity(arr)

		cos_similarities_df = pd.DataFrame(cosSimilarities, columns=files_all, index=files_all)
		#cos_similarities_df.to_csv('{}.csv'.format(ad_acc))
		cos_similarities_df.to_csv('/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}/{a}.csv'.format(a=ad_acc))




	return {"val":"Success"}