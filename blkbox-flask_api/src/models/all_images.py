
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


imgs_model_width, imgs_model_height = 224, 224
nb_closest_images = 5 # number of most similar images to retrieve



AllImages = Blueprint(name='train_selective1', import_name=__name__)

@AllImages.route('/all_images',methods=['GET'])
def train_all_images():
	ad_acc = 'All_image'
	imgs_path = '/home/jignesh/blkbox/blkbox-ml-master/All_image/'
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


@AllImages.route('/test_all_images',methods=['GET'])
def test_all():
    data = request.get_json()
    given_img = data['img']
 
    ad_acc = 'All_image'


   

    if os.path.isdir('/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}'.format(a=ad_acc)):
        cos_similarities_df = pd.read_csv('/home/jignesh/blkbox/blkbox-ml-master/training_data_storage/{a}/{a}.csv'.format(a=ad_acc))
    else:
        return {"val": "NO trained data found for this ad_acc : {}".format(ad_acc)}
   
    cos_similarities_df.set_index('Unnamed: 0',inplace=True)

    
    closest_imgs = cos_similarities_df[given_img].sort_values(ascending=False)[1:nb_closest_images+1].index
    closest_imgs_scores = cos_similarities_df[given_img].sort_values(ascending=False)[1:nb_closest_images+1]
  
    return {"Similar Images": list(closest_imgs),"scores":list(closest_imgs_scores)}
